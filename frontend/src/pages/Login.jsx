import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUsers } from "../api.js";
import LogoUrl from "../assets/logo.svg";

const AVATAR_COLORS = [
  { bg: "rgba(122,143,166,0.15)", color: "#7a8fa6" },
  { bg: "rgba(196,149,106,0.15)", color: "#c4956a" },
];

const s = {
  screen: {
    minHeight: "100vh",
    background: "var(--bg)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "60px 24px 40px",
  },
  wordmark: {
    fontFamily: "var(--font-display)",
    fontSize: "28px",
    color: "var(--text-primary)",
    letterSpacing: "-0.01em",
    marginBottom: "6px",
    marginTop: "16px",
  },
  subtitle: {
    fontSize: "12px",
    fontWeight: 300,
    color: "var(--text-muted)",
    textAlign: "center",
    marginBottom: "36px",
    lineHeight: 1.5,
  },
  cardsWrapper: {
    width: "100%",
    maxWidth: "320px",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    marginBottom: "16px",
  },
  card: (selected, hovered) => ({
    background: selected ? "var(--surface-raised)" : "var(--surface)",
    border: `1px solid ${selected ? "var(--accent)" : hovered ? "var(--text-muted)" : "var(--border)"}`,
    borderRadius: "var(--radius-lg)",
    padding: "14px",
    display: "flex",
    alignItems: "center",
    gap: "12px",
    cursor: "pointer",
    width: "100%",
    transition: "border-color 0.15s, background 0.15s",
    fontFamily: "var(--font-body)",
    textAlign: "left",
  }),
  avatar: (color) => ({
    width: "40px",
    height: "40px",
    borderRadius: "10px",
    background: color.bg,
    color: color.color,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "16px",
    fontFamily: "var(--font-display)",
    flexShrink: 0,
  }),
  cardName: { fontSize: "14px", fontWeight: 500, color: "var(--text-primary)", marginBottom: "2px" },
  cardBlurb: { fontSize: "11px", fontWeight: 300, color: "var(--text-secondary)", lineHeight: 1.4 },
  badge: (selected) => ({
    fontSize: "10px",
    fontWeight: 500,
    color: selected ? "var(--accent)" : "var(--text-muted)",
    background: selected ? "var(--accent-soft)" : "var(--surface-raised)",
    border: `1px solid ${selected ? "var(--accent-border)" : "var(--border)"}`,
    borderRadius: "4px",
    padding: "2px 7px",
    flexShrink: 0,
    marginLeft: "auto",
    transition: "all 0.15s",
  }),
  primaryBtn: (enabled) => ({
    width: "100%",
    maxWidth: "320px",
    background: "var(--accent)",
    border: "none",
    borderRadius: "10px",
    padding: "13px",
    fontSize: "13px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: enabled ? "pointer" : "default",
    fontFamily: "var(--font-body)",
    letterSpacing: "0.02em",
    opacity: enabled ? 1 : 0.35,
    transition: "opacity 0.15s",
    marginBottom: "14px",
  }),
  dividerRow: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    width: "100%",
    maxWidth: "320px",
    marginBottom: "14px",
  },
  dividerLine: { flex: 1, height: "1px", background: "var(--border)" },
  dividerText: { fontSize: "11px", color: "var(--text-muted)" },
  ghostBtn: {
    width: "100%",
    maxWidth: "320px",
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "10px",
    padding: "12px",
    fontSize: "12px",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    transition: "border-color 0.15s, color 0.15s",
    marginBottom: "20px",
  },
  disclaimer: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    background: "var(--accent-soft)",
    border: "1px solid var(--accent-border)",
    borderRadius: "6px",
    padding: "6px 12px",
    fontSize: "11px",
    color: "var(--accent)",
    fontWeight: 400,
  },
  dot: {
    width: "5px",
    height: "5px",
    borderRadius: "50%",
    background: "var(--accent)",
    flexShrink: 0,
  },
};

export default function Login({ onSelectUser }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [hoveredId, setHoveredId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getUsers()
      .then((data) => { setUsers(data.users); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, []);

  const selectedUser = users.find((u) => u.user_id === selectedId);

  function handleContinue() {
    if (!selectedUser) return;
    onSelectUser(selectedUser);
    navigate("/home");
  }

  function handleGuest() {
    onSelectUser({ user_id: "guest", display_name: "Guest", entry_count: 0 });
    navigate("/companion");
  }

  return (
    <div style={s.screen}>
      <img src={LogoUrl} width={54} height={54} alt="Integra logo" />
      <h1 style={s.wordmark}>Integra</h1>
      <p style={s.subtitle}>Your integration companion.<br />Choose a profile to begin.</p>

      <div style={s.cardsWrapper}>
        {loading && (
          <p style={{ color: "var(--text-muted)", fontSize: "13px", textAlign: "center" }}>Loading...</p>
        )}
        {error && (
          <p style={{ color: "#a67b7b", fontSize: "13px", textAlign: "center" }}>
            Could not reach backend on port 8000.
          </p>
        )}
        {users.map((user, i) => {
          const av = AVATAR_COLORS[i % AVATAR_COLORS.length];
          const selected = selectedId === user.user_id;
          const hovered = hoveredId === user.user_id;
          return (
            <button
              key={user.user_id}
              style={s.card(selected, hovered)}
              onClick={() => setSelectedId(user.user_id)}
              onMouseEnter={() => setHoveredId(user.user_id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              <div style={s.avatar(av)}>{user.display_name.charAt(0)}</div>
              <div style={{ flex: 1 }}>
                <div style={s.cardName}>{user.display_name}</div>
                <div style={s.cardBlurb}>{user.context_blurb}</div>
              </div>
              <div style={s.badge(selected)}>
                {user.entry_count === 0 ? "new" : `${user.entry_count} entries`}
              </div>
            </button>
          );
        })}
      </div>

      <button style={s.primaryBtn(!!selectedUser)} onClick={handleContinue} disabled={!selectedUser}>
        Continue to Journal
      </button>

      <div style={s.dividerRow}>
        <div style={s.dividerLine} />
        <span style={s.dividerText}>or</span>
        <div style={s.dividerLine} />
      </div>

      <button style={s.ghostBtn} onClick={handleGuest}>
        Chat with Indy as a guest
      </button>

      <div style={s.disclaimer}>
        <div style={s.dot} />
        Indy is an AI companion, not a therapist
      </div>
    </div>
  );
}
