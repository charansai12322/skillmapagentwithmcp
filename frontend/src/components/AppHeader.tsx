"use client";

import React, { useEffect, useState } from "react";
import { fetchHealth } from "@/lib/api";
import { HealthResponse } from "@/types/skillmap";
import { Activity, Bookmark, Sparkles, Compass } from "lucide-react";

interface AppHeaderProps {
  onOpenSaved?: () => void;
  savedCount?: number;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  onOpenSaved,
  savedCount = 0,
}) => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    fetchHealth()
      .then((data) => {
        if (isMounted) {
          setHealth(data);
          setIsOnline(data.status === "healthy");
        }
      })
      .catch(() => {
        if (isMounted) setIsOnline(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#DDE1D8] bg-[#F5F4EC]/90 backdrop-blur-md transition-colors">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand identity */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#111914] text-[#D7F36B] shadow-sm">
            <Compass className="h-5 w-5" aria-hidden="true" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-display text-lg font-bold tracking-tight text-[#111914]">
                SkillMap
              </span>
              <span className="rounded bg-[#1C3027] px-1.5 py-0.5 text-[10px] font-semibold tracking-wider text-[#D7F36B]">
                AI ATLAS
              </span>
            </div>
            <span className="text-[11px] font-medium text-[#626B63] hidden sm:inline">
              Career & Industry Intelligence
            </span>
          </div>
        </div>

        {/* Center / Navigation items */}
        <nav className="hidden md:flex items-center gap-1 rounded-full border border-[#DDE1D8] bg-[#EBEDE5]/60 px-3 py-1">
          <a
            href="#workspace"
            className="rounded-full px-3 py-1 text-xs font-medium text-[#111914] hover:bg-[#FFFFFF] transition-colors"
          >
            Research
          </a>
          <a
            href="#results"
            className="rounded-full px-3 py-1 text-xs font-medium text-[#626B63] hover:text-[#111914] hover:bg-[#FFFFFF] transition-colors"
          >
            Intelligence
          </a>
          <a
            href="#sources"
            className="rounded-full px-3 py-1 text-xs font-medium text-[#626B63] hover:text-[#111914] hover:bg-[#FFFFFF] transition-colors"
          >
            Provenance
          </a>
        </nav>

        {/* Status indicator and Saved drawer button */}
        <div className="flex items-center gap-3">
          {/* Health indicator */}
          <div
            className="flex items-center gap-2 rounded-full border border-[#DDE1D8] bg-[#FFFFFF] px-2.5 py-1 text-xs text-[#626B63] shadow-xs"
            title={
              health
                ? `Services: Gemini (${health.services.gemini}), JSearch (${health.services.rapidapi}), Tavily (${health.services.tavily})`
                : "Checking backend connection..."
            }
          >
            <span
              className={`inline-block h-2 w-2 rounded-full ${
                isOnline === true
                  ? "bg-[#237A50] animate-pulse"
                  : isOnline === false
                  ? "bg-[#B42318]"
                  : "bg-[#8B9A8D]"
              }`}
            />
            <span className="text-[11px] font-medium tabular-nums hidden sm:inline">
              {isOnline === true ? "Network Active" : isOnline === false ? "Offline" : "Connecting..."}
            </span>
          </div>

          {/* Saved Drawer button */}
          <button
            type="button"
            onClick={onOpenSaved}
            className="relative flex items-center gap-1.5 rounded-lg border border-[#DDE1D8] bg-[#FFFFFF] px-3 py-1.5 text-xs font-medium text-[#111914] hover:bg-[#EBEDE5] hover:border-[#8B9A8D] transition-colors focus:outline-none focus:ring-2 focus:ring-[#111914]"
            aria-label="View saved research items"
          >
            <Bookmark className="h-3.5 w-3.5 text-[#626B63]" />
            <span className="hidden sm:inline">Saved</span>
            {savedCount > 0 && (
              <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-[#111914] px-1 text-[10px] font-bold text-[#D7F36B] tabular-nums">
                {savedCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
