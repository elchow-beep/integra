import { useLocation, useNavigate } from "react-router-dom";

/**
 * BottomNav.jsx
 *
 * Persistent bottom tab bar -- the primary navigation pattern from the UX proposal.
 * Four tabs: Home, Journal, Insights, Indy (Companion).
 */

const TABS = [
  {
    path: "/home",
    label: "Home",
    icon: (active) => (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={active ? "var(--accent)" : "var(--text-muted)"} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/>
        <path d="M9 21V12h6v9"/>
      </svg>
    ),
  },
  {
    path: "/journal",
    label: "Journal",
    icon: (active) => (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={active ? "var(--accent)" : "var(--text-muted)"} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <rect x="4" y="2" width="16" height="20" rx="2"/>
        <path d="M8 7h8M8 11h8M8 15h5"/>
      </svg>
    ),
  },
  {
    path: "/insights",
    label: "Insights",
    icon: (active) => (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={active ? "var(--accent)" : "var(--text-muted)"} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 17l4-6 4 4 4-7 4 5"/>
        <path d="M3 21h18"/>
      </svg>
    ),
  },
  {
    path: "/companion",
    label: "Indy",
    icon: (active) => (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={active ? "var(--accent)" : "var(--text-muted)"} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
    ),
  },
];

const styles = {
  nav: {
    position: "fixed",
    bottom: 0,
    left: 0,
    right: 0,
    height: "64px",
    background: "var(--surface)",
    borderTop: "1px solid var(--border)",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-around",
    padding: "0 8px",
    zIndex: 100,
    // Safe area for phones with home indicator
    paddingBottom: "env(safe-area-inset-bottom)",
  },
  tab: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "3px",
    cursor: "pointer",
    padding: "8px 0",
    border: "none",
    background: "transparent",
    fontFamily: "var(--font-body)",
    transition: "opacity 0.15s ease",
  },
  label: {
    fontSize: "10px",
    fontWeight: 500,
    letterSpacing: "0.04em",
  },
};

export default function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav style={styles.nav}>
      {TABS.map((tab) => {
        const active = location.pathname === tab.path;
        return (
          <button
            key={tab.path}
            style={styles.tab}
            onClick={() => navigate(tab.path)}
          >
            {tab.icon(active)}
            <span style={{ ...styles.label, color: active ? "var(--accent)" : "var(--text-muted)" }}>
              {tab.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
