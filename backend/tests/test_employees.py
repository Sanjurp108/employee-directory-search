from collections.abc import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.models.employee import Employee


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Provide a TestClient backed by an isolated in-memory SQLite database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as seed_session:
        seed_session.add_all(
            [
                Employee(
                    name="Rahul Sharma",
                    email="rahul.sharma@company.com",
                    department="Engineering",
                    designation="Senior Backend Engineer",
                    date_of_joining=date(2021, 3, 15),
                ),
                Employee(
                    name="Rahim Khan",
                    email="rahim.khan@company.com",
                    department="Engineering",
                    designation="Frontend Developer",
                    date_of_joining=date(2023, 1, 10),
                ),
                Employee(
                    name="Sneha Kulkarni",
                    email="sneha.kulkarni@company.com",
                    department="HR",
                    designation="HR Business Partner",
                    date_of_joining=date(2020, 9, 3),
                ),
                Employee(
                    name="Ananya Iyer",
                    email="ananya.iyer@company.com",
                    department="Design",
                    designation="Lead Product Designer",
                    date_of_joining=date(2021, 11, 8),
                ),
            ]
        )
        seed_session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def test_list_all_employees_paginated(test_client: TestClient) -> None:
    response = test_client.get("/employees?limit=2&offset=0")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert payload["limit"] == 2
    assert payload["offset"] == 0
    assert len(payload["items"]) == 2


def test_search_by_name_prefix_and_last_name(test_client: TestClient) -> None:
    response = test_client.get("/employees?search=Rah")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()["items"]}
    assert names == {"Rahul Sharma", "Rahim Khan"}

    last_name_res = test_client.get("/employees?search=sharma")
    assert last_name_res.status_code == 200
    assert [item["name"] for item in last_name_res.json()["items"]] == ["Rahul Sharma"]


def test_search_by_department(test_client: TestClient) -> None:
    eng_res = test_client.get("/employees?search=engineering")
    assert eng_res.status_code == 200
    assert eng_res.json()["total"] == 2

    hr_res = test_client.get("/employees?search=HR")
    assert hr_res.status_code == 200
    items = hr_res.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Sneha Kulkarni"


def test_search_no_results(test_client: TestClient) -> None:
    response = test_client.get("/employees?search=NonExistentPerson")
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == []
    assert payload["total"] == 0


def test_wildcard_characters_are_escaped(test_client: TestClient) -> None:
    response = test_client.get("/employees?search=%25")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_empty_and_whitespace_search_rejected(test_client: TestClient) -> None:
    for query in ("", "   "):
        response = test_client.get(f"/employees?search={query}")
        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "INVALID_QUERY"
        assert "empty" in body["detail"].lower()


def test_overlong_search_rejected(test_client: TestClient) -> None:
    long_query = "a" * 101
    response = test_client.get(f"/employees?search={long_query}")
    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_QUERY"


def test_invalid_query_params_return_422(test_client: TestClient) -> None:
    for params in ("limit=0", "limit=101", "limit=abc", "offset=-1"):
        response = test_client.get(f"/employees?{params}")
        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"


def test_health_check(test_client: TestClient) -> None:
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_database_failure_returns_503() -> None:
    from app.db.session import engine as real_engine

    class BrokenSession:
        def get_bind(self):
            return real_engine

        def execute(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, Exception("Connection refused"))

        def close(self) -> None:
            pass

    def override_broken_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = override_broken_db
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/employees?search=rahul")
            assert response.status_code == 503
            body = response.json()
            assert body["error_code"] == "DATABASE_UNAVAILABLE"
            assert "Connection refused" not in body["detail"]
    finally:
        app.dependency_overrides.clear()
