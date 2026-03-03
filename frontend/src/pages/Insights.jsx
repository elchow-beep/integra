import { useEffect, useState } from "react";
import { getInsights } from "../api.js";
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";

/**
 * Insights.jsx
 *
 * Longitudinal view of the user's emotional arc.
 * Shows emotion timeline line chart, theme frequency, and arc summary.
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

const INTEGRA_EMOTIONS = ["awe", "overwhelm", "fear", "grief", "confusion", "joy", "gratitude", "calm"];

function formatDateShort(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

const s = {
  screen: {
    minHeight: "100vh",
    background: "var(--bg)",
    paddingBottom: "80px",
  },
  header: {
    padding: "52px 20px 0",
  },
  title: {
    fontFamily: "var(--font-display)",
    fontSize: "24px",
    color: "var(--text-primary)",
    marginBottom: "4px",
  },
  sub: {
    fontSize: "12px",
    fontWeight: 300,
    color: "var(--text-muted)",
  },
  section: {
    padding: "24px 20px 0",
  },
  sectionLabel: {
    fontSize: "11px",
    fontWeight: 500,
    letterSpacing: "0.10em",
    textTransform: "uppercase",
    color: "var(--text-muted)",
    marginBottom: "14px",
  },
  card: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-lg)",
    padding: "16px",
  },
  legendRow: {
    display: "flex",
    gap: "8px",
    flexWrap: "wrap",
    marginBottom: "16px",
  },
  legendItem: {
    display: "flex",
    alignItems: "center",
    gap: "5px",
    fontSize: "11px",
    color: "var(--text-secondary)",
  },
  legendDot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    flexShrink: 0,
  },
  arcText: {
    fontSize: "13px",
    fontWeight: 300,
    color: "var(--text-secondary)",
    lineHeight: 1.7,
  },
  themeRow: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  themeItem: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "10px",
  },
  themeLabel: {
    fontSize: "12px",
    color: "var(--text-secondary)",
    minWidth: "140px",
  },
  themeBar: {
    flex: 1,
    height: "4px",
    background: "var(--surface-raised)",
    borderRadius: "2px",
    overflow: "hidden",
  },
  themeCount: {
    fontSize: "11px",
    color: "var(--text-muted)",
    minWidth: "20px",
    textAlign: "right",
  },
  emptyState: {
    textAlign: "center",
    padding: "80px 20px",
    color: "var(--text-muted)",
    fontSize: "13px",
    fontWeight: 300,
    lineHeight: 1.7,
  },
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "var(--surface-raised)",
      border: "1px solid var(--border)",
      borderRadius: "8px",
      padding: "10px 12px",
      fontSize: "11px",
    }}>
      <div style={{ color: "var(--text-muted)", marginBottom: "6px" }}>{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ color: p.color, marginBottom: "2px" }}>
          {p.dataKey}: {(p.value * 100).toFixed(0)}%
        </div>
      ))}
    </div>
  );
};

export default function Insights({ user }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [visibleEmotions, setVisibleEmotions] = useState(new Set(INTEGRA_EMOTIONS));

  useEffect(() => {
    if (!user) return;
    getInsights(user.user_id)
      .then((d) => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [user]);

  function toggleEmotion(emotion) {
    setVisibleEmotions((prev) => {
      const next = new Set(prev);
      if (next.has(emotion)) { next.delete(emotion); } else { next.add(emotion); }
      return next;
    });
  }

  if (loading) {
    return (
      <div style={s.screen}>
        <div style={s.header}><h1 style={s.title}>Insights</h1></div>
        <p style={{ padding: "20px", color: "var(--text-muted)", fontSize: "13px" }}>Loading...</p>
      </div>
    );
  }

  if (!data?.has_data) {
    return (
      <div style={s.screen}>
        <div style={s.header}><h1 style={s.title}>Insights</h1></div>
        <div style={s.emptyState}>
          <p style={{ marginBottom: "8px" }}>No insights yet.</p>
          <p>Write a few journal entries and your emotional arc will appear here.</p>
        </div>
      </div>
    );
  }

  const timelineData = (data.emotion_timeline || []).map((row) => ({
    ...row,
    date: formatDateShort(row.date),
  }));

  const themeFreq = Object.entries(data.theme_frequency || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);
  const maxThemeCount = themeFreq[0]?.[1] || 1;

  return (
    <div style={s.screen}>
      <div style={s.header}>
        <h1 style={s.title}>Insights</h1>
        <p style={s.sub}>Your emotional arc over time</p>
      </div>

      {/* Arc summary */}
      {data.arc_summary && (
        <div style={s.section}>
          <div style={s.sectionLabel}>Your arc</div>
          <div style={s.card}>
            <p style={s.arcText}>{data.arc_summary}</p>
          </div>
        </div>
      )}

      {/* Emotion timeline chart */}
      {timelineData.length > 0 && (
        <div style={s.section}>
          <div style={s.sectionLabel}>Emotion timeline</div>
          <div style={s.card}>
            {/* Tap-to-toggle legend */}
            <div style={s.legendRow}>
              {INTEGRA_EMOTIONS.map((emotion) => (
                <button
                  key={emotion}
                  onClick={() => toggleEmotion(emotion)}
                  style={{
                    ...s.legendItem,
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                    opacity: visibleEmotions.has(emotion) ? 1 : 0.3,
                    padding: 0,
                    fontFamily: "var(--font-body)",
                    transition: "opacity 0.15s ease",
                  }}
                >
                  <div style={{ ...s.legendDot, background: EMOTION_COLORS[emotion] }} />
                  {emotion}
                </button>
              ))}
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={timelineData} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={[0, 1]}
                  tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                />
                <Tooltip content={<CustomTooltip />} />
                {INTEGRA_EMOTIONS.filter((e) => visibleEmotions.has(e)).map((emotion) => (
                  <Line
                    key={emotion}
                    type="monotone"
                    dataKey={emotion}
                    stroke={EMOTION_COLORS[emotion]}
                    strokeWidth={1.8}
                    dot={{ r: 3, fill: EMOTION_COLORS[emotion], strokeWidth: 0 }}
                    activeDot={{ r: 5 }}
                    connectNulls
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Theme frequency */}
      {themeFreq.length > 0 && (
        <div style={s.section}>
          <div style={s.sectionLabel}>Recurring themes</div>
          <div style={s.card}>
            <div style={s.themeRow}>
              {themeFreq.map(([theme, count]) => (
                <div key={theme} style={s.themeItem}>
                  <span style={s.themeLabel}>{theme}</span>
                  <div style={s.themeBar}>
                    <div style={{
                      height: "100%",
                      width: `${(count / maxThemeCount) * 100}%`,
                      background: "var(--accent)",
                      borderRadius: "2px",
                    }} />
                  </div>
                  <span style={s.themeCount}>{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
