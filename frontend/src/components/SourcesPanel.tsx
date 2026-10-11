"use client";

import React, { useState } from "react";
import { SourceAttribution } from "@/types/skillmap";
import { ExternalLink, ShieldCheck, ChevronDown, ChevronUp } from "lucide-react";

interface SourcesPanelProps {
  sources: SourceAttribution[];
}

export const SourcesPanel: React.FC<SourcesPanelProps> = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (sources.length === 0) return null;

  return (
    <section
      id="sources"
      className="my-8 rounded-2xl border border-[#DDE1D8] bg-[#FFFFFF] p-6 sm:p-8 shadow-xs"
    >
      <div className="flex items-center justify-between border-b border-[#DDE1D8] pb-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-[#237A50]" />
          <h3 className="font-display text-base sm:text-lg font-bold text-[#111914]">
            Data Sources & Evidence Provenance
          </h3>
          <span className="rounded-full bg-[#EBEDE5] px-2 py-0.5 text-[10px] font-bold text-[#1C3027] tabular-nums">
            {sources.length} Verified
          </span>
        </div>

        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="rounded-lg p-1 text-[#626B63] hover:bg-[#EBEDE5] transition-colors"
          aria-expanded={isOpen}
          aria-label="Toggle sources list"
        >
          {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>

      {isOpen && (
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {sources.map((src, idx) => (
            <div
              key={idx}
              className="flex flex-col justify-between rounded-xl border border-[#DDE1D8] bg-[#F5F4EC] p-4 text-xs"
            >
              <div>
                <span className="font-semibold text-[#111914] block">
                  {src.name}
                </span>
                {src.url && (
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-1 flex items-center gap-1 text-[11px] text-[#237A50] hover:underline break-all"
                  >
                    <span className="truncate max-w-[220px]">{src.url}</span>
                    <ExternalLink className="h-3 w-3 shrink-0" />
                  </a>
                )}
              </div>

              {src.retrieved_at && (
                <span className="mt-3 text-[10px] text-[#8B9A8D] tabular-nums">
                  Retrieved: {new Date(src.retrieved_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
