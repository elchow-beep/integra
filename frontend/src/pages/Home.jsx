import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEntries, getInsights, postCheckin } from "../api.js";
import EmotionPill from "../components/EmotionPill.jsx";
import BottomSheet from "../components/BottomSheet.jsx";

const QUICK_MOODS = [
  { label: "calm",      color: "#7ba68f" },
  { label: "awe",       color: "#7b9ea6" },
  { label: "gratitude", color: "#c4956a" },
  { label: "grief",     color: "#7a8fa6" },
  { label: "overwhelm", color: "#9b7fa6" },
  { label: "joy",       color: "#a6c47b" },
];

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

const s = {
  screen: { minHeight: "100vh", background: "var(--bg)", paddingBottom: "80px" },
  header: { padding: "52px 20px 0", display: "flex", alignItems: "center", justifyContent: "space-between" },
  brand: { fontFamily: "var(--font-display)", fontSize: "20px", color: "var(--text-primary)" },
  switchBtn: {
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    padding: "5px 12px",
    fontSize: "11px",
    color: "var(--text-muted)",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    transition: "border-color 0.15s, color 0.15s",
  },
  greeting: { padding: "20px 20px 0" },
  eyebrow: { fontSize: "11px", fontWeight: 500, letterSpacing: "0.10em", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "4px" },
  name: { fontFamily: "var(--font-display)", fontSize: "26px", color: "var(--text-primary)", marginBottom: "2px" },
  sub: { fontSize: "12px", fontWeight: 300, color: "var(--text-secondary)" },
  sectionHeader: { padding: "20px 20px 8px", display: "flex", alignItems: "center", justifyContent: "space-between" },
  sectionTitle: { fontSize: "11px", fontWeight: 500, letterSpacing: "0.10em", textTransform: "uppercase", color: "var(--text-muted)" },
  moodRow: { display: "flex", gap: "8px", padding: "0 20px", overflowX: "auto", paddingBottom: "4px" },
  moodPill: { flexShrink: 0, border: "none", borderRadius: "20px", padding: "7px 14px", fontSize: "12px", fontWeight: 500, cursor: "pointer", fontFamily: "var(--font-body)", transition: "opacity 0.15s ease, transform 0.1s ease" },
  card: { margin: "0 20px", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", padding: "16px" },
  writeCard: { margin: "0 20px", background: "var(--accent-soft)", border: "1px solid var(--accent-border)", borderRadius: "var(--radius-lg)", padding: "16px 18px", display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer", boxSizing: "border-box", transition: "border-color 0.15s ease", fontFamily: "var(--font-body)" },
  writeTitle: { fontFamily: "var(--font-display)", fontSize: "17px", color: "var(--text-primary)", marginBottom: "2px" },
  writeSub: { fontSize: "12px", fontWeight: 300, color: "var(--text-secondary)" },
  cardLabel: { fontSize: "10px", fontWeight: 500, letterSpacing: "0.10em", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "8px" },
  entryTitle: { fontSize: "13px", color: "var(--text-primary)", marginBottom: "8px", lineHeight: 1.45, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" },
  arcText: { fontSize: "13px", fontWeight: 300, color: "var(--text-secondary)", lineHeight: 1.6 },
  pillRow: { display: "flex", gap: "5px", flexWrap: "wrap", marginTop: "8px" },
  loadingRow: { padding: "32px 20px", display: "flex", flexDirection: "column", gap: "10px" },
  skeleton: { background: "var(--surface)", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", animation: "pulse 1.6s ease-in-out infinite" },
  emptyCard: { margin: "0 20px", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", padding: "20px" },
  emptyTitle: { fontFamily: "var(--font-display)", fontSize: "17px", color: "var(--text-primary)", marginBottom: "6px" },
  emptyBody: { fontSize: "12px", fontWeight: 300, color: "var(--text-secondary)", lineHeight: 1.65, marginBottom: "14px" },
  emptySteps: { display: "flex", flexDirection: "column", gap: "8px" },
  emptyStep: { display: "flex", alignItems: "flex-start", gap: "10px" },
  stepNum: { flexShrink: 0, width: "20px", height: "20px", borderRadius: "50%", background: "var(--accent-soft)", border: "1px solid var(--accent-border)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "10px", fontWeight: 500, color: "var(--accent)", marginTop: "1px" },
  stepText: { fontSize: "12px", fontWeight: 300, color: "var(--text-secondary)", lineHeight: 1.55 },
  // bottom sheet styles
  sheetEmotion: (color) => ({
    display: "inline-block",
    padding: "4px 14px",
    borderRadius: "20px",
    fontSize: "13px",
    fontWeight: 500,
    background: `${color}22`,
    border: `1px solid ${color}55`,
    color: color,
    marginBottom: "10px",
    textTransform: "capitalize",
  }),
  sheetTitle: { fontFamily: "var(--font-display)", fontSize: "20px", color: "var(--text-primary)", marginBottom: "6px" },
  sheetSub: { fontSize: "12px", fontWeight: 300, color: "var(--text-secondary)" },
  sheetBtns: { display: "flex", flexDirection: "column", gap: "10px", marginTop: "20px" },
  primaryBtn: {
    background: "var(--accent)",
    border: "none",
    borderRadius: "10px",
    padding: "13px 16px",
    fontSize: "13px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    letterSpacing: "0.02em",
  },
  ghostBtn: (muted) => ({
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "10px",
    padding: "13px 16px",
    fontSize: "13px",
    fontWeight: 400,
    color: muted ? "var(--calm, #7ba68f)" : "var(--text-secondary)",
    cursor: muted ? "default" : "pointer",
    fontFamily: "var(--font-body)",
    transition: "color 0.2s",
  }),
};

function SkeletonBlock({ height }) {
  return <div style={{ ...s.skeleton, height: height || "56px" }} />;
}

export default function Home({ user, onSwitchProfile }) {
  const navigate = useNavigate();
  const [recentEntry, setRecentEntry]     = useState(null);
  const [arcSummary, setArcSummary]       = useState(null);
  const [dataLoaded, setDataLoaded]       = useState(false);
  const [tappedMood, setTappedMood]       = useState(null);

  // check-in sheet state
  const [sheetOpen, setSheetOpen]         = useState(false);
  const [checkinEmotion, setCheckinEmotion] = useState(null);
  const [checkinStatus, setCheckinStatus] = useState(null); // null | "logging" | "done"

  const today = new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });

  useEffect(() => {
    if (!user || user.user_id === "guest") {
      setDataLoaded(true);
      return;
    }
    setDataLoaded(false);
    let entriesDone = false;
    let insightsDone = false;

    function checkDone() {
      if (entriesDone && insightsDone) setDataLoaded(true);
    }

    getEntries(user.user_id)
      .then((data) => { if (data.entries.length > 0) setRecentEntry(data.entries[0]); })
      .catch(() => {})
      .finally(() => { entriesDone = true; checkDone(); });

    getInsights(user.user_id)
      .then((data) => { if (data.has_data) setArcSummary(data.arc_summary); })
      .catch(() => {})
      .finally(() => { insightsDone = true; checkDone(); });
  }, [user]);

  function handleMoodTap(mood) {
    setCheckinEmotion(mood);
    setCheckinStatus(null);
    setTappedMood(mood);
    setSheetOpen(true);
  }

  function handleSheetClose() {
    setSheetOpen(false);
    setTappedMood(null);
  }

  async function handleJustLog() {
    if (!user || user.user_id === "guest") return;
    setCheckinStatus("logging");
    try {
      await postCheckin(user.user_id, checkinEmotion);
      setCheckinStatus("done");
      setTimeout(() => {
        setSheetOpen(false);
        setTappedMood(null);
        setCheckinStatus(null);
      }, 1200);
    } catch {
      setCheckinStatus(null);
    }
  }

  function handleChatWithIndy() {
    setSheetOpen(false);
    setTappedMood(null);
    navigate("/companion", { state: { checkinEmotion } });
  }

  const selectedMoodColor = QUICK_MOODS.find((m) => m.label === checkinEmotion)?.color || "var(--accent)";
  const hasHistory = recentEntry || arcSummary;

  return (
    <div style={s.screen}>
      <style>{`@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.45; } }`}</style>

      <div style={s.header}>
        <span style={s.brand}>Integra</span>
        <button style={s.switchBtn} onClick={onSwitchProfile}>Switch profile</button>
      </div>

      <div style={s.greeting}>
        <div style={s.eyebrow}>{today}</div>
        <div style={s.name}>{greeting()}, {user?.display_name}.</div>
        <div style={s.sub}>How are you feeling today?</div>
      </div>

      <div style={s.sectionHeader}><span style={s.sectionTitle}>Quick check-in</span></div>
      <div style={s.moodRow}>
        {QUICK_MOODS.map((m) => (
          <button
            key={m.label}
            style={{
              ...s.moodPill,
              background: `${m.color}18`,
              color: m.color,
              border: `1px solid ${m.color}30`,
              transform: tappedMood === m.label ? "scale(0.94)" : "scale(1)",
              opacity: tappedMood && tappedMood !== m.label ? 0.4 : 1,
            }}
            onClick={() => handleMoodTap(m.label)}
          >
            {m.label}
          </button>
        ))}
      </div>

      <div style={s.sectionHeader}><span style={s.sectionTitle}>Today</span></div>
      <button style={s.writeCard} onClick={() => navigate("/journal")}>
        <div>
          <div style={s.writeTitle}>Write an entry</div>
          <div style={s.writeSub}>Reflect on your integration</div>
        </div>
        <span style={{ fontSize: "20px", color: "var(--accent)" }}>+</span>
      </button>

      {!dataLoaded && (
        <div style={s.loadingRow}>
          <SkeletonBlock height="72px" />
          <SkeletonBlock height="56px" />
        </div>
      )}

      {dataLoaded && hasHistory && (
        <>
          {recentEntry && (
            <>
              <div style={s.sectionHeader}>
                <span style={s.sectionTitle}>Last entry</span>
                <span style={{ fontSize: "11px", color: "var(--accent)", cursor: "pointer" }} onClick={() => navigate("/journal")}>All entries</span>
              </div>
              <div style={{ ...s.card, cursor: "pointer" }} onClick={() => navigate("/journal")}>
                <div style={s.cardLabel}>{formatDate(recentEntry.date)}</div>
                <div style={s.entryTitle}>{recentEntry.text}</div>
                {recentEntry.emotions && (
                  <div style={s.pillRow}>
                    {Object.entries(recentEntry.emotions).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([emotion, score]) => (
                      <EmotionPill key={emotion} emotion={emotion} score={score} />
                    ))}
                  </div>
                )}
              </div>
            </>
          )}

          {arcSummary && (
            <>
              <div style={s.sectionHeader}>
                <span style={s.sectionTitle}>Your arc</span>
                <span style={{ fontSize: "11px", color: "var(--accent)", cursor: "pointer" }} onClick={() => navigate("/insights")}>Full insights</span>
              </div>
              <div style={s.card}><div style={s.arcText}>{arcSummary}</div></div>
            </>
          )}
        </>
      )}

      {dataLoaded && !hasHistory && (
        <>
          <div style={s.sectionHeader}><span style={s.sectionTitle}>Getting started</span></div>
          <div style={s.emptyCard}>
            <div style={s.emptyTitle}>Welcome to Integra.</div>
            <div style={s.emptyBody}>
              This is your integration space. Write your first entry and Integra will start tracking your emotional arc over time.
            </div>
            <div style={s.emptySteps}>
              <div style={s.emptyStep}>
                <div style={s.stepNum}>1</div>
                <div style={s.stepText}>Write a journal entry about what you're processing -- no structure needed, just write.</div>
              </div>
              <div style={s.emptyStep}>
                <div style={s.stepNum}>2</div>
                <div style={s.stepText}>Integra detects emotions and themes from your text automatically.</div>
              </div>
              <div style={s.emptyStep}>
                <div style={s.stepNum}>3</div>
                <div style={s.stepText}>After a few entries, your emotional arc appears here and on the Insights page.</div>
              </div>
            </div>
          </div>
        </>
      )}

      <BottomSheet isOpen={sheetOpen} onClose={handleSheetClose}>
        <div style={{ textAlign: "center", marginBottom: "4px" }}>
          <div style={s.sheetEmotion(selectedMoodColor)}>{checkinEmotion}</div>
          <div style={s.sheetTitle}>How do you want to sit with this?</div>
          <div style={s.sheetSub}>Log it quietly or open it up with Indy.</div>
        </div>
        <div style={s.sheetBtns}>
          <button style={s.primaryBtn} onClick={handleChatWithIndy}>
            Chat with Indy
          </button>
          <button
            style={s.ghostBtn(checkinStatus === "done")}
            onClick={handleJustLog}
            disabled={checkinStatus !== null}
          >
            {checkinStatus === "logging" && "Logging..."}
            {checkinStatus === "done"    && "Logged"}
            {checkinStatus === null      && "Just log it"}
          </button>
        </div>
      </BottomSheet>
    </div>
  );
}
