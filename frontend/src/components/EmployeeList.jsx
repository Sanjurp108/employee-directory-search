import { EmployeeCard } from "./EmployeeCard";

export function EmployeeList({
  employees,
  total,
  limit,
  offset,
  isLoading,
  error,
  searchQuery,
  onRetry,
  onClearSearch,
  onPageChange,
}) {
  if (isLoading) {
    return (
      <section className="status-box" aria-busy="true" aria-live="polite">
        <span className="spinner" aria-hidden="true" />
        <p>Loading employees...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="status-box error-box" role="alert">
        <h2>Unable to load employees</h2>
        <p>{error}</p>
        <button type="button" className="btn btn-primary" onClick={onRetry}>
          Retry
        </button>
      </section>
    );
  }

  if (employees.length === 0) {
    return (
      <section className="status-box" aria-live="polite">
        <h2>No employees found</h2>
        <p>
          {searchQuery
            ? `No employees matched "${searchQuery}".`
            : "No employee records available."}
        </p>
        {searchQuery && (
          <button type="button" className="btn btn-secondary" onClick={onClearSearch}>
            Clear search
          </button>
        )}
      </section>
    );
  }

  const startIndex = offset + 1;
  const endIndex = Math.min(offset + employees.length, total);
  const hasPrev = offset > 0;
  const hasNext = offset + limit < total;

  return (
    <section aria-live="polite">
      <p className="results-count">
        Showing {startIndex}&ndash;{endIndex} of {total}{" "}
        {total === 1 ? "employee" : "employees"}
        {searchQuery ? ` for "${searchQuery}"` : ""}
      </p>

      <div className="employee-grid">
        {employees.map((employee) => (
          <EmployeeCard key={employee.id} employee={employee} />
        ))}
      </div>

      {total > limit && (
        <nav className="pagination" aria-label="Pagination">
          <button
            type="button"
            className="btn btn-secondary"
            disabled={!hasPrev}
            onClick={() => onPageChange(Math.max(0, offset - limit))}
          >
            Previous
          </button>
          <span className="page-text">
            Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit)}
          </span>
          <button
            type="button"
            className="btn btn-secondary"
            disabled={!hasNext}
            onClick={() => onPageChange(offset + limit)}
          >
            Next
          </button>
        </nav>
      )}
    </section>
  );
}
