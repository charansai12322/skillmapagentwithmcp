"use client";

import React from "react";
import { JobOpportunity } from "@/types/skillmap";
import { X, Trash2, ExternalLink, Bookmark, MapPin } from "lucide-react";

interface SavedDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  savedJobs: JobOpportunity[];
  onRemoveJob: (job: JobOpportunity) => void;
  onClearAll: () => void;
}

export const SavedDrawer: React.FC<SavedDrawerProps> = ({
  isOpen,
  onClose,
  savedJobs,
  onRemoveJob,
  onClearAll,
}) => {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs transition-opacity animate-fade-in"
    >
      <div className="w-full max-w-md h-full bg-[#FFFFFF] shadow-2xl flex flex-col border-l border-[#DDE1D8]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#DDE1D8] px-6 py-4">
          <div className="flex items-center gap-2">
            <Bookmark className="h-4 w-4 text-[#111914]" />
            <h3 className="font-display text-base font-bold text-[#111914]">
              Saved Opportunities
            </h3>
            <span className="rounded-full bg-[#EBEDE5] px-2 py-0.5 text-xs font-bold text-[#111914] tabular-nums">
              {savedJobs.length}
            </span>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-[#626B63] hover:bg-[#EBEDE5] transition-colors"
            aria-label="Close saved drawer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content list */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {savedJobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <Bookmark className="h-8 w-8 text-[#8B9A8D] stroke-1" />
              <p className="mt-3 text-sm font-semibold text-[#111914]">
                No saved opportunities
              </p>
              <p className="mt-1 text-xs text-[#626B63] max-w-xs">
                Click the bookmark icon on any job card to store it in your local browser session.
              </p>
            </div>
          ) : (
            savedJobs.map((job, idx) => (
              <div
                key={idx}
                className="flex flex-col justify-between rounded-xl border border-[#DDE1D8] bg-[#F5F4EC] p-4 text-xs shadow-xs"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="font-display text-sm font-bold text-[#111914]">
                      {job.title}
                    </h4>
                    <span className="text-xs font-medium text-[#626B63]">
                      {job.company}
                    </span>
                    {job.location && (
                      <span className="flex items-center gap-1 mt-1 text-[11px] text-[#8B9A8D]">
                        <MapPin className="h-3 w-3" />
                        <span>{job.location}</span>
                      </span>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={() => onRemoveJob(job)}
                    className="text-[#8B9A8D] hover:text-[#B42318] p-1 transition-colors"
                    title="Remove item"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>

                {job.apply_url && (
                  <div className="mt-3 pt-2 border-t border-[#DDE1D8]/60 flex justify-end">
                    <a
                      href={job.apply_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-[11px] font-semibold text-[#237A50] hover:underline"
                    >
                      <span>Apply Now</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        {savedJobs.length > 0 && (
          <div className="border-t border-[#DDE1D8] p-4 flex justify-between items-center bg-[#F5F4EC]">
            <span className="text-[11px] text-[#626B63]">
              Stored locally on this device
            </span>
            <button
              type="button"
              onClick={onClearAll}
              className="text-xs font-semibold text-[#B42318] hover:underline"
            >
              Clear All
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
