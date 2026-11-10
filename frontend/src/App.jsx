import { EmployeeList } from "./components/EmployeeList";
import { SearchBar } from "./components/SearchBar";
import { useEmployeeSearch } from "./hooks/useEmployeeSearch";

export function App() {
  const {
    searchInput,
    debouncedQuery,
    employees,
    total,
    limit,
    offset,
    isLoading,
    error,
    setSearchInput,
    clearSearch,
    setOffset,
    retry,
  } = useEmployeeSearch();

  return (
    <div className="page">
      <header className="header">
        <h1>Employee Directory</h1>
        <p className="subtitle">Search employees by name or department.</p>
      </header>

      <main className="container">
        <SearchBar
          value={searchInput}
          onChange={setSearchInput}
          onClear={clearSearch}
          isLoading={isLoading}
        />

        <EmployeeList
          employees={employees}
          total={total}
          limit={limit}
          offset={offset}
          isLoading={isLoading}
          error={error}
          searchQuery={debouncedQuery}
          onRetry={retry}
          onClearSearch={clearSearch}
          onPageChange={setOffset}
        />
      </main>
    </div>
  );
}

export default App;
