"use client";

import React, { useState, useEffect } from "react";
import { AppHeader } from "@/components/AppHeader";
import { ResearchComposer } from "@/components/ResearchComposer";
import { ResearchProgress } from "@/components/ResearchProgress";
import { ResearchBrief } from "@/components/ResearchBrief";
import { MarketSignals } from "@/components/MarketSignals";
import { SkillsExplorer } from "@/components/SkillsExplorer";
import { JobOpportunityCard } from "@/components/JobOpportunityCard";
import { SourcesPanel } from "@/components/SourcesPanel";
import { WarningBanner } from "@/components/WarningBanner";
import { SavedDrawer } from "@/components/SavedDrawer";

import {
  SkillQueryRequest,
  SkillQueryResponse,
  JobOpportunity,
} from "@/types/skillmap";
import { querySkillMap, ApiError } from "@/lib/api";
import { Briefcase, AlertCircle, RefreshCw, Sparkles } from "lucide-react";

export default function Home() {
  const [response, setResponse] = useState<SkillQueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeQuery, setActiveQuery] = useState("");
  const [lastRequest, setLastRequest] = useState<SkillQueryRequest | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  // Saved Jobs LocalStorage persistence
  const [savedJobs, setSavedJobs] = useState<JobOpportunity[]>([]);
  const [isSavedDrawerOpen, setIsSavedDrawerOpen] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("skillmap_saved_jobs");
      if (stored) {
        setSavedJobs(JSON.parse(stored));
      }
    } catch {
      // LocalStorage not available or parse error
    }
  }, []);

  const handleToggleBookmark = (job: JobOpportunity) => {
    setSavedJobs((prev) => {
      const exists = prev.some(
        (j) => j.title === job.title && j.company === job.company
      );
      let updated: JobOpportunity[];
      if (exists) {
        updated = prev.filter(
          (j) => !(j.title === job.title && j.company === job.company)
        );
      } else {
        updated = [job, ...prev];
      }
      try {
        localStorage.setItem("skillmap_saved_jobs", JSON.stringify(updated));
      } catch {
        // LocalStorage quota or access error
      }
      return updated;
    });
  };

  const handleClearAllSaved = () => {
    setSavedJobs([]);
    try {
      localStorage.removeItem("skillmap_saved_jobs");
    } catch {
      // Ignore
    }
  };

  const handleSearch = async (req: SkillQueryRequest) => {
    setIsLoading(true);
    setActiveQuery(req.query);
    setLastRequest(req);
    setError(null);

    try {
      const result = await querySkillMap(req);
      setResponse(result);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setError(err);
      } else if (err instanceof Error) {
        setError(new ApiError(err.message));
      } else {
        setError(new ApiError("An unexpected error occurred during synthesis."));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (lastRequest) {
      handleSearch(lastRequest);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#F5F4EC] text-[#111914]">
      {/* Top Navigation */}
      <AppHeader
        onOpenSaved={() => setIsSavedDrawerOpen(true)}
        savedCount={savedJobs.length}
      />

      {/* Main Content Area */}
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
        {/* Research Query Composer */}
        <ResearchComposer
          onSubmit={handleSearch}
          isLoading={isLoading}
          initialQuery={activeQuery}
        />

        {/* Informative Multi-stage Progress Experience */}
        {isLoading && (
          <ResearchProgress query={activeQuery} onCancel={() => setIsLoading(false)} />
        )}

        {/* Error Callout */}
        {error && !isLoading && (
          <div
            role="alert"
            className="my-8 rounded-2xl border border-[#B42318]/30 bg-[#FFFFFF] p-6 sm:p-8 shadow-xs"
          >
            <div className="flex items-start gap-3 text-[#B42318]">
              <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-display text-base font-bold text-[#111914]">
                  Synthesis Interrupted
                </h3>
                <p className="mt-1 text-sm text-[#626B63] leading-relaxed">
                  {error.message}
                </p>
                {lastRequest && (
                  <button
                    type="button"
                    onClick={handleRetry}
                    className="mt-4 flex items-center gap-1.5 rounded-lg bg-[#111914] px-4 py-2 text-xs font-semibold text-white hover:bg-[#1C3027] transition-colors"
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                    <span>Retry Request</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Results Dashboard */}
        {response && !isLoading && (
          <div id="results" className="mt-12 space-y-8 animate-fade-in">
            {/* Warning Callout for Partial Success */}
            <WarningBanner warnings={response.warnings} />

            {/* Research Brief */}
            <ResearchBrief data={response} />

            {/* 4-Card Market Signals Strip */}
            <MarketSignals data={response} />

            {/* Technical Skills Taxonomy */}
            <SkillsExplorer skills={response.key_skills} />

            {/* Job Opportunities Section */}
            <section className="my-8 rounded-2xl border border-[#DDE1D8] bg-[#FFFFFF] p-6 sm:p-8 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#DDE1D8] pb-5">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-bold tracking-wider text-[#626B63] uppercase">
                      OPPORTUNITIES / 03
                    </span>
                    <span className="text-[#DDE1D8]">•</span>
                    <span className="text-xs text-[#8B9A8D] font-medium">
                      Direct Market Listings
                    </span>
                  </div>
                  <h2 className="font-display text-xl sm:text-2xl font-bold tracking-tight text-[#111914] mt-0.5">
                    Active Job Openings
                  </h2>
                </div>

                <div className="flex items-center gap-2 text-xs text-[#626B63]">
                  <span>Retrieved:</span>
                  <span className="font-bold text-[#111914] tabular-nums">
                    {response.job_opportunities.length}
                  </span>
                </div>
              </div>

              {response.job_opportunities.length > 0 ? (
                <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {response.job_opportunities.map((job, idx) => {
                    const isBookmarked = savedJobs.some(
                      (j) => j.title === job.title && j.company === job.company
                    );
                    return (
                      <JobOpportunityCard
                        key={idx}
                        job={job}
                        isBookmarked={isBookmarked}
                        onToggleBookmark={handleToggleBookmark}
                      />
                    );
                  })}
                </div>
              ) : (
                <div className="mt-8 rounded-xl border border-dashed border-[#DDE1D8] bg-[#F5F4EC]/60 p-8 text-center">
                  <Briefcase className="mx-auto h-8 w-8 text-[#8B9A8D] stroke-1" />
                  <p className="mt-3 text-sm font-semibold text-[#111914]">
                    No active job listings returned for this specific filter batch
                  </p>
                  <p className="mt-1 text-xs text-[#626B63] max-w-md mx-auto">
                    Try broadening your geographical scope or clearing location restrictions in the query composer.
                  </p>
                </div>
              )}
            </section>

            {/* Evidence Provenance & Sources Panel */}
            <SourcesPanel sources={response.sources} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#DDE1D8] bg-[#F5F4EC] py-8 text-center text-xs text-[#626B63]">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-display font-bold text-[#111914]">
              SkillMap AI
            </span>
            <span>•</span>
            <span>The Signal Atlas / Production Edition</span>
          </div>
          <div className="text-[11px] text-[#8B9A8D]">
            Intelligence synthesized via Gemini 2.5 Flash, RapidAPI JSearch v2, Tavily, and Composio.
          </div>
        </div>
      </footer>

      {/* Bookmarks Drawer */}
      <SavedDrawer
        isOpen={isSavedDrawerOpen}
        onClose={() => setIsSavedDrawerOpen(false)}
        savedJobs={savedJobs}
        onRemoveJob={handleToggleBookmark}
        onClearAll={handleClearAllSaved}
      />
    </div>
  );
}
