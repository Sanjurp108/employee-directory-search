
export function SearchBar({ value, onChange, onClear, isLoading }) {
  return (
    <div className="search-bar">
      <label htmlFor="employee-search" className="sr-only">
        Search employees by name or department
      </label>

      <div className="search-row">
        <input
          id="employee-search"
          type="text"
          className="search-input"
          placeholder="Search by name or department (e.g. Rahul, Engineering, HR)"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          autoComplete="off"
        />

        {value && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClear}
          >
            Clear
          </button>
        )}
      </div>

      {isLoading && <p className="search-status">Searching...</p>}
    </div>
  );
}
