"use client";

import React, { useState, useRef, useEffect } from "react";
import { SkillQueryRequest, ExperienceLevel } from "@/types/skillmap";
import {
  Sparkles,
  ArrowRight,
  MapPin,
  Globe,
  Briefcase,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  RotateCcw,
} from "lucide-react";

interface ResearchComposerProps {
  onSubmit: (request: SkillQueryRequest) => void;
  isLoading: boolean;
  initialQuery?: string;
}

const EXAMPLE_QUERIES = [
  "Analyze demand for Generative AI jobs and internships in India, key skills, and current opportunities.",
  "What is the market demand for Rust and systems engineering in the US, and what do employers expect?",
  "Map entry-level Python and data engineering roles in Bengaluru with salary benchmarks.",
  "Which backend and cloud architecture skills are most sought after for remote AI engineering roles?",
];

export const ResearchComposer: React.FC<ResearchComposerProps> = ({
  onSubmit,
  isLoading,
  initialQuery = "",
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [location, setLocation] = useState("");
  const [country, setCountry] = useState("in");
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel | "">(
    "entry"
  );
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (isLoading) return;

    const trimmed = query.trim();
    if (trimmed.length < 3) {
      setErrorMsg("Please enter a research inquiry of at least 3 characters.");
      textareaRef.current?.focus();
      return;
    }

    setErrorMsg(null);

    const payload: SkillQueryRequest = {
      query: trimmed,
      location: location.trim() || null,
      country: country.trim().toLowerCase() || null,
      experience_level: (experienceLevel as ExperienceLevel) || null,
      remote_only: remoteOnly,
    };

    onSubmit(payload);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSelectExample = (ex: string) => {
    setQuery(ex);
    setErrorMsg(null);
    textareaRef.current?.focus();
  };

  return (
    <section
      id="workspace"
      className="relative overflow-hidden rounded-2xl bg-[#111914] text-white shadow-xl technical-grid-dark border border-[#1C3027]"
    >
      {/* Decorative top accent line */}
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-transparent via-[#D7F36B] to-transparent opacity-60" />

      <div className="p-6 sm:p-8 lg:p-10">
        {/* Eyebrow and Headline */}
        <div className="flex flex-col gap-2 max-w-3xl">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold tracking-wider text-[#D7F36B] uppercase">
              CAREER INTELLIGENCE / 01
            </span>
            <span className="text-white/20">•</span>
            <span className="text-xs text-[#8B9A8D]">
              Multi-Agent Evidence Synthesis
            </span>
          </div>

          <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-white leading-tight">
            See where the industry is going.
          </h1>

          <p className="text-sm sm:text-base text-[#8B9A8D] mt-1 max-w-2xl leading-relaxed">
            Synthesize real-time labor demand, verified core skills, and active
            career opportunities grounded in live web intelligence.
          </p>
        </div>

        {/* Query Input Area */}
        <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
          <div className="relative rounded-xl border border-white/10 bg-[#1C3027]/40 p-3 sm:p-4 backdrop-blur-sm focus-within:border-[#D7F36B]/60 focus-within:ring-1 focus-within:ring-[#D7F36B]/40 transition-all">
            <textarea
              ref={textareaRef}
              rows={3}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (errorMsg) setErrorMsg(null);
              }}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              placeholder="e.g. Map demand for Generative AI in India, required technical skills, and current hiring opportunities..."
              className="w-full resize-none bg-transparent text-sm sm:text-base text-white placeholder-white/30 focus:outline-none"
              aria-label="Research query"
            />

            {/* Bottom Bar inside Composer */}
            <div className="mt-3 flex flex-wrap items-center justify-between gap-3 border-t border-white/5 pt-3">
              {/* Filter toggle button */}
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition-colors ${
                  showFilters || location || experienceLevel || remoteOnly
                    ? "bg-[#D7F36B]/10 text-[#D7F36B] border border-[#D7F36B]/30"
                    : "text-white/60 hover:text-white hover:bg-white/5"
                }`}
                aria-expanded={showFilters}
              >
                <SlidersHorizontal className="h-3.5 w-3.5" />
                <span>Structured Filters</span>
                {(location || remoteOnly) && (
                  <span className="h-1.5 w-1.5 rounded-full bg-[#D7F36B]" />
                )}
                {showFilters ? (
                  <ChevronUp className="h-3 w-3" />
                ) : (
                  <ChevronDown className="h-3 w-3" />
                )}
              </button>

              {/* Submit Button & Shortcut hint */}
              <div className="flex items-center gap-3 ml-auto">
                <span className="hidden text-[11px] text-white/30 sm:inline">
                  Press <kbd className="rounded border border-white/20 px-1 py-0.5 text-[10px] text-white/50">Enter</kbd> to search
                </span>

                <button
                  type="submit"
                  disabled={isLoading || query.trim().length < 3}
                  className="flex items-center gap-2 rounded-lg bg-[#D7F36B] px-4 py-2 text-xs sm:text-sm font-semibold text-[#111914] shadow-sm hover:bg-[#c9e855] disabled:cursor-not-allowed disabled:opacity-40 transition-all focus:outline-none focus:ring-2 focus:ring-[#D7F36B] focus:ring-offset-2 focus:ring-offset-[#111914]"
                >
                  {isLoading ? (
                    <>
                      <span className="h-3.5 w-3.5 rounded-full border-2 border-[#111914] border-t-transparent animate-spin" />
                      <span>Synthesizing...</span>
                    </>
                  ) : (
                    <>
                      <span>Generate intelligence</span>
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Validation error message */}
          {errorMsg && (
            <p className="text-xs font-medium text-[#f87171] flex items-center gap-1">
              <span>•</span> {errorMsg}
            </p>
          )}

          {/* Collapsible Structured Filters */}
          {showFilters && (
            <div className="rounded-xl border border-white/10 bg-white/5 p-4 animate-fade-in">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {/* Location Filter */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-medium text-white/70 flex items-center gap-1">
                    <MapPin className="h-3 w-3 text-[#D7F36B]" />
                    <span>Location</span>
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Bengaluru, San Francisco"
                    className="rounded-lg border border-white/10 bg-[#111914] px-3 py-1.5 text-xs text-white placeholder-white/30 focus:border-[#D7F36B] focus:outline-none"
                  />
                </div>

                {/* Country Filter */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-medium text-white/70 flex items-center gap-1">
                    <Globe className="h-3 w-3 text-[#D7F36B]" />
                    <span>Country (ISO 2-letter)</span>
                  </label>
                  <select
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="rounded-lg border border-white/10 bg-[#111914] px-3 py-1.5 text-xs text-white focus:border-[#D7F36B] focus:outline-none"
                  >
                    <option value="in">India (in)</option>
                    <option value="us">United States (us)</option>
                    <option value="gb">United Kingdom (gb)</option>
                    <option value="ca">Canada (ca)</option>
                    <option value="de">Germany (de)</option>
                    <option value="sg">Singapore (sg)</option>
                  </select>
                </div>

                {/* Experience Level Filter */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-medium text-white/70 flex items-center gap-1">
                    <Briefcase className="h-3 w-3 text-[#D7F36B]" />
                    <span>Experience Level</span>
                  </label>
                  <select
                    value={experienceLevel}
                    onChange={(e) =>
                      setExperienceLevel(e.target.value as ExperienceLevel | "")
                    }
                    className="rounded-lg border border-white/10 bg-[#111914] px-3 py-1.5 text-xs text-white focus:border-[#D7F36B] focus:outline-none"
                  >
                    <option value="">Any Level</option>
                    <option value="entry">Entry Level / Intern</option>
                    <option value="mid">Mid Level (2–5 years)</option>
                    <option value="senior">Senior / Staff (5+ years)</option>
                  </select>
                </div>

                {/* Remote Only Toggle */}
                <div className="flex flex-col justify-end">
                  <label className="flex items-center gap-2 cursor-pointer py-1.5">
                    <input
                      type="checkbox"
                      checked={remoteOnly}
                      onChange={(e) => setRemoteOnly(e.target.checked)}
                      className="h-4 w-4 rounded border-white/20 bg-[#111914] text-[#D7F36B] focus:ring-[#D7F36B]"
                    />
                    <span className="text-xs font-medium text-white/80">
                      Remote Opportunities Only
                    </span>
                  </label>
                </div>
              </div>
            </div>
          )}
        </form>

        {/* Suggestion Chips */}
        <div className="mt-6 flex flex-col gap-2">
          <span className="text-[11px] font-semibold text-[#8B9A8D] uppercase tracking-wider">
            Curated Research Inquiries
          </span>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUERIES.map((ex, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectExample(ex)}
                disabled={isLoading}
                className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-left text-xs text-white/70 hover:border-[#D7F36B]/40 hover:text-white hover:bg-white/10 transition-colors disabled:opacity-50"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
