"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

export interface DetailPanelData {
  type: "competitor" | "alert";
  companyName: string;
  domain?: string;
  momentumScore?: number;
  tone?: string;
  coreOffering?: string;
  icp?: string;
  analystNote?: string;
  signals?: { text: string; severity: "high" | "medium" | "low" }[];
  keywords?: string[];
  headline?: string;
  summary?: string;
  severity?: string;
  businessImpact?: string;
  recommendedAction?: string;
  confidence?: number;
}

interface DetailPanelContextValue {
  selected: DetailPanelData | null;
  select: (data: DetailPanelData) => void;
  clear: () => void;
}

const DetailPanelContext = createContext<DetailPanelContextValue>({
  selected: null,
  select: () => {},
  clear: () => {},
});

export function DetailPanelProvider({ children }: { children: ReactNode }) {
  const [selected, setSelected] = useState<DetailPanelData | null>(null);

  return (
    <DetailPanelContext.Provider
      value={{
        selected,
        select: (data: DetailPanelData) => setSelected(data),
        clear: () => setSelected(null),
      }}
    >
      {children}
    </DetailPanelContext.Provider>
  );
}

export function useDetailPanel() {
  return useContext(DetailPanelContext);
}
