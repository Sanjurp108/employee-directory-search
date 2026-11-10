# Employee Directory Search System

An internal full-stack **Employee Directory Search System** built with **React + Vite** (frontend), **Python + FastAPI** (backend), and **MySQL** (database). Users can search and browse employees efficiently by `name` or `department`.

---

## Project Structure

```text
Restaverse_assignment/
├── README.md
├── .gitignore
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── schema.sql                  # Database, employees table, indexes, seed data
│   ├── app/
│   │   ├── main.py                 # FastAPI app, CORS, global error handlers, /health
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic BaseSettings loading backend/.env
│   │   │   └── exceptions.py       # Domain exceptions (mapped to HTTP errors)
│   │   ├── db/
│   │   │   └── session.py          # SQLAlchemy pooled engine & get_db() dependency
│   │   ├── models/
│   │   │   └── employee.py         # SQLAlchemy ORM model
│   │   ├── schemas/
│   │   │   └── employee.py         # Pydantic response & error contracts
│   │   ├── repositories/
│   │   │   └── employee_repo.py    # Pure SQL/ORM queries (indexed search + pagination)
│   │   ├── services/
│   │   │   └── employee_service.py # Input normalization & business rules
│   │   └── routers/
│   │       └── employees.py        # Thin HTTP route handlers
│   └── tests/
│       └── test_employees.py       # Automated API & validation test suite
└── frontend/
    ├── .env.example
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── api/employees.js        # Fetch client configured via VITE_API_BASE_URL
        ├── hooks/
        │   ├── useDebounce.js      # Delays search triggers while typing
        │   └── useEmployeeSearch.js# State, pagination & AbortController lifecycle
        ├── components/
        │   ├── SearchBar.jsx       # Controlled search input UI
        │   ├── EmployeeList.jsx    # Loading, error, empty, results & pagination UI
        │   └── EmployeeCard.jsx    # Single employee card UI
        ├── App.jsx
        └── index.css
```

---

## Setup Steps

### Prerequisites
- **MySQL Server 8.0+** (running locally)
- **Python 3.11+**
- **Node.js 20+** and **npm**

### 1. Database Setup (MySQL)
Execute [`backend/schema.sql`](backend/schema.sql) to create the `employee_directory` database, `employees` table, indexes, and 20 sample records:

```powershell
Get-Content backend\schema.sql | mysql -u root -p
```

*(Or run `SOURCE d:/Restaverse_assignment/backend/schema.sql;` inside `mysql -u root -p`.)*

### 2. Backend Setup (FastAPI)
From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set your local MySQL credentials (`DB_USER`, `DB_PASSWORD`, etc.), then start the API server:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

- API docs (Swagger UI): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

Run automated backend tests:

```powershell
.\.venv\Scripts\pytest.exe -v
```

### 3. Frontend Setup (React + Vite)
In a new terminal, from the repository root:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Database Choice & Connection Strategy

### Why MySQL?
- **Structured, relational data:** Every employee record has a fixed schema (`id`, `name`, `email`, `department`, `designation`, `date_of_joining`) where strict types (`DATE`, `VARCHAR`, `AUTO_INCREMENT` primary key) and constraints (`UNIQUE` on `email`, `NOT NULL`) prevent malformed records.
- **Native case-insensitive search & indexing:** Using `utf8mb4_unicode_ci` provides case-insensitive comparisons without wrapping indexed columns in `LOWER()` (which would disable index lookups). MySQL InnoDB also supports both **B-Tree indexes** and **`FULLTEXT` indexes** on the same table.
- **Read-heavy suitability:** Employee directories are overwhelmingly read-heavy (`SELECT` with filtering and sorting), which MySQL handles predictably with low latency.

### Why SQLAlchemy Connection Pooling (`session.py`)?
- **Scalability:** Creating a new TCP connection + MySQL authentication handshake on every API call does not scale under concurrent users. `create_engine(..., pool_size=10, max_overflow=20)` reuses persistent connections across requests.
- **Resilience:** `pool_pre_ping=True` validates pooled connections before checkout and `pool_recycle=3600` refreshes aging connections before MySQL's idle timeout closes them.
- **Fast failure & safety:** `connect_timeout=5` prevents requests from hanging if the database is unreachable, returning a clean `503 Service Unavailable` response, and `URL.create()` safely escapes special characters in credentials while ORM/bound parameters prevent SQL injection.

---

## How Search Performance Is Optimized (Conceptually)

Performance is addressed across all three layers so the system stays responsive as employee counts grow:

1. **Frontend Request Control (`useDebounce` + `AbortController`):**
   - Typing `"Rah"` rapidly does **not** fire 3 API calls (`"R"`, `"Ra"`, `"Rah"`). `useDebounce` waits `350ms` after the user pauses typing before issuing a single request, and trims whitespace first so trailing spaces don't cause duplicate calls.
   - Each request passes an `AbortSignal` from `AbortController`. If a new search or page change occurs while an older request is still in-flight, the stale request is aborted immediately—saving bandwidth and preventing out-of-order responses from overwriting newer results.

2. **Database Indexing (`FULLTEXT` + B-Tree):**
   - **Why avoid `LIKE '%query%'` everywhere?** A leading wildcard (`%term%`) forces MySQL to perform an `O(N)` full table scan regardless of B-Tree indexes.
   - Instead, [`backend/schema.sql`](backend/schema.sql) defines:
     - `FULLTEXT INDEX ft_emp_name_dept (name, department)` — used in `BOOLEAN MODE` (`+token*`) for alphanumeric queries of 3+ characters, allowing fast inverted-index lookups on any word in `name` or `department` (e.g., `"Rah"` matches `"Rahul Sharma"` and `"Rahim Khan"`; `"Sharma"` matches `"Rahul Sharma"`).
     - `INDEX x_emp_name (name)` and `INDEX x_emp_department (department)` — used via prefix `LIKE 'term%'` for short 1–2 character tokens like `"HR"` or `"IT"` (which fall below MySQL InnoDB's default 3-character `FULLTEXT` token limit) or punctuation-containing queries.

3. **Payload & Memory Bounding (Column Projection + Pagination):**
   - `EmployeeRepository` selects only the required display columns explicitly (`EMPLOYEE_COLUMNS`) rather than `SELECT *`, avoiding over-fetching if internal columns are added later.
   - Results are paginated via `limit` (default `12` in UI, max `100` in API) and `offset`, ensuring neither MySQL, FastAPI JSON serialization, nor React DOM rendering ever has to process the entire table at once.

---

## API Reference

- `GET /employees?search=rahul&limit=20&offset=0`
  - `search` *(optional)*: Filters by `name` or `department`. Omitting returns paginated employees.
  - `limit` *(default `20`, `1..100`)*, `offset` *(default `0`, `>= 0`)*.
  - Error status codes:
    - `400 Bad Request` (`INVALID_QUERY`): Empty/whitespace `search=` or query > 100 chars.
    - `422 Unprocessable Entity` (`VALIDATION_ERROR`): Invalid `limit`/`offset` types or bounds.
    - `503 Service Unavailable` (`DATABASE_UNAVAILABLE`): Database unreachable or query failure (no internal stack traces exposed).
- `GET /health`
  - Returns `200 OK` when API and MySQL connection are healthy, or `503` if the database is unreachable.

---

## Clean Architecture & Extensibility

Backend layers follow strict separation of concerns (`Routers` → `Services` → `Repositories` → `DB/Models`):
- **Routers** handle HTTP query parsing/validation and response schemas only.
- **Services** enforce domain rules (trimming, query validation) without knowing about SQL or HTTP.
- **Repositories** isolate all SQLAlchemy queries.

Adding future endpoints (such as `POST /employees`) only requires adding a create schema, repository insert method, service validation, and route handler without touching existing logic.

