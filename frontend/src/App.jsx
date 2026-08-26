import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function api(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.message || "Request failed");
  return body;
}

export function App() {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [artifact, setArtifact] = useState(null);
  const [format, setFormat] = useState("markdown");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/sessions", { method: "POST", body: JSON.stringify({ user_metadata: { source: "web" } }) })
      .then(setSession)
      .catch((requestError) => setError(requestError.message));
  }, []);

  async function sendMessage(event) {
    event.preventDefault();
    if (!draft.trim() || !session || loading) return;
    const content = draft.trim();
    setDraft("");
    setError("");
    setLoading(true);
    setMessages((current) => [...current, { role: "user", content }]);
    try {
      const response = await api(`/sessions/${session.id}/messages`, {
        method: "POST",
        body: JSON.stringify({ content }),
      });
      setMessages((current) => [...current, response]);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function createArtifact() {
    if (!session || loading) return;
    setError("");
    setLoading(true);
    try {
      const response = await api(`/sessions/${session.id}/artifacts`, {
        method: "POST",
        body: JSON.stringify({ format }),
      });
      setArtifact(response);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">LG</span><div><p className="eyebrow">FIELD NOTES / 01</p><h1>Lenny Growth Assistant</h1></div></div>
        <div className="status"><span className="status-dot" /> Local knowledge base <strong>qwen2.5:1.5b</strong></div>
      </header>
      <section className="workspace">
        <div className="conversation panel">
          <div className="panel-head"><div><p className="eyebrow">Research desk</p><h2>Ask better growth questions.</h2></div><span className="session-label">{session ? "SESSION ACTIVE" : "CONNECTING"}</span></div>
          <div className="messages" aria-live="polite">
            {messages.length === 0 && <div className="empty-state"><span className="empty-number">01</span><p>Start with a product, growth, or team question. Answers are grounded in the transcript archive.</p></div>}
            {messages.map((message, index) => <article className={`message ${message.role}`} key={`${message.id || message.role}-${index}`}><span className="message-role">{message.role === "user" ? "YOU" : "ASSISTANT"}</span><div className="message-body">{message.role === "assistant" ? <ReactMarkdown>{message.content}</ReactMarkdown> : <p>{message.content}</p>}{message.sources?.length > 0 && <div className="sources"><span>Sources</span>{message.sources.map((source) => <small key={`${source.source}-${source.score}`}>{source.source}</small>)}</div>}</div></article>)}
            {loading && <div className="thinking"><span /> thinking with the archive...</div>}
          </div>
          <form className="composer" onSubmit={sendMessage}><textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Ask about activation, retention, positioning..." rows="2" disabled={!session || loading} /><button type="submit" disabled={!session || loading || !draft.trim()} aria-label="Send question">Send <span>↗</span></button></form>
          {error && <p className="error" role="alert">{error}</p>}
        </div>
        <aside className="artifact panel">
          <div className="panel-head"><div><p className="eyebrow">Workbench</p><h2>Artifact viewer</h2></div><span className="artifact-icon">✦</span></div>
          <div className="artifact-actions"><button className={format === "markdown" ? "selected" : ""} onClick={() => setFormat("markdown")}>Markdown</button><button className={format === "html" ? "selected" : ""} onClick={() => setFormat("html")}>HTML</button><button className="generate" onClick={createArtifact} disabled={!session || loading}>Generate</button></div>
          <div className="artifact-preview">{artifact ? (artifact.format === "markdown" ? <ReactMarkdown>{artifact.content}</ReactMarkdown> : <iframe title="Generated HTML artifact" sandbox="" srcDoc={artifact.content} />) : <div className="artifact-empty"><span>✧</span><p>Your generated essay or artifact will appear here.</p></div>}</div>
          {artifact && <p className="artifact-meta">{artifact.format.toUpperCase()} / SANDBOXED PREVIEW</p>}
        </aside>
      </section>
    </main>
  );
}
