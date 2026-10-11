"use client";

import React from "react";
import { JobOpportunity } from "@/types/skillmap";
import {
  ExternalLink,
  MapPin,
  Building2,
  Calendar,
  Banknote,
  Bookmark,
  Check,
} from "lucide-react";

interface JobOpportunityCardProps {
  job: JobOpportunity;
  isBookmarked?: boolean;
  onToggleBookmark?: (job: JobOpportunity) => void;
}

export const JobOpportunityCard: React.FC<JobOpportunityCardProps> = ({
  job,
  isBookmarked = false,
  onToggleBookmark,
}) => {
  return (
    <div className="group relative flex flex-col justify-between rounded-xl border border-[#DDE1D8] bg-[#FFFFFF] p-5 sm:p-6 shadow-xs hover:border-[#111914] hover:shadow-md transition-all">
      <div>
        {/* Top Header: Company and Bookmark */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#EBEDE5] text-[#111914] font-bold text-xs uppercase">
              {job.company.slice(0, 2)}
            </div>
            <div>
              <h4 className="text-xs font-semibold text-[#626B63] truncate max-w-[200px]">
                {job.company}
              </h4>
              <span className="text-[10px] text-[#8B9A8D] font-medium uppercase tracking-wider">
                {job.source.replace("RAPIDAPI_", "").replace("_", " ")}
              </span>
            </div>
          </div>

          {onToggleBookmark && (
            <button
              type="button"
              onClick={() => onToggleBookmark(job)}
              className={`rounded-lg p-1.5 transition-colors ${
                isBookmarked
                  ? "bg-[#111914] text-[#D7F36B]"
                  : "text-[#8B9A8D] hover:bg-[#EBEDE5] hover:text-[#111914]"
              }`}
              title={isBookmarked ? "Remove bookmark" : "Save opportunity"}
              aria-label={`Save ${job.title} at ${job.company}`}
            >
              <Bookmark className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Job Title */}
        <h3 className="font-display text-base sm:text-lg font-bold text-[#111914] mt-3 group-hover:text-[#1C3027] leading-snug">
          {job.title}
        </h3>

        {/* Metadata Pills */}
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-[#626B63]">
          {job.location && (
            <span className="flex items-center gap-1 rounded bg-[#F5F4EC] px-2 py-0.5">
              <MapPin className="h-3 w-3 text-[#8B9A8D]" />
              <span>{job.location}</span>
            </span>
          )}

          {job.employment_type && (
            <span className="rounded bg-[#F5F4EC] px-2 py-0.5 font-medium">
              {job.employment_type}
            </span>
          )}

          {job.salary && (
            <span className="flex items-center gap-1 rounded bg-[#1C3027]/10 px-2 py-0.5 font-semibold text-[#1C3027]">
              <Banknote className="h-3 w-3" />
              <span>{job.salary}</span>
            </span>
          )}
        </div>

        {/* Description Snippet */}
        {job.description && (
          <p className="mt-3 text-xs text-[#626B63] line-clamp-2 leading-relaxed">
            {job.description}
          </p>
        )}
      </div>

      {/* Card Footer: Apply Action & Posted Date */}
      <div className="mt-5 flex items-center justify-between border-t border-[#DDE1D8]/60 pt-3 text-xs">
        {job.posted_at ? (
          <span className="flex items-center gap-1 text-[11px] text-[#8B9A8D] tabular-nums">
            <Calendar className="h-3 w-3" />
            <span>
              {new Date(job.posted_at).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
              })}
            </span>
          </span>
        ) : (
          <span className="text-[11px] text-[#8B9A8D]">Verified Opening</span>
        )}

        {job.apply_url ? (
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg bg-[#111914] px-3 py-1.5 text-xs font-semibold text-[#D7F36B] hover:bg-[#1C3027] transition-colors focus:outline-none focus:ring-2 focus:ring-[#111914]"
          >
            <span>View Opportunity</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        ) : (
          <span className="text-xs text-[#8B9A8D] italic">
            Direct link unavailable
          </span>
        )}
      </div>
    </div>
  );
};
