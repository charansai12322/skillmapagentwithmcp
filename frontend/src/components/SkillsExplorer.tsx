"use client";

import React, { useState } from "react";
import { Check, Copy, Layers, Search } from "lucide-react";

interface SkillsExplorerProps {
  skills: string[];
}

export const SkillsExplorer: React.FC<SkillsExplorerProps> = ({ skills }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [copied, setCopied] = useState(false);

  // Clean raw markdown artifacts from skills strings
  const cleanedSkills = skills
    .map((s) => s.replace(/\*\*/g, "").replace(/^[-*•]\s*/, "").trim())
    .filter((s) => s.length > 0);

  const filtered = cleanedSkills.filter((s) =>
    s.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCopyAll = () => {
    if (cleanedSkills.length === 0) return;
    navigator.clipboard.writeText(cleanedSkills.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="my-8 rounded-2xl border border-[#DDE1D8] bg-[#FFFFFF] p-6 sm:p-8 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DDE1D8] pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-bold tracking-wider text-[#626B63] uppercase">
              TAXONOMY / 02
            </span>
            <span className="text-[#DDE1D8]">•</span>
            <span className="text-xs text-[#8B9A8D] font-medium">
              Extracted Capabilities
            </span>
          </div>
          <h2 className="font-display text-xl sm:text-2xl font-bold tracking-tight text-[#111914] mt-0.5">
            Key Technical Skills & Competencies
          </h2>
        </div>

        <div className="flex items-center gap-2">
          {/* Quick filter input */}
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-[#8B9A8D]" />
            <input
              type="text"
              placeholder="Filter skills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="rounded-lg border border-[#DDE1D8] bg-[#F5F4EC] py-1.5 pl-8 pr-3 text-xs text-[#111914] placeholder-[#8B9A8D] focus:border-[#111914] focus:outline-none"
            />
          </div>

          {/* Copy all button */}
          <button
            type="button"
            onClick={handleCopyAll}
            className="flex items-center gap-1.5 rounded-lg border border-[#DDE1D8] bg-[#FFFFFF] px-3 py-1.5 text-xs font-medium text-[#111914] hover:bg-[#EBEDE5] transition-colors"
            title="Copy all skills to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-[#237A50]" />
                <span className="text-[#237A50]">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-[#626B63]" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Skills Grid */}
      {filtered.length > 0 ? (
        <div className="mt-6 flex flex-wrap gap-2.5">
          {filtered.map((skill, idx) => (
            <div
              key={idx}
              className="group flex items-center gap-2 rounded-xl border border-[#DDE1D8] bg-[#F5F4EC] px-3.5 py-2 text-xs font-semibold text-[#111914] hover:border-[#111914] hover:bg-[#FFFFFF] transition-all shadow-xs"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-[#1C3027] group-hover:bg-[#D7F36B] transition-colors" />
              <span>{skill}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-6 text-sm text-[#626B63] italic">
          {searchTerm
            ? `No skills matching "${searchTerm}".`
            : "No specific skills extracted for this inquiry."}
        </p>
      )}
    </section>
  );
};
