/**
 * EmotionPill.jsx
 *
 * Reusable colored chip for displaying a single emotion label.
 * Colors match the Integra style guide tokens exactly.
 */

const EMOTION_COLORS = {
  awe:       "#7b9ea6",
  overwhelm: "#9b7fa6",
  fear:      "#a67b7b",
  grief:     "#7a8fa6",
  confusion: "#a69b7b",
  joy:       "#a6c47b",
  gratitude: "#c4956a",
  calm:      "#7ba68f",
};

export default function EmotionPill({ emotion, score = null, size = "sm" }) {
  const color = EMOTION_COLORS[emotion] || "var(--text-muted)";
  const fontSize = size === "sm" ? "10px" : "12px";
  const padding = size === "sm" ? "2px 8px" : "4px 12px";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "4px",
        fontSize,
        fontWeight: 500,
        padding,
        borderRadius: "4px",
        background: `${color}18`,
        color,
        border: `1px solid ${color}30`,
        whiteSpace: "nowrap",
      }}
    >
      {emotion}
      {score !== null && (
        <span style={{ opacity: 0.6, fontWeight: 300 }}>
          {Math.round(score * 100)}%
        </span>
      )}
    </span>
  );
}
