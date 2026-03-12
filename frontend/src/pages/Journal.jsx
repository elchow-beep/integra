import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEntries, createEntry } from "../api.js";
import EmotionPill from "../components/EmotionPill.jsx";

/**
 * Journal.jsx
 *
 * Two modes:
 *   "browse" -- scrollable list of past entries, each expandable
 *   "write"  -- full-screen text entry form with live submit
 *
 * After submitting an entry, analysis results (emotions, themes,
 * recommendations) are shown inline before returning to browse mode.
 * A "Reflect with Indy" button navigates to Companion with entry context.
 */

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function getWeekNumber(entryDateStr, firstEntryDateStr) {
  if (!entryDateStr || !firstEntryDateStr) return null;
  const entry = new Date(entryDateStr + "T00:00:00");
  const first = new Date(firstEntryDateStr + "T00:00:00");
  const diffDays = Math.floor((entry - first) / (1000 * 60 * 60 * 24));
  return Math.floor(diffDays / 7) + 1;
}

const s = {
  screen: {
    minHeight: "100vh",
    background: "var(--bg)",
    paddingBottom: "80px",
  },
  header: {
    padding: "52px 20px 0",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  title: {
    fontFamily: "var(--font-display)",
    fontSize: "24px",
    color: "var(--text-primary)",
  },
  newBtn: {
    background: "var(--accent)",
    border: "none",
    borderRadius: "10px",
    padding: "8px 16px",
    fontSize: "13px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    letterSpacing: "0.02em",
  },
  list: {
    padding: "20px 20px 0",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  entryCard: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-md)",
    padding: "14px",
    cursor: "pointer",
    transition: "border-color 0.15s ease",
  },
  entryDate: {
    fontSize: "11px",
    color: "var(--text-muted)",
    marginBottom: "5px",
  },
  entryPreview: {
    fontSize: "13px",
    color: "var(--text-primary)",
    lineHeight: 1.5,
    marginBottom: "8px",
  },
  pillRow: {
    display: "flex",
    gap: "5px",
    flexWrap: "wrap",
  },
  expandedBody: {
    marginTop: "12px",
    paddingTop: "12px",
    borderTop: "1px solid var(--border)",
  },
  expandedText: {
    fontSize: "13px",
    fontWeight: 300,
    color: "var(--text-secondary)",
    lineHeight: 1.7,
    marginBottom: "12px",
    whiteSpace: "pre-wrap",
  },
  sectionLabel: {
    fontSize: "10px",
    fontWeight: 500,
    letterSpacing: "0.10em",
    textTransform: "uppercase",
    color: "var(--text-muted)",
    marginBottom: "6px",
    marginTop: "12px",
  },
  themeChip: {
    fontSize: "11px",
    padding: "2px 8px",
    borderRadius: "4px",
    background: "var(--surface-raised)",
    color: "var(--text-secondary)",
    border: "1px solid var(--border)",
  },
  recItem: {
    fontSize: "12px",
    fontWeight: 300,
    color: "var(--text-secondary)",
    padding: "6px 0",
    borderBottom: "1px solid var(--border)",
    lineHeight: 1.4,
  },
  // Write mode
  writeScreen: {
    minHeight: "100vh",
    background: "var(--bg)",
    padding: "52px 20px 100px",
    display: "flex",
    flexDirection: "column",
  },
  writeHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: "24px",
  },
  backBtn: {
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    padding: "7px 14px",
    fontSize: "12px",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
  },
  writeTitle: {
    fontFamily: "var(--font-display)",
    fontSize: "22px",
    color: "var(--text-primary)",
    marginBottom: "4px",
  },
  writeSub: {
    fontSize: "12px",
    fontWeight: 300,
    color: "var(--text-muted)",
    marginBottom: "20px",
  },
  textarea: {
    width: "100%",
    flex: 1,
    minHeight: "220px",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-md)",
    padding: "16px",
    fontSize: "14px",
    fontWeight: 300,
    color: "var(--text-primary)",
    fontFamily: "var(--font-body)",
    lineHeight: 1.7,
    resize: "vertical",
    outline: "none",
    marginBottom: "16px",
  },
  submitBtn: {
    background: "var(--accent)",
    border: "none",
    borderRadius: "10px",
    padding: "14px",
    fontSize: "14px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    letterSpacing: "0.02em",
    width: "100%",
  },
  ghostBtn: {
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "10px",
    padding: "14px",
    fontSize: "14px",
    fontWeight: 400,
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    width: "100%",
    marginTop: "10px",
    transition: "border-color 0.15s, color 0.15s",
  },
  resultCard: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-lg)",
    padding: "18px",
    marginBottom: "16px",
  },
  emptyState: {
    margin: "32px 20px 0",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-lg)",
    padding: "28px 20px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    textAlign: "center",
    gap: "8px",
  },
  emptyTitle: {
    fontFamily: "var(--font-display)",
    fontSize: "18px",
    color: "var(--text-primary)",
  },
  emptyBody: {
    fontSize: "12px",
    fontWeight: 300,
    color: "var(--text-muted)",
    lineHeight: 1.65,
    maxWidth: "240px",
  },
  emptyBtn: {
    marginTop: "8px",
    background: "var(--accent)",
    border: "none",
    borderRadius: "10px",
    padding: "10px 20px",
    fontSize: "13px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
  },
};

function EntryCard({ entry, firstEntryDate }) {
  const weekNum = entry.week_number || getWeekNumber(entry.date, firstEntryDate);
  const [expanded, setExpanded] = useState(false);
  const topEmotions = Object.entries(entry.emotions || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  return (
    <div
      style={{ ...s.entryCard, borderColor: expanded ? "var(--accent)" : "var(--border)" }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={s.entryDate}>{formatDate(entry.date)}{weekNum ? ` · Week ${weekNum}` : ""}</div>
      <div style={{ ...s.entryPreview, display: "-webkit-box", WebkitLineClamp: expanded ? "none" : 2, WebkitBoxOrient: "vertical", overflow: expanded ? "visible" : "hidden" }}>
        {entry.text}
      </div>
      <div style={s.pillRow}>
        {topEmotions.map(([emotion, score]) => (
          <EmotionPill key={emotion} emotion={emotion} score={score} />
        ))}
      </div>

      {expanded && (
        <div style={s.expandedBody}>
          {entry.themes?.length > 0 && (
            <>
              <div style={s.sectionLabel}>Themes</div>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                {entry.themes.map((t) => <span key={t} style={s.themeChip}>{t}</span>)}
              </div>
            </>
          )}
          {entry.recommendations?.length > 0 && (
            <>
              <div style={s.sectionLabel}>Suggested practices</div>
              {entry.recommendations.map((r, i) => (
                <div key={i} style={s.recItem}>{r}</div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default function Journal({ user, onEntrySubmitted }) {
  const navigate = useNavigate();
  const [mode, setMode] = useState("browse");
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [submittedText, setSubmittedText] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    getEntries(user.user_id)
      .then((data) => { setEntries(data.entries); setLoading(false); })
      .catch(() => setLoading(false));
  }, [user]);

  function handleSubmit() {
    if (!text.trim()) return;
    setSubmitting(true);
    setError(null);
    const entryText = text.trim();
    createEntry(user.user_id, entryText)
      .then((data) => {
        setResult(data.entry);
        setSubmittedText(entryText);
        setEntries((prev) => [data.entry, ...prev]);
        onEntrySubmitted(entryText);
        setSubmitting(false);
      })
      .catch((err) => {
        setError(err.message);
        setSubmitting(false);
      });
  }

  function handleReflectWithIndy() {
    // Entry context was already set via onEntrySubmitted -- just navigate
    navigate("/companion");
  }

  function handleBackToBrowse() {
    setMode("browse");
    setResult(null);
    setText("");
    setSubmittedText("");
  }

  if (mode === "write") {
    return (
      <div style={s.writeScreen}>
        <div style={s.writeHeader}>
          <button style={s.backBtn} onClick={handleBackToBrowse}>Back</button>
          <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
            {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric" })}
          </span>
        </div>

        {result ? (
          <>
            <div style={s.writeTitle}>Entry saved.</div>
            <div style={s.writeSub}>Here's what Integra found.</div>

            <div style={s.resultCard}>
              <div style={s.sectionLabel}>Emotions detected</div>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "16px" }}>
                {Object.entries(result.emotions || {})
                  .sort((a, b) => b[1] - a[1])
                  .map(([emotion, score]) => (
                    <EmotionPill key={emotion} emotion={emotion} score={score} size="md" />
                  ))}
              </div>

              {result.themes?.length > 0 && (
                <>
                  <div style={s.sectionLabel}>Themes</div>
                  <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "16px" }}>
                    {result.themes.map((t) => <span key={t} style={s.themeChip}>{t}</span>)}
                  </div>
                </>
              )}

              {result.recommendations?.length > 0 && (
                <>
                  <div style={s.sectionLabel}>Suggested practices</div>
                  {result.recommendations.map((r, i) => (
                    <div key={i} style={s.recItem}>{r}</div>
                  ))}
                </>
              )}
            </div>

            <button style={s.submitBtn} onClick={handleReflectWithIndy}>
              Reflect with Indy
            </button>
            <button style={s.ghostBtn} onClick={handleBackToBrowse}>
              Back to journal
            </button>
          </>
        ) : (
          <>
            <div style={s.writeTitle}>Today's entry</div>
            <div style={s.writeSub}>Write freely. There's no right way.</div>

            <textarea
              style={s.textarea}
              placeholder="What's coming up for you today..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              autoFocus
            />

            {error && (
              <p style={{ color: "#a67b7b", fontSize: "12px", marginBottom: "12px" }}>{error}</p>
            )}

            <button
              style={{ ...s.submitBtn, opacity: submitting || !text.trim() ? 0.5 : 1 }}
              onClick={handleSubmit}
              disabled={submitting || !text.trim()}
            >
              {submitting ? "Analyzing..." : "Save entry"}
            </button>
          </>
        )}
      </div>
    );
  }

  return (
    <div style={s.screen}>
      <div style={s.header}>
        <h1 style={s.title}>Journal</h1>
        <button style={s.newBtn} onClick={() => setMode("write")}>+ New entry</button>
      </div>

      {loading && (
        <p style={{ color: "var(--text-muted)", fontSize: "13px", padding: "20px" }}>Loading entries...</p>
      )}

      {!loading && entries.length === 0 && (
        <div style={s.emptyState}>
          <div style={s.emptyTitle}>No entries yet.</div>
          <div style={s.emptyBody}>
            Write your first entry and Integra will detect emotions and themes from your text automatically.
          </div>
          <button style={s.emptyBtn} onClick={() => setMode("write")}>
            Write your first entry
          </button>
        </div>
      )}

      {!loading && entries.length > 0 && (
        <div style={s.list}>
          {entries.map((entry) => (
            <EntryCard
              key={entry.entry_id}
              entry={entry}
              firstEntryDate={entries[entries.length - 1]?.date}
            />
          ))}
        </div>
      )}
    </div>
  );
}
