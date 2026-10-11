"use client";

import React from "react";
import { AlertTriangle, Info } from "lucide-react";

interface WarningBannerProps {
  warnings: string[];
}

export const WarningBanner: React.FC<WarningBannerProps> = ({ warnings }) => {
  if (warnings.length === 0) return null;

  return (
    <div
      role="alert"
      className="my-6 rounded-xl border border-[#925F12]/30 bg-[#925F12]/10 p-4 text-xs text-[#925F12]"
    >
      <div className="flex items-start gap-2.5">
        <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5 text-[#925F12]" />
        <div className="flex flex-col gap-1">
          <span className="font-bold text-xs uppercase tracking-wider">
            Partial Service Notice
          </span>
          {warnings.map((warn, idx) => (
            <p key={idx} className="text-xs text-[#925F12]/90 leading-relaxed">
              • {warn}
            </p>
          ))}
          <span className="text-[11px] text-[#925F12]/70 mt-1">
            Data synthesized from available operational tools is displayed below.
          </span>
        </div>
      </div>
    </div>
  );
};
