import { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { sendMessage, resetChat, createEntry } from "../api.js";

/**
 * Companion.jsx
 *
 * Chat interface for Indy, the RAG-powered integration companion.
 *
 * Features:
 *   - Disclaimer chip always visible at top
 *   - If entry context is passed from Journal, first message includes it
 *   - If checkinEmotion is passed via router state, Indy opens with a
 *     targeted prompt on mount
 *   - Crisis responses are visually distinct (amber warning card)
 *   - Crisis response has a brief thinking delay so it feels considered
 *   - Crisis response shows a tappable 988 call button
 *   - Auto-scrolls to latest message
 *   - Reset button requires confirmation before clearing
 *   - Guest mode shows a welcome message on first load
 *   - Thinking state shows rotating phrases instead of static text
 *   - After 3 user messages in a checkin flow, a "Save as journal entry"
 *     banner appears above the input
 */

const THINKING_PHRASES = [
  "Sitting with what you shared...",
  "Holding this with you...",
  "Taking a moment with this...",
  "Letting that land...",
  "Reflecting on what you've shared...",
];

function randomThinkingPhrase() {
  return THINKING_PHRASES[Math.floor(Math.random() * THINKING_PHRASES.length)];
}

const SAVE_BANNER_THRESHOLD = 3;

const s = {
  screen: {
    height: "100vh",
    background: "var(--bg)",
    display: "flex",
    flexDirection: "column",
    paddingBottom: "64px",
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
  confirmBanner: {
    margin: "0 20px",
    background: "rgba(166,123,123,0.08)",
    border: "1px solid rgba(166,123,123,0.25)",
    borderRadius: "8px",
    padding: "10px 14px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "12px",
    flexShrink: 0,
  },
  confirmText: {
    fontSize: "12px",
    fontWeight: 300,
    color: "#c49090",
  },
  confirmBtns: {
    display: "flex",
    gap: "8px",
    flexShrink: 0,
  },
  confirmYes: {
    background: "rgba(166,123,123,0.2)",
    border: "1px solid rgba(166,123,123,0.35)",
    borderRadius: "6px",
    padding: "4px 10px",
    fontSize: "11px",
    fontWeight: 500,
    color: "#d4a4a4",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
  },
  confirmNo: {
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "6px",
    padding: "4px 10px",
    fontSize: "11px",
    color: "var(--text-muted)",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
  },
  saveBanner: {
    margin: "0 16px 8px",
    background: "var(--surface-raised)",
    border: "1px solid var(--border)",
    borderRadius: "10px",
    padding: "10px 14px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "12px",
    flexShrink: 0,
  },
  saveBannerText: {
    fontSize: "12px",
    fontWeight: 300,
    color: "var(--text-secondary)",
    lineHeight: 1.4,
  },
  saveBannerBtns: {
    display: "flex",
    gap: "8px",
    flexShrink: 0,
  },
  saveBtn: {
    background: "var(--accent)",
    border: "none",
    borderRadius: "7px",
    padding: "5px 12px",
    fontSize: "11px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
  },
  dismissBtn: {
    background: "transparent",
    border: "none",
    fontSize: "11px",
    color: "var(--text-muted)",
    cursor: "pointer",
    padding: "4px 8px",
    fontFamily: "var(--font-body)",
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
  callBtn: {
    display: "block",
    marginTop: "10px",
    background: "var(--accent)",
    border: "none",
    borderRadius: "8px",
    padding: "8px 14px",
    fontSize: "12px",
    fontWeight: 500,
    color: "#1c1a18",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    textDecoration: "none",
    textAlign: "center",
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
    fontWeight: 300,
    fontStyle: "italic",
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
    maxWidth: "260px",
  },
  guestNote: {
    marginTop: "12px",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    padding: "10px 14px",
    fontSize: "11px",
    fontWeight: 300,
    color: "var(--text-secondary)",
    lineHeight: 1.6,
    maxWidth: "260px",
    textAlign: "left",
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
  const location = useLocation();
  const checkinEmotion = location.state?.checkinEmotion || null;

  const [messages, setMessages]               = useState([]);
  const [input, setInput]                     = useState("");
  const [loading, setLoading]                 = useState(false);
  const [thinkingPhrase, setThinkingPhrase]   = useState(THINKING_PHRASES[0]);
  const [contextConsumed, setContextConsumed] = useState(false);
  const [showConfirm, setShowConfirm]         = useState(false);
  const [userMessageCount, setUserMessageCount] = useState(0);
  const [saveBannerVisible, setSaveBannerVisible] = useState(false);
  const [saveStatus, setSaveStatus]           = useState(null); // null | "saving" | "saved"
  const bottomRef = useRef(null);

  const isGuest = !user || user.user_id === "guest";

  // inject checkin opening message on mount if arriving from check-in flow
  useEffect(() => {
    if (checkinEmotion) {
      setMessages([
        {
          role: "assistant",
          content: `You checked in as ${checkinEmotion} -- want to tell me what's going on?`,
        },
      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (entryContext) setContextConsumed(false);
  }, [entryContext]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    const contextToSend = !contextConsumed && entryContext ? entryContext : null;
    if (contextToSend) {
      setContextConsumed(true);
      onContextUsed();
    }

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    setThinkingPhrase(randomThinkingPhrase());

    const newCount = userMessageCount + 1;
    setUserMessageCount(newCount);

    // show save banner after threshold, only once, only in checkin flow
    if (checkinEmotion && newCount >= SAVE_BANNER_THRESHOLD && !saveBannerVisible && saveStatus === null) {
      setSaveBannerVisible(true);
    }

    try {
      const data = await sendMessage(user?.user_id ?? "guest", text, contextToSend);

      if (data.crisis_detected) {
        await new Promise((resolve) => setTimeout(resolve, 1500));
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          crisis: data.crisis_detected,
        },
      ]);
    } catch {
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

  async function handleSaveAsEntry() {
    if (!user || isGuest) return;
    setSaveStatus("saving");
    try {
      const transcript = messages
        .map((m) => `${m.role === "user" ? "You" : "Indy"}: ${m.content}`)
        .join("\n\n");
      await createEntry(user.user_id, transcript, null, "checkin", checkinEmotion);
      setSaveStatus("saved");
      setTimeout(() => setSaveBannerVisible(false), 1500);
    } catch {
      setSaveStatus(null);
    }
  }

  function handleResetClick() {
    if (messages.length === 0) return;
    if (isGuest) {
      resetChat("guest").catch(() => {});
      setMessages([]);
      return;
    }
    setShowConfirm(true);
  }

  async function confirmReset() {
    setShowConfirm(false);
    await resetChat(user?.user_id ?? "guest").catch(() => {});
    setMessages([]);
  }

  function cancelReset() {
    setShowConfirm(false);
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
          <button style={s.resetBtn} onClick={handleResetClick}>Clear chat</button>
        </div>
        <div style={s.disclaimer}>
          <div style={s.dot} />
          Indy is an AI companion, not a therapist
        </div>
      </div>

      {showConfirm && (
        <div style={s.confirmBanner}>
          <span style={s.confirmText}>Clear this conversation? This cannot be undone.</span>
          <div style={s.confirmBtns}>
            <button style={s.confirmYes} onClick={confirmReset}>Clear</button>
            <button style={s.confirmNo} onClick={cancelReset}>Cancel</button>
          </div>
        </div>
      )}

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
            {isGuest && (
              <div style={s.guestNote}>
                You're chatting as a guest. Indy can still reflect with you, but
                your conversation won't be saved and there's no entry history to
                draw on. Create a profile to unlock journaling and longitudinal
                tracking.
              </div>
            )}
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={s.bubbleWrapper(msg.role)}>
            <div style={s.bubble(msg.role, msg.crisis)}>
              {msg.crisis && <div style={s.crisisLabel}>Crisis support</div>}
              {msg.content}
              {msg.crisis && (
                <a href="tel:988" style={s.callBtn}>
                  Call or text 988
                </a>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={s.bubbleWrapper("assistant")}>
            <div style={s.typing}>{thinkingPhrase}</div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {saveBannerVisible && (
        <div style={s.saveBanner}>
          <span style={s.saveBannerText}>Save this conversation as a journal entry?</span>
          <div style={s.saveBannerBtns}>
            <button style={s.dismissBtn} onClick={() => setSaveBannerVisible(false)}>
              Dismiss
            </button>
            <button
              style={{ ...s.saveBtn, opacity: saveStatus !== null ? 0.6 : 1 }}
              onClick={handleSaveAsEntry}
              disabled={saveStatus !== null}
            >
              {saveStatus === "saving" && "Saving..."}
              {saveStatus === "saved"  && "Saved"}
              {saveStatus === null     && "Save as entry"}
            </button>
          </div>
        </div>
      )}

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
