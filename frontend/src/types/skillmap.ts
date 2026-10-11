/**
 * SkillMap AI TypeScript Contract
 * Mapped 1:1 with backend/app/schemas.py
 */

export type ExperienceLevel = "entry" | "mid" | "senior";

export type JobSearchStatus = "success" | "empty" | "unavailable" | "error";

export type ResponseStatus = "SUCCESS" | "PARTIAL_SUCCESS" | "ERROR";

export interface SkillQueryRequest {
  query: string;
  location?: string | null;
  country?: string | null;
  experience_level?: ExperienceLevel | null;
  remote_only?: boolean;
}

export interface JobOpportunity {
  title: string;
  company: string;
  location?: string | null;
  description?: string | null;
  employment_type?: string | null;
  experience_level?: string | null;
  is_remote?: boolean;
  salary?: string | null;
  posted_at?: string | null;
  apply_url?: string | null;
  skills: string[];
  source: string;
}

export interface IndustryOverview {
  summary: string;
  demand_level?: "HIGH" | "MODERATE" | "LOW" | "EMERGING" | string;
  growth_metrics?: string | null;
}

export interface SalaryInsights {
  currency: string;
  entry_level?: string | null;
  median?: string | null;
  senior?: string | null;
  notes?: string | null;
}

export interface SourceAttribution {
  name: string;
  url?: string | null;
  retrieved_at?: string | null;
}

export interface ResponseMetadata {
  execution_time_ms: number;
  timestamp: string;
  tools_invoked: string[];
  job_results_count: number;
  job_search_status: JobSearchStatus;
}

export interface SkillQueryResponse {
  request_id: string;
  query: string;
  status: ResponseStatus;
  industry_overview?: IndustryOverview | null;
  salary_insights?: SalaryInsights | null;
  key_skills: string[];
  job_opportunities: JobOpportunity[];
  sources: SourceAttribution[];
  warnings: string[];
  metadata: ResponseMetadata;
}

export interface HealthResponse {
  status: "healthy" | string;
  version: string;
  timestamp: string;
  services: {
    gemini?: "configured" | "missing" | string;
    rapidapi?: "configured" | "missing" | string;
    composio?: "configured" | "missing" | string;
    tavily?: "configured" | "not_configured" | "missing" | string;
    [key: string]: string | undefined;
  };
}

export interface ErrorResponse {
  error: boolean;
  code: string;
  message: string;
  request_id?: string | null;
  details?: Record<string, unknown> | null;
}
