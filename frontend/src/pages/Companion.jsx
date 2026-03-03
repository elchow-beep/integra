import { useState, useEffect, useRef } from "react";
import { sendMessage, resetChat } from "../api.js";

/**
 * Companion.jsx
 *
 * Chat interface for Indy, the RAG-powered integration companion.
 *
 * Features:
 *   - Disclaimer chip always visible at top
 *   - If entry context is passed from Journal, first message includes it
 *   - Crisis responses are visually distinct (amber warning card)
 *   - Auto-scrolls to latest message
 *   - Reset button clears history
 */

const s = {
  screen: {
    height: "100vh",
    background: "var(--bg)",
    display: "flex",
    flexDirection: "column",
    paddingBottom: "64px", // BottomNav height
  },
  header: {
    padding: "52px 20px 12px",
    borderBottom: "1px solid var(--border)",
    flexShrink: 0,
  },
  headerRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  title: {
    fontFamily: "var(--font-display)",
    fontSize: "22px",
    color: "var(--text-primary)",
  },
  resetBtn: {
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "7px",
    padding: "5px 12px",
    fontSize: "11px",
    color: "var(--text-muted)",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    transition: "border-color 0.15s",
  },
  disclaimer: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    background: "var(--accent-soft)",
    border: "1px solid var(--accent-border)",
    borderRadius: "5px",
    padding: "4px 10px",
    fontSize: "10px",
    color: "var(--accent)",
    fontWeight: 400,
    marginTop: "8px",
  },
  dot: {
    width: "5px",
    height: "5px",
    borderRadius: "50%",
    background: "var(--accent)",
    flexShrink: 0,
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: "16px 20px",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  bubbleWrapper: (role) => ({
    display: "flex",
    justifyContent: role === "user" ? "flex-end" : "flex-start",
  }),
  bubble: (role, crisis) => ({
    maxWidth: "82%",
    padding: "10px 14px",
    borderRadius: role === "user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
    background: crisis
      ? "rgba(196,149,106,0.12)"
      : role === "user"
        ? "var(--accent)"
        : "var(--surface)",
    color: crisis
      ? "var(--accent)"
      : role === "user"
        ? "#1c1a18"
        : "var(--text-primary)",
    border: crisis
      ? "1px solid var(--accent-border)"
      : role === "user"
        ? "none"
        : "1px solid var(--border)",
    fontSize: "13px",
    fontWeight: role === "user" ? 400 : 300,
    lineHeight: 1.65,
  }),
  crisisLabel: {
    fontSize: "9px",
    fontWeight: 500,
    letterSpacing: "0.10em",
    textTransform: "uppercase",
    color: "var(--accent)",
    marginBottom: "5px",
    opacity: 0.7,
  },
  inputArea: {
    padding: "12px 20px 16px",
    borderTop: "1px solid var(--border)",
    display: "flex",
    gap: "10px",
    flexShrink: 0,
    background: "var(--bg)",
  },
  input: {
    flex: 1,
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "10px",
    padding: "10px 14px",
    fontSize: "13px",
    color: "var(--text-primary)",
    fontFamily: "var(--font-body)",
    outline: "none",
    lineHeight: 1.5,
    resize: "none",
  },
  sendBtn: {
    background: "var(--accent)",
    border: "none",
    borderRadius: "10px",
    padding: "10px 16px",
    fontSize: "13px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    flexShrink: 0,
    alignSelf: "flex-end",
    transition: "opacity 0.15s",
  },
  typing: {
    padding: "10px 14px",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "14px 14px 14px 4px",
    fontSize: "13px",
    color: "var(--text-muted)",
    maxWidth: "82%",
  },
  emptyState: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    flex: 1,
    padding: "20px",
    textAlign: "center",
    gap: "8px",
  },
  emptyName: {
    fontFamily: "var(--font-display)",
    fontSize: "20px",
    color: "var(--text-primary)",
  },
  emptySub: {
    fontSize: "12px",
    fontWeight: 300,
    color: "var(--text-muted)",
    lineHeight: 1.6,
    maxWidth: "240px",
  },
  contextBanner: {
    margin: "0 20px 4px",
    background: "rgba(123,166,143,0.08)",
    border: "1px solid rgba(123,166,143,0.18)",
    borderRadius: "8px",
    padding: "8px 12px",
    fontSize: "11px",
    color: "#7ba68f",
    fontWeight: 400,
  },
};

export default function Companion({ user, entryContext, onContextUsed }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [contextConsumed, setContextConsumed] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Reset context consumed flag when new entry context arrives
  useEffect(() => {
    if (entryContext) setContextConsumed(false);
  }, [entryContext]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    // Use entry context on the first send if available
    const contextToSend = !contextConsumed && entryContext ? entryContext : null;
    if (contextToSend) {
      setContextConsumed(true);
      onContextUsed();
    }

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendMessage(user.user_id, text, contextToSend);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          crisis: data.crisis_detected,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong reaching the server. Please try again.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleReset() {
    if (messages.length === 0) return;
    await resetChat(user.user_id).catch(() => {});
    setMessages([]);
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div style={s.screen}>
      <div style={s.header}>
        <div style={s.headerRow}>
          <h1 style={s.title}>Indy</h1>
          <button style={s.resetBtn} onClick={handleReset}>Clear chat</button>
        </div>
        <div style={s.disclaimer}>
          <div style={s.dot} />
          Indy is an AI companion, not a therapist
        </div>
      </div>

      {entryContext && !contextConsumed && (
        <div style={s.contextBanner}>
          Entry context ready -- Indy will reflect on your entry with your first message.
        </div>
      )}

      <div style={s.messages}>
        {messages.length === 0 && (
          <div style={s.emptyState}>
            <div style={s.emptyName}>Hi, I'm Indy.</div>
            <div style={s.emptySub}>
              I'm here to support your integration. Share what's on your mind.
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={s.bubbleWrapper(msg.role)}>
            <div style={s.bubble(msg.role, msg.crisis)}>
              {msg.crisis && <div style={s.crisisLabel}>Crisis support</div>}
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div style={s.bubbleWrapper("assistant")}>
            <div style={s.typing}>Indy is thinking...</div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div style={s.inputArea}>
        <textarea
          style={s.input}
          placeholder="Message Indy..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button
          style={{ ...s.sendBtn, opacity: !input.trim() || loading ? 0.4 : 1 }}
          onClick={handleSend}
          disabled={!input.trim() || loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
