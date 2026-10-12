// All calls to the backend live here, so pages stay simple.
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function getToken() { return localStorage.getItem("token"); }
export function setSession(data) {
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("role", data.role);
  localStorage.setItem("name", data.name);
}
export function logout() { localStorage.clear(); }

async function call(path, method = "GET", body) {
  const res = await fetch(BASE + path, {
    method,
    headers: { "Content-Type": "application/json", ...(getToken() ? { Authorization: "Bearer " + getToken() } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Request failed");
  return data;
}

export const api = {
  login: (b) => call("/auth/login", "POST", b),
  register: (b) => call("/auth/register", "POST", b),
  myProfile: () => call("/profiles/me"),
  saveProfile: (b) => call("/profiles/me", "PUT", b),
  matchResearchers: (method, scope) => call(`/match/researchers?method=${method}&scope=${scope}`),
  matchProjects: (method) => call(`/match/projects?method=${method}`),
  compare: () => call("/match/compare"),
  projects: (q = "") => call(`/projects?q=${encodeURIComponent(q)}`),
  createProject: (b) => call("/projects", "POST", b),
  sendRequest: (b) => call("/requests", "POST", b),
  inbox: () => call("/requests/inbox"),
  answer: (id, status) => call(`/requests/${id}`, "PATCH", { status }),
  notifications: () => call("/notifications"),
  opportunities: () => call("/opportunities"),
  stats: () => call("/admin/stats"),
  runAlerts: () => call("/alerts/run", "POST"),
  alertHistory: () => call("/alerts"),
};
