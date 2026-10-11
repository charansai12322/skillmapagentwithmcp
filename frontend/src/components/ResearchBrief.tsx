"use client";

import React from "react";
import { SkillQueryResponse } from "@/types/skillmap";
import { Clock, ShieldCheck, AlertTriangle, MapPin, Zap } from "lucide-react";

interface ResearchBriefProps {
  data: SkillQueryResponse;
}

export const ResearchBrief: React.FC<ResearchBriefProps> = ({ data }) => {
  const overview = data.industry_overview;
  const isPartial = data.status === "PARTIAL_SUCCESS";
  const demandLevel = overview?.demand_level || "HIGH";

  const getDemandColor = (lvl: string) => {
    switch (lvl.toUpperCase()) {
      case "HIGH":
      case "VERY HIGH":
        return "bg-[#1C3027] text-[#D7F36B] border-[#1C3027]";
      case "MODERATE":
        return "bg-[#F5F4EC] text-[#111914] border-[#DDE1D8]";
      case "LOW":
        return "bg-[#EBEDE5] text-[#626B63] border-[#DDE1D8]";
      default:
        return "bg-[#1C3027] text-[#D7F36B] border-[#1C3027]";
    }
  };

  return (
    <article className="rounded-2xl border border-[#DDE1D8] bg-[#FFFFFF] p-6 sm:p-8 lg:p-10 shadow-xs">
      {/* Top Meta Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#DDE1D8] pb-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-bold tracking-wider text-[#626B63] uppercase">
            BRIEF REF: {data.request_id.slice(0, 8)}
          </span>
          <span className="text-[#DDE1D8]">•</span>
          <span
            className={`flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
              isPartial
                ? "border-[#925F12]/30 bg-[#925F12]/10 text-[#925F12]"
                : "border-[#237A50]/30 bg-[#237A50]/10 text-[#237A50]"
            }`}
          >
            {isPartial ? (
              <>
                <AlertTriangle className="h-3 w-3" />
                <span>Partial Synthesis</span>
              </>
            ) : (
              <>
                <ShieldCheck className="h-3 w-3" />
                <span>Verified Evidence</span>
              </>
            )}
          </span>
        </div>

        <div className="flex items-center gap-3 text-xs text-[#626B63]">
          <div className="flex items-center gap-1.5 tabular-nums">
            <Clock className="h-3.5 w-3.5" />
            <span>{(data.metadata.execution_time_ms / 1000).toFixed(2)}s</span>
          </div>
          <span className="text-[#DDE1D8]">•</span>
          <span className="tabular-nums">
            {new Date(data.metadata.timestamp).toLocaleDateString(undefined, {
              month: "short",
              day: "numeric",
              year: "numeric",
            })}
          </span>
        </div>
      </div>

      {/* Submitted Inquiry Block */}
      <div className="mt-6 rounded-xl border border-[#DDE1D8] bg-[#F5F4EC] p-4">
        <span className="text-[10px] font-bold tracking-wider text-[#8B9A8D] uppercase">
          Inquiry Scope
        </span>
        <p className="mt-1 font-display text-sm sm:text-base font-semibold text-[#111914] leading-relaxed">
          &ldquo;{data.query}&rdquo;
        </p>
      </div>

      {/* Main Editorial Synthesis */}
      <div className="mt-8 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-xl sm:text-2xl font-bold tracking-tight text-[#111914]">
            Industry Demand & Market Landscape
          </h2>
          <span
            className={`rounded-md border px-2.5 py-1 text-xs font-bold tracking-wide uppercase ${getDemandColor(
              demandLevel
            )}`}
          >
            {demandLevel} Demand
          </span>
        </div>

        {overview ? (
          <div className="prose prose-sm max-w-none text-[#111914] leading-relaxed font-sans space-y-4">
            {overview.summary.split("\n\n").map((para, idx) => (
              <p key={idx} className="text-sm sm:text-base text-[#111914]/90">
                {para.replace(/\*\*/g, "")}
              </p>
            ))}
          </div>
        ) : (
          <p className="text-sm text-[#626B63] italic">
            No generalized overview generated for this query. Refer to the specific skills and job openings below.
          </p>
        )}
      </div>
    </article>
  );
};
