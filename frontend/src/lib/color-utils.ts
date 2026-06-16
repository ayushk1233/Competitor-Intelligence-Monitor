export const tonePaletteColors = [
  { bg: "#3B82F6", text: "#3B82F6", border: "#3B82F6" }, // Blue
  { bg: "#10B981", text: "#10B981", border: "#10B981" }, // Emerald
  { bg: "#F59E0B", text: "#F59E0B", border: "#F59E0B" }, // Amber
  { bg: "#8B5CF6", text: "#8B5CF6", border: "#8B5CF6" }, // Violet
  { bg: "#EC4899", text: "#EC4899", border: "#EC4899" }, // Pink
  { bg: "#6366F1", text: "#6366F1", border: "#6366F1" }, // Indigo
  { bg: "#14B8A6", text: "#14B8A6", border: "#14B8A6" }, // Teal
  { bg: "#F43F5E", text: "#F43F5E", border: "#F43F5E" }, // Rose
];

export function getToneColorHex(tone: string) {
  const t = tone.toLowerCase().trim();
  if (t === "enterprise") return { bg: "#6366F1", text: "#6366F1", border: "#6366F1" };
  if (t === "startup") return { bg: "#BC6C50", text: "#BC6C50", border: "#BC6C50" };
  if (t === "technical") return { bg: "#3B82F6", text: "#3B82F6", border: "#3B82F6" };
  if (t === "visionary") return { bg: "#F59E0B", text: "#F59E0B", border: "#F59E0B" };
  if (t === "hybrid") return { bg: "#8B5CF6", text: "#8B5CF6", border: "#8B5CF6" };

  let hash = 0;
  for (let i = 0; i < t.length; i++) {
    hash = t.charCodeAt(i) + ((hash << 5) - hash);
  }
  return tonePaletteColors[Math.abs(hash) % tonePaletteColors.length];
}

export function getSeverityColorHex(severity: string) {
  const mapping: Record<string, any> = {
    critical: { bg: "#EF4444", text: "#EF4444", border: "#EF4444" },
    high: { bg: "#F59E0B", text: "#F59E0B", border: "#F59E0B" },
    medium: { bg: "#3B82F6", text: "#3B82F6", border: "#3B82F6" },
    low: { bg: "#6B7280", text: "#6B7280", border: "#6B7280" },
  };
  return mapping[severity.toLowerCase()] || mapping["low"];
}

export function getConfidenceColorHex(confidence: number) {
  if (confidence >= 90) return { bg: "#22C55E", text: "#22C55E", border: "#22C55E" };
  if (confidence >= 70) return { bg: "#3B82F6", text: "#3B82F6", border: "#3B82F6" };
  if (confidence >= 40) return { bg: "#F59E0B", text: "#F59E0B", border: "#F59E0B" };
  return { bg: "#EF4444", text: "#EF4444", border: "#EF4444" };
}

// Helper to convert hex to rgba for backgrounds (15% opacity) and borders (30% opacity)
export function getInlineStyle(colors: { bg: string, text: string, border: string }, bgOpacity = "26", borderOpacity = "4D") {
  return {
    backgroundColor: `${colors.bg}${bgOpacity}`,
    color: colors.text,
    borderColor: `${colors.border}${borderOpacity}`,
  };
}
