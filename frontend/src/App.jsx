import { useEffect, useState } from "react";
import { api, getToken, logout, setSession } from "./api.js";

const split = (s) => s.split(",").map((x) => x.trim()).filter(Boolean);

/* ---------- Login / Register ---------- */
function Auth({ onDone }) {
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ name: "", email: "", password: "", organization_name: "", organization_type: "college", role: "researcher" });
  const [err, setErr] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const submit = async () => {
    try {
      setErr("");
      const data = mode === "login" ? await api.login({ email: f.email, password: f.password }) : await api.register(f);
      setSession(data); onDone();
    } catch (e) { setErr(e.message); }
  };
  return (
    <div className="card" style={{ maxWidth: 420, margin: "60px auto" }}>
      <h2>ResearchConnect</h2>
      {mode === "register" && (<>
        <label>Full name</label><input value={f.name} onChange={set("name")} />
        <label>Organisation (college / university / company)</label><input value={f.organization_name} onChange={set("organization_name")} />
        <div className="row">
          <div><label>Type</label><select value={f.organization_type} onChange={set("organization_type")}><option>college</option><option>university</option><option>company</option></select></div>
          <div><label>I am a</label><select value={f.role} onChange={set("role")}><option value="researcher">Researcher</option><option value="coordinator">Coordinator</option><option value="industry">Industry partner</option></select></div>
        </div>
      </>)}
      <label>Email</label><input value={f.email} onChange={set("email")} />
      <label>Password (min 8 characters)</label><input type="password" value={f.password} onChange={set("password")} />
      {err && <p className="err">{err}</p>}
      <button className="primary" onClick={submit}>{mode === "login" ? "Login" : "Create account"}</button>
      <p className="small" style={{ cursor: "pointer" }} onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "No account? Register" : "Have an account? Login"}
      </p>
    </div>
  );
}

/* ---------- Dashboard: recommendations ---------- */
function Dashboard() {
  const [method, setMethod] = useState("hybrid");
  const [scope, setScope] = useState("all");
  const [items, setItems] = useState([]);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  useEffect(() => {
    setErr("");
    api.matchResearchers(method, scope).then(setItems).catch((e) => setErr(e.message));
  }, [method, scope]);
  const send = async (id) => {
    try { await api.sendRequest({ receiver_id: id, message: "I would like to explore a collaboration with you." }); setMsg("Request sent!"); }
    catch (e) { setMsg(e.message); }
  };
  return (<>
    <div className="card">
      <h2>Recommended collaborators</h2>
      <div className="row">
        <div><label>Matching method</label>
          <select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option value="hybrid">Hybrid</option><option value="tfidf">TF-IDF</option><option value="tag">Tag (Jaccard)</option><option value="keyword">Keyword</option>
          </select></div>
        <div><label>Search within</label>
          <select value={scope} onChange={(e) => setScope(e.target.value)}>
            <option value="org">My college only (intra)</option><option value="academia">Other colleges (inter)</option>
            <option value="industry">Industry partners</option><option value="all">Everyone</option>
          </select></div>
      </div>
      {err && <p className="err">{err}</p>}{msg && <p className="ok">{msg}</p>}
    </div>
    {items.map((r) => (
      <div className="card match" key={r.user_id}>
        <div className={"pct " + (r.percent >= 40 ? "" : r.percent >= 20 ? "mid" : "low")}>{Math.round(r.percent)}%</div>
        <div style={{ flex: 1 }}>
          <b>{r.name}</b>
          <div className="bar"><div style={{ width: Math.min(100, r.percent) + "%" }} /></div>
          <ul className="reasons">{r.explanation.reasons.map((x, i) => <li key={i}>{x}</li>)}</ul>
          {r.explanation.shared_tags.map((t) => <span className="chip" key={t}>{t}</span>)}
          <div><button className="ghost" onClick={() => send(r.user_id)}>Send collaboration request</button></div>
        </div>
      </div>
    ))}
    {!items.length && !err && <p className="small">No matches yet. Complete your profile and add more researchers.</p>}
  </>);
}

/* ---------- Profile ---------- */
function Profile() {
  const [p, setP] = useState(null);
  const [msg, setMsg] = useState("");
  useEffect(() => { api.myProfile().then(setP); }, []);
  if (!p) return <p>Loading...</p>;
  const set = (k) => (e) => setP({ ...p, [k]: e.target.value });
  const setList = (k) => (e) => setP({ ...p, [k]: split(e.target.value) });
  const save = async () => {
    try { const r = await api.saveProfile(p); setP(r); setMsg("Saved. Profile " + r.completeness + "% complete"); }
    catch (e) { setMsg(e.message); }
  };
  return (
    <div className="card">
      <h2>My profile ({p.organization})</h2>
      <label>Department</label><input value={p.department} onChange={set("department")} />
      <label>Designation</label><input value={p.designation} onChange={set("designation")} />
      <label>Bio</label><textarea rows={4} value={p.bio} onChange={set("bio")} />
      <label>Skills (comma separated)</label><input defaultValue={p.skills.join(", ")} onBlur={setList("skills")} />
      <label>Research interests (comma separated)</label><input defaultValue={p.interests.join(", ")} onBlur={setList("interests")} />
      <label>Expertise (comma separated)</label><input defaultValue={p.expertise.join(", ")} onBlur={setList("expertise")} />
      <label>Looking to collaborate on</label><input value={p.collab_area} onChange={set("collab_area")} />
      <label>Who can see my profile?</label>
      <select value={p.visibility} onChange={set("visibility")}><option value="public">Everyone (all colleges and industry)</option><option value="org">My organisation only</option></select>
      <label><input type="checkbox" style={{ width: "auto" }} checked={p.email_alerts} onChange={(e) => setP({ ...p, email_alerts: e.target.checked })} />
        {" "}Email me (and the other researcher) when we find a strong match</label>
      <p className="small">If both profiles are public, the email includes each other's contact address.</p>
      <button className="primary" onClick={save}>Save profile</button>{" "}
      <button className="ghost" onClick={async () => { const r = await api.runAlerts(); setMsg(r.new_matches_emailed + " new match email(s) sent"); }}>Check matches now</button>{" "}
      <span className="ok">{msg}</span>
    </div>
  );
}

/* ---------- Projects ---------- */
function Projects() {
  const [list, setList] = useState([]);
  const [f, setF] = useState({ title: "", description: "", domain: "", tags: "" });
  const load = () => api.projects().then(setList);
  useEffect(() => { load(); }, []);
  const create = async () => { await api.createProject({ ...f, tags: split(f.tags) }); setF({ title: "", description: "", domain: "", tags: "" }); load(); };
  return (<>
    <div className="card">
      <h2>Add a project</h2>
      <label>Title</label><input value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} />
      <label>Domain</label><input value={f.domain} onChange={(e) => setF({ ...f, domain: e.target.value })} />
      <label>Description</label><textarea rows={3} value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} />
      <label>Required skills (comma separated)</label><input value={f.tags} onChange={(e) => setF({ ...f, tags: e.target.value })} />
      <button className="primary" onClick={create}>Create project</button>
    </div>
    {list.map((p) => (
      <div className="card" key={p.id}><b>{p.title}</b> <span className="small">by {p.owner}, {p.organization}</span>
        <p>{p.description}</p>{p.tags.map((t) => <span className="chip" key={t}>{t}</span>)}</div>
    ))}
  </>);
}

/* ---------- Inbox (requests + notifications) ---------- */
function Inbox() {
  const [reqs, setReqs] = useState([]);
  const [notes, setNotes] = useState([]);
  const load = () => { api.inbox().then(setReqs); api.notifications().then(setNotes); };
  useEffect(load, []);
  const answer = async (id, s) => { await api.answer(id, s); load(); };
  return (<>
    <div className="card"><h2>Collaboration requests</h2>
      {reqs.map((r) => (
        <div key={r.id} style={{ marginBottom: 10 }}>
          <b>{r.sender}</b>: {r.message} <span className="chip">{r.status}</span>
          {r.status === "pending" && <> <button className="primary" onClick={() => answer(r.id, "accepted")}>Accept</button> <button className="ghost" onClick={() => answer(r.id, "rejected")}>Reject</button></>}
        </div>))}
      {!reqs.length && <p className="small">No requests yet.</p>}
    </div>
    <div className="card"><h2>Notifications</h2>
      {notes.map((n) => <p key={n.id}>🔔 {n.message}</p>)}
      {!notes.length && <p className="small">Nothing new.</p>}
    </div>
  </>);
}

/* ---------- Opportunities ---------- */
function Opportunities() {
  const [list, setList] = useState([]);
  useEffect(() => { api.opportunities().then(setList); }, []);
  return (<div className="card"><h2>Opportunities and industry challenges</h2>
    {list.map((o) => (<div key={o.id} style={{ marginBottom: 12 }}>
      <b>{o.title}</b> <span className="chip">{o.type}</span>
      <div className="small">{o.organization} {o.deadline && "| deadline " + o.deadline.slice(0, 10)}</div><p>{o.description}</p></div>))}
    {!list.length && <p className="small">No open opportunities.</p>}
  </div>);
}

/* ---------- Admin dashboard ---------- */
function Admin() {
  const [s, setS] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => { api.stats().then(setS).catch((e) => setErr(e.message)); }, []);
  if (err) return <p className="err">{err}</p>;
  if (!s) return <p>Loading...</p>;
  const max = Math.max(1, ...s.top_tags.map((t) => t.count));
  return (<>
    <div className="card"><h2>Platform statistics</h2>
      <div className="stats">{[["Researchers", s.researchers], ["Organisations", s.organizations], ["Projects", s.projects], ["Requests", s.collaboration_requests], ["Accepted", s.accepted_collaborations], ["Opportunities", s.opportunities]].map(([k, v]) => <div className="stat" key={k}><b>{v}</b>{k}</div>)}</div></div>
    <div className="card"><h2>Top research tags</h2>
      {s.top_tags.map((t) => (<div key={t.tag}><span className="small">{t.tag} ({t.count})</span><div className="bar"><div style={{ width: (100 * t.count) / max + "%" }} /></div></div>))}
    </div>
  </>);
}

/* ---------- App shell ---------- */
export default function App() {
  const [authed, setAuthed] = useState(!!getToken());
  const [page, setPage] = useState("dashboard");
  if (!authed) return <Auth onDone={() => setAuthed(true)} />;
  const role = localStorage.getItem("role");
  const tabs = [["dashboard", "Recommendations"], ["profile", "My profile"], ["projects", "Projects"], ["opps", "Opportunities"], ["inbox", "Inbox"]];
  if (role === "admin" || role === "coordinator") tabs.push(["admin", "Admin"]);
  const view = { dashboard: <Dashboard />, profile: <Profile />, projects: <Projects />, opps: <Opportunities />, inbox: <Inbox />, admin: <Admin /> }[page];
  return (<>
    <header>
      <h1>ResearchConnect</h1>
      <nav>{tabs.map(([k, l]) => <button key={k} className={page === k ? "active" : ""} onClick={() => setPage(k)}>{l}</button>)}</nav>
      <span className="spacer" />
      <span className="small" style={{ color: "#cfe3f1" }}>{localStorage.getItem("name")}</span>
      <button className="ghost" onClick={() => { logout(); setAuthed(false); }}>Logout</button>
    </header>
    <main>{view}</main>
  </>);
}
