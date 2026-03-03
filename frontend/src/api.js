/**
 * src/api.js
 *
 * All communication with the FastAPI backend goes through this file.
 * If you ever change the backend URL (e.g. for deployment), you only
 * need to update the BASE_URL constant below.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// ---- Users / profiles ----

export function getUsers() {
  return request("/users");
}

// ---- Journal entries ----

export function getEntries(userId) {
  return request(`/users/${userId}/entries`);
}

export function createEntry(userId, text, weekNumber = null) {
  return request("/entries", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, text, week_number: weekNumber }),
  });
}

// ---- Insights ----

export function getInsights(userId) {
  return request(`/users/${userId}/insights`);
}

// ---- Chat ----

export function sendMessage(userId, message, entryContext = null) {
  return request("/chat", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, message, entry_context: entryContext }),
  });
}

export function resetChat(userId) {
  return request("/chat/reset", {
    method: "POST",
    body: JSON.stringify({ user_id: userId }),
  });
}
