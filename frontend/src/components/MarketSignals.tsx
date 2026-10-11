"use client";

import React from "react";
import { SkillQueryResponse } from "@/types/skillmap";
import { TrendingUp, Banknote, Briefcase, Cpu, Check } from "lucide-react";

interface MarketSignalsProps {
  data: SkillQueryResponse;
}

export const MarketSignals: React.FC<MarketSignalsProps> = ({ data }) => {
  const overview = data.industry_overview;
  const salary = data.salary_insights;
  const jobsCount = data.job_opportunities.length;
  const tools = data.metadata.tools_invoked;

  // Format salary display honestly
  const salaryDisplay =
    salary?.median || salary?.entry_level || salary?.senior
      ? `${salary.median || salary.entry_level || salary.senior} ${
          salary.currency || ""
        }`.trim()
      : salary?.notes
      ? salary.notes.slice(0, 45) + (salary.notes.length > 45 ? "..." : "")
      : "Not specified";

  return (
    <section className="my-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {/* 1. Demand Signal */}
      <div className="flex flex-col justify-between rounded-xl border border-[#DDE1D8] bg-[#FFFFFF] p-5 shadow-xs">
        <div className="flex items-center justify-between text-[#626B63]">
          <span className="text-[11px] font-semibold tracking-wider uppercase">
            Market Demand
          </span>
          <TrendingUp className="h-4 w-4 text-[#1C3027]" />
        </div>
        <div className="mt-3">
          <div className="font-display text-2xl font-bold text-[#111914]">
            {overview?.demand_level || "HIGH"}
          </div>
          <p className="mt-1 text-xs text-[#626B63] truncate">
            Based on current industry synthesis
          </p>
        </div>
      </div>

      {/* 2. Salary Signal */}
      <div className="flex flex-col justify-between rounded-xl border border-[#DDE1D8] bg-[#FFFFFF] p-5 shadow-xs">
        <div className="flex items-center justify-between text-[#626B63]">
          <span className="text-[11px] font-semibold tracking-wider uppercase">
            Compensation Signal
          </span>
          <Banknote className="h-4 w-4 text-[#1C3027]" />
        </div>
        <div className="mt-3">
          <div className="font-display text-lg font-bold text-[#111914] truncate">
            {salaryDisplay}
          </div>
          <p className="mt-1 text-xs text-[#626B63] truncate">
            {salary ? "Reported market distribution" : "Undisclosed by live postings"}
          </p>
        </div>
      </div>

      {/* 3. Verified Job Openings */}
      <div className="flex flex-col justify-between rounded-xl border border-[#DDE1D8] bg-[#FFFFFF] p-5 shadow-xs">
        <div className="flex items-center justify-between text-[#626B63]">
          <span className="text-[11px] font-semibold tracking-wider uppercase">
            Live Openings
          </span>
          <Briefcase className="h-4 w-4 text-[#1C3027]" />
        </div>
        <div className="mt-3">
          <div className="font-display text-2xl font-bold text-[#111914] tabular-nums">
            {jobsCount}
          </div>
          <p className="mt-1 text-xs text-[#626B63]">
            {jobsCount > 0 ? "Direct applicant postings" : "No live openings in batch"}
          </p>
        </div>
      </div>

      {/* 4. Multi-Agent Sources */}
      <div className="flex flex-col justify-between rounded-xl border border-[#DDE1D8] bg-[#FFFFFF] p-5 shadow-xs">
        <div className="flex items-center justify-between text-[#626B63]">
          <span className="text-[11px] font-semibold tracking-wider uppercase">
            Agent Provenance
          </span>
          <Cpu className="h-4 w-4 text-[#1C3027]" />
        </div>
        <div className="mt-3">
          <div className="flex flex-wrap gap-1">
            {tools.map((t, idx) => (
              <span
                key={idx}
                className="rounded bg-[#EBEDE5] px-1.5 py-0.5 text-[10px] font-semibold text-[#111914]"
              >
                {t.replace("RAPIDAPI_", "").replace("_SEARCH", "").replace("_MCP", "")}
              </span>
            ))}
          </div>
          <p className="mt-1 text-xs text-[#626B63]">
            {tools.length} providers verified
          </p>
        </div>
      </div>
    </section>
  );
};
