import {
  SkillQueryRequest,
  SkillQueryResponse,
  HealthResponse,
  ErrorResponse,
} from "@/types/skillmap";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

export class ApiError extends Error {
  code: string;
  statusCode: number;
  details?: Record<string, unknown> | null;

  constructor(
    message: string,
    code = "API_ERROR",
    statusCode = 500,
    details: Record<string, unknown> | null = null
  ) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
}

/**
 * Checks backend health and service vitality.
 */
export async function fetchHealth(): Promise<HealthResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);

  try {
    const res = await fetch(`${API_BASE}/api/health`, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: controller.signal,
      cache: "no-store",
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      throw new ApiError(
        `Health check failed with status ${res.status}`,
        "HEALTH_CHECK_FAILED",
        res.status
      );
    }

    return (await res.json()) as HealthResponse;
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) throw err;
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiError("Health check timed out", "TIMEOUT", 504);
    }
    throw new ApiError(
      "Failed to connect to SkillMap AI backend. Ensure the server is running on port 8000.",
      "NETWORK_ERROR",
      0
    );
  }
}

/**
 * Submits natural language career intelligence query.
 */
export async function querySkillMap(
  payload: SkillQueryRequest
): Promise<SkillQueryResponse> {
  // Allow up to 75 seconds for multi-agent reasoning & live retrieval
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 75000);

  try {
    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      let errorData: ErrorResponse | null = null;
      try {
        errorData = (await res.json()) as ErrorResponse;
      } catch {
        // Response was not JSON
      }

      if (errorData?.message) {
        throw new ApiError(
          errorData.message,
          errorData.code || "REQUEST_ERROR",
          res.status,
          errorData.details
        );
      }

      if (res.status === 422) {
        throw new ApiError(
          "Invalid query parameters. Please check your query length or country code.",
          "VALIDATION_ERROR",
          422
        );
      }

      throw new ApiError(
        `Backend returned HTTP ${res.status}: ${res.statusText}`,
        "SERVER_ERROR",
        res.status
      );
    }

    const data = (await res.json()) as SkillQueryResponse;
    return data;
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) throw err;
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiError(
        "Intelligence synthesis timed out. The agent required more time than allotted.",
        "AGENT_TIMEOUT",
        504
      );
    }
    throw new ApiError(
      "Unable to connect to SkillMap AI backend. Check your network connection.",
      "NETWORK_ERROR",
      0
    );
  }
}
