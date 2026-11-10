const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;

function getApiBaseUrl() {
  if (!rawBaseUrl || !rawBaseUrl.trim()) {
    throw new Error(
      "VITE_API_BASE_URL is not configured. Please define it in frontend/.env."
    );
  }
  return rawBaseUrl.trim().replace(/\/+$/, "");
}

/**
 * Fetch paginated employees optionally filtered by name or department.
 * Supports AbortSignal so stale in-flight requests can be cancelled cleanly.
 */
export async function fetchEmployees({
  search = "",
  limit = 12,
  offset = 0,
  signal,
} = {}) {
  const baseUrl = getApiBaseUrl();
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  const trimmed = search.trim();
  if (trimmed.length > 0) {
    params.set("search", trimmed);
  }

  let response;
  try {
    response = await fetch(`${baseUrl}/employees?${params.toString()}`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      signal,
    });
  } catch (err) {
    if (err.name === "AbortError") {
      throw err;
    }
    throw new Error(
      "Unable to reach the server. Please verify the backend API is running."
    );
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message =
      payload?.detail ||
      `Request failed with status ${response.status}. Please try again.`;
    throw new Error(message);
  }

  return payload;
}

