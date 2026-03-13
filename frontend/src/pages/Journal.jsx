import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEntries, createEntry, deleteEntry } from "../api.js";
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

const ANALYZING_PHRASES = [
  "Reading your entry...",
  "Detecting emotions...",
  "Extracting themes...",
  "Finding practices...",
  "Almost there...",
];

function useAnalyzingPhrase(active) {
  const [index, setIndex] = useState(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!active) {
      setIndex(0);
      clearInterval(intervalRef.current);
      return;
    }
    intervalRef.current = setInterval(() => {
      setIndex((i) => (i + 1) % ANALYZING_PHRASES.length);
    }, 2200);
    return () => clearInterval(intervalRef.current);
  }, [active]);

  return ANALYZING_PHRASES[index];
}

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
  // Delete
  swipeWrapper: {
    position: "relative",
    overflow: "hidden",
    borderRadius: "var(--radius-md)",
  },
  swipeDelete: {
    position: "absolute",
    top: 0, right: 0, bottom: 0,
    width: "72px",
    background: "#a67b7b",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    borderRadius: "0 var(--radius-md) var(--radius-md) 0",
  },
  deleteIconBtn: {
    background: "transparent",
    border: "none",
    cursor: "pointer",
    padding: "4px",
    color: "var(--text-muted)",
    display: "flex",
    alignItems: "center",
    lineHeight: 1,
  },
  // Confirmation sheet
  sheetTitle: {
    fontFamily: "var(--font-display)",
    fontSize: "20px",
    color: "var(--text-primary)",
    marginBottom: "8px",
  },
  sheetBody: {
    fontSize: "13px",
    fontWeight: 300,
    color: "var(--text-muted)",
    lineHeight: 1.6,
    marginBottom: "24px",
  },
  destructiveBtn: {
    background: "#a67b7b",
    border: "none",
    borderRadius: "10px",
    padding: "14px",
    fontSize: "14px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    width: "100%",
    marginBottom: "10px",
  },
};

function TrashIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14H6L5 6" />
      <path d="M10 11v6M14 11v6" />
      <path d="M9 6V4h6v2" />
    </svg>
  );
}

function DeleteConfirmSheet({ onConfirm, onCancel, deleting }) {
  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 400,
      display: "flex", flexDirection: "column", justifyContent: "flex-end",
    }}>
      <div
        style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.5)" }}
        onClick={onCancel}
      />
      <div style={{
        position: "relative",
        background: "var(--surface)",
        borderRadius: "20px 20px 0 0",
        padding: "28px 20px 88px",
        borderTop: "1px solid var(--border)",
      }}>
        <div style={{ width: "36px", height: "4px", borderRadius: "2px", background: "var(--border)", margin: "0 auto 24px" }} />
        <div style={s.sheetTitle}>Delete this entry?</div>
        <div style={s.sheetBody}>This can't be undone. The entry and its analysis will be permanently removed.</div>
        <button
          style={{ ...s.destructiveBtn, opacity: deleting ? 0.6 : 1 }}
          onClick={onConfirm}
          disabled={deleting}
        >
          {deleting ? "Deleting..." : "Delete entry"}
        </button>
        <button style={s.ghostBtn} onClick={onCancel}>Cancel</button>
      </div>
    </div>
  );
}

function EntryCard({ entry, firstEntryDate, onDelete }) {
  const weekNum = entry.week_number || getWeekNumber(entry.date, firstEntryDate);
  const [expanded, setExpanded] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [swipeX, setSwipeX] = useState(0);
  const touchStartX = useRef(null);

  const topEmotions = Object.entries(entry.emotions || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  function handleTouchStart(e) {
    touchStartX.current = e.touches[0].clientX;
  }

  function handleTouchMove(e) {
    if (touchStartX.current === null || expanded) return;
    const dx = e.touches[0].clientX - touchStartX.current;
    if (dx < 0) setSwipeX(Math.max(dx, -72));
  }

  function handleTouchEnd() {
    if (swipeX < -40) {
      setSwipeX(-72);
    } else {
      setSwipeX(0);
    }
    touchStartX.current = null;
  }

  function handleConfirmDelete() {
    setDeleting(true);
    onDelete(entry.entry_id).catch(() => {
      setDeleting(false);
      setShowConfirm(false);
    });
  }

  return (
    <>
      <div style={s.swipeWrapper}>
        {/* Swipe-revealed delete zone */}
        {swipeX <= -40 && (
          <div style={s.swipeDelete} onClick={() => { setSwipeX(0); setShowConfirm(true); }}>
            <TrashIcon />
          </div>
        )}
        {/* Card */}
        <div
          style={{
            ...s.entryCard,
            borderColor: expanded ? "var(--accent)" : "var(--border)",
            transform: `translateX(${swipeX}px)`,
            transition: swipeX === 0 || swipeX === -72 ? "transform 0.2s ease" : "none",
            position: "relative",
          }}
          onClick={() => { if (swipeX !== 0) { setSwipeX(0); return; } setExpanded(!expanded); }}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
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
              {/* Delete button in expanded footer */}
              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "14px", paddingTop: "10px", borderTop: "1px solid var(--border)" }}>
                <button
                  style={s.deleteIconBtn}
                  onClick={(e) => { e.stopPropagation(); setShowConfirm(true); }}
                >
                  <TrashIcon />
                  <span style={{ marginLeft: "5px", fontSize: "11px", color: "var(--text-muted)" }}>Delete</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {showConfirm && (
        <DeleteConfirmSheet
          onConfirm={handleConfirmDelete}
          onCancel={() => setShowConfirm(false)}
          deleting={deleting}
        />
      )}
    </>
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
  const analyzingPhrase = useAnalyzingPhrase(submitting);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    getEntries(user.user_id)
      .then((data) => { setEntries(data.entries); setLoading(false); })
      .catch(() => setLoading(false));
  }, [user]);

  function handleDelete(entryId) {
    return deleteEntry(user.user_id, entryId).then(() => {
      setEntries((prev) => prev.filter((e) => e.entry_id !== entryId));
    });
  }

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
              {submitting ? analyzingPhrase : "Save entry"}
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
        <div style={s.list}>
          {[0, 1, 2].map((i) => (
            <div key={i} style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-md)",
              padding: "14px",
            }}>
              <div className="skeleton" style={{ width: "80px", height: "11px", borderRadius: "4px", marginBottom: "10px", animationDelay: `${i * 0.1}s` }} />
              <div className="skeleton" style={{ width: "65%", height: "13px", borderRadius: "4px", marginBottom: "6px", animationDelay: `${i * 0.1 + 0.05}s` }} />
              <div className="skeleton" style={{ width: "45%", height: "13px", borderRadius: "4px", marginBottom: "10px", animationDelay: `${i * 0.1 + 0.08}s` }} />
              <div style={{ display: "flex", gap: "6px" }}>
                <div className="skeleton" style={{ width: "64px", height: "20px", borderRadius: "10px", animationDelay: `${i * 0.1 + 0.1}s` }} />
                <div className="skeleton" style={{ width: "48px", height: "20px", borderRadius: "10px", animationDelay: `${i * 0.1 + 0.15}s` }} />
              </div>
            </div>
          ))}
        </div>
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
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
