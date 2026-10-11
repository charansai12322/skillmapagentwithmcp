"use client";

import React, { useEffect, useState } from "react";
import { Compass, CheckCircle2, Loader2, Sparkles, AlertCircle } from "lucide-react";

interface ResearchProgressProps {
  query: string;
  onCancel?: () => void;
}

interface Stage {
  id: number;
  label: string;
  detail: string;
  approxSec: number;
}

const STAGES: Stage[] = [
  {
    id: 1,
    label: "Analyzing Inquiry & Context",
    detail: "Parsing domain requirements, geographical bounds, and role scope.",
    approxSec: 0,
  },
  {
    id: 2,
    label: "Synthesizing Web Intelligence",
    detail: "Querying Tavily and Composio MCP for market signals and industry demand.",
    approxSec: 4,
  },
  {
    id: 3,
    label: "Retrieving Verified Job Openings",
    detail: "Searching RapidAPI JSearch v2 for active openings and direct apply links.",
    approxSec: 9,
  },
  {
    id: 4,
    label: "Extracting Skills & Compensation",
    detail: "Structuring complementary technologies and compensation ranges.",
    approxSec: 14,
  },
  {
    id: 5,
    label: "Compiling Evidence-Backed Brief",
    detail: "Formatting final intelligence brief with strict provenance.",
    approxSec: 19,
  },
];

export const ResearchProgress: React.FC<ResearchProgressProps> = ({
  query,
}) => {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Determine current active stage based on elapsed seconds
  const currentStageIndex = STAGES.findIndex(
    (s, i) =>
      elapsed >= s.approxSec &&
      (i === STAGES.length - 1 || elapsed < STAGES[i + 1].approxSec)
  );

  const activeIndex = currentStageIndex === -1 ? STAGES.length - 1 : currentStageIndex;

  return (
    <div
      role="status"
      aria-live="polite"
      className="my-8 rounded-2xl border border-[#DDE1D8] bg-[#FFFFFF] p-6 sm:p-8 shadow-sm technical-grid"
    >
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DDE1D8] pb-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#111914] text-[#D7F36B] shadow-sm animate-signal-pulse">
            <Compass className="h-5 w-5 animate-spin-slow" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-display text-base sm:text-lg font-bold text-[#111914]">
                Multi-Agent Synthesis in Progress
              </h2>
              <span className="rounded-full bg-[#EBEDE5] px-2 py-0.5 text-[10px] font-bold tracking-wider text-[#1C3027] uppercase">
                Live Retrieval
              </span>
            </div>
            <p className="text-xs text-[#626B63] mt-0.5 max-w-xl truncate">
              Inquiry: &ldquo;{query}&rdquo;
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto rounded-lg bg-[#F5F4EC] px-3 py-1.5 border border-[#DDE1D8]">
          <span className="text-[11px] font-semibold text-[#626B63] uppercase">
            Elapsed:
          </span>
          <span className="text-sm font-bold text-[#111914] tabular-nums">
            {elapsed}s
          </span>
        </div>
      </div>

      {/* Sweeping Radar Bar */}
      <div className="relative my-6 h-1.5 w-full overflow-hidden rounded-full bg-[#EBEDE5]">
        <div className="h-full w-1/3 rounded-full bg-[#111914] animate-sweep-line" />
      </div>

      {/* Stage Sequence List */}
      <div className="grid grid-cols-1 gap-3 sm:gap-4 md:grid-cols-5">
        {STAGES.map((stage, idx) => {
          const isDone = idx < activeIndex;
          const isCurrent = idx === activeIndex;

          return (
            <div
              key={stage.id}
              className={`flex flex-col gap-1.5 rounded-xl p-3.5 transition-all border ${
                isCurrent
                  ? "border-[#111914] bg-[#F5F4EC] shadow-xs"
                  : isDone
                  ? "border-[#237A50]/20 bg-[#FFFFFF] opacity-90"
                  : "border-[#DDE1D8]/60 bg-[#FFFFFF]/60 opacity-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-[#8B9A8D] tabular-nums">
                  STAGE 0{stage.id}
                </span>
                {isDone ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-[#237A50]" />
                ) : isCurrent ? (
                  <Loader2 className="h-3.5 w-3.5 text-[#111914] animate-spin" />
                ) : (
                  <span className="h-2 w-2 rounded-full bg-[#DDE1D8]" />
                )}
              </div>

              <h3 className="font-display text-xs font-semibold text-[#111914] leading-snug">
                {stage.label}
              </h3>

              <p className="text-[11px] text-[#626B63] leading-relaxed hidden sm:block">
                {stage.detail}
              </p>
            </div>
          );
        })}
      </div>

      {/* Disclaimer */}
      <div className="mt-6 flex items-center gap-2 border-t border-[#DDE1D8]/60 pt-4 text-[11px] text-[#8B9A8D]">
        <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#8B9A8D]" />
        <span>
          Live query orchestration contacts Google Gemini, RapidAPI JSearch v2, Tavily, and Composio. Typical execution completes within 15–30 seconds.
        </span>
      </div>
    </div>
  );
};
