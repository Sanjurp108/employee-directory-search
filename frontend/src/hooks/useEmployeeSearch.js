import { useCallback, useEffect, useState } from "react";

import { fetchEmployees } from "../api/employees";
import { useDebounce } from "./useDebounce";

const PAGE_SIZE = 12;
const DEBOUNCE_DELAY_MS = 350;


export function useEmployeeSearch() {
  const [searchInput, setSearchInput] = useState("");
  const [offset, setOffset] = useState(0);
  const [retryCounter, setRetryCounter] = useState(0);

  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);


  const normalizedInput = searchInput.trim();
  const debouncedQuery = useDebounce(normalizedInput, DEBOUNCE_DELAY_MS);

  const handleSearchChange = useCallback((nextValue) => {
    setSearchInput(nextValue);
    setOffset(0);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchInput("");
    setOffset(0);
  }, []);

  const retry = useCallback(() => {
    setRetryCounter((prev) => prev + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadEmployees() {
      setIsLoading(true);
      setError(null);

      try {
        const data = await fetchEmployees({
          search: debouncedQuery,
          limit: PAGE_SIZE,
          offset,
          signal: controller.signal,
        });
        setEmployees(data.items ?? []);
        setTotal(data.total ?? 0);
      } catch (err) {
        if (err.name === "AbortError") {
          return;
        }
        setEmployees([]);
        setTotal(0);
        setError(err.message || "Failed to load employees.");
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadEmployees();

    return () => {
      controller.abort();
    };
  }, [debouncedQuery, offset, retryCounter]);

  return {
    searchInput,
    debouncedQuery,
    employees,
    total,
    limit: PAGE_SIZE,
    offset,
    isLoading,
    error,
    setSearchInput: handleSearchChange,
    clearSearch,
    setOffset,
    retry,
  };
}

