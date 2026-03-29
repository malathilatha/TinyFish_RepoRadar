import { useState, useEffect } from "react";

const BACKEND = "http://localhost:8000";

const SEV_COLOR  = { critical:"#ff4444", high:"#ff8800", opportunity:"#00ff88", medium:"#f5a623" };
const FREQ_COLOR = { high:"#ff5555", medium:"#f5a623", low:"#aaa" };
const DEMAND     = { high:"#00ff88", medium:"#f5a623", low:"#ff5555", unknown:"#777" };

const DEMO_REPOS = [
  "https://github.com/microsoft/vscode",
  "https://github.com/facebook/react",
  "https://github.com/tiangolo/fastapi",
  "https://github.com/pytorch/pytorch",
  "https://github.com/vercel/next.js",
];

const GithubIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
  </svg>
);

const Badge = ({ label, color="#aaa" }) => (
  <span style={{ background:`${color}22`, border:`1px solid ${color}55`, color,
    borderRadius:"100px", padding:"3px 12px", fontSize:"12px",
    fontWeight:800, letterSpacing:"0.06em", textTransform:"uppercase" }}>
    {label}
  </span>
);

const Card = ({ children, style={} }) => (
  <div style={{ background:"#161616", border:"1px solid #2a2a2a", borderRadius:"10px", padding:"16px", ...style }}>
    {children}
  </div>
);

const Label = ({ children, color="#777" }) => (
  <div style={{ fontSize:"11px", color, textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:"8px", fontWeight:700 }}>
    {children}
  </div>
);

function AgentRow({ icon, label, status }) {
  const c = { waiting:"#333", running:"#f5a623", done:"#00ff88" };
  return (
    <div style={{ display:"flex", alignItems:"center", gap:"12px", padding:"9px 0", borderBottom:"1px solid #1a1a1a" }}>
      <span style={{ fontSize:"16px" }}>{icon}</span>
      <span style={{ flex:1, fontSize:"14px", fontWeight:600,
        color:status==="done"?"#eee":status==="running"?"#fff":"#666" }}>{label}</span>
      <span style={{ width:"8px", height:"8px", borderRadius:"50%", background:c[status],
        boxShadow:status==="running"?`0 0 10px ${c.running}`:"none",
        animation:status==="running"?"pulse 1s ease-in-out infinite":"none" }}/>
    </div>
  );
}

const CopyBtn = ({ text }) => {
  const [done, setDone] = useState(false);
  return (
    <button onClick={async () => { await navigator.clipboard.writeText(text); setDone(true); setTimeout(()=>setDone(false),2000); }}
      style={{ background:done?"#00ff8822":"#ffffff15", border:`1px solid ${done?"#00ff8855":"#444"}`,
        borderRadius:"6px", color:done?"#00ff88":"#ccc", cursor:"pointer", padding:"5px 12px", fontSize:"13px", fontWeight:600 }}>
      {done?"✓ Copied":"Copy"}
    </button>
  );
};

function SignalCard({ signal, onAutoPost, autoposting }) {
  const color = SEV_COLOR[signal.severity] || "#aaa";
  return (
    <div style={{ background:"#0f0f0f", border:`1px solid ${color}44`,
      borderLeft:`4px solid ${color}`, borderRadius:"12px", padding:"18px", marginBottom:"14px" }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:"10px" }}>
        <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
          <span style={{ fontSize:"22px" }}>{signal.emoji}</span>
          <span style={{ fontWeight:800, fontSize:"16px", color }}>{signal.title}</span>
        </div>
        <Badge label={signal.severity} color={color}/>
      </div>
      <p style={{ fontSize:"14px", color:"#bbb", margin:"0 0 6px", lineHeight:1.6 }}>{signal.detail}</p>
      <p style={{ fontSize:"13px", color:"#777", margin:"0 0 12px" }}>📊 {signal.metric}</p>
      <div style={{ background:"#1a1a1a", borderRadius:"8px", padding:"12px", marginBottom:"10px" }}>
        <Label color="#00ff88aa">⚡ Recommended Action</Label>
        <p style={{ fontSize:"14px", color:"#ddd", margin:0, fontWeight:600 }}>{signal.action}</p>
      </div>
      {signal.post_draft && (
        <div style={{ background:"#0c1a0c", borderRadius:"8px", padding:"12px" }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"8px" }}>
            <Label color="#00ff88aa">📝 Auto-Draft</Label>
            <div style={{ display:"flex", gap:"8px" }}>
              <CopyBtn text={signal.post_draft}/>
              <button onClick={() => onAutoPost(signal.post_draft)} disabled={autoposting}
                style={{ background:"#9b59b622", border:"1px solid #9b59b666",
                  borderRadius:"6px", color:"#d7a8ff", cursor:"pointer",
                  padding:"5px 12px", fontSize:"13px", fontWeight:700,
                  opacity: autoposting ? 0.5 : 1 }}>
                {autoposting ? "🐦 Posting..." : "🐦 Auto-Post"}
              </button>
            </div>
          </div>
          <p style={{ fontSize:"13px", color:"#bbb", margin:0, fontStyle:"italic", lineHeight:1.6 }}>
            {signal.post_draft}
          </p>
        </div>
      )}
    </div>
  );
}

const WorkflowBanner = ({ activeStep }) => {
  const steps = [
    { id:1, icon:"🌐", label:"Fan Out" },
    { id:2, icon:"🔍", label:"Detect Signal" },
    { id:3, icon:"🚨", label:"Alert" },
  ];
  return (
    <div style={{ display:"flex", alignItems:"center", justifyContent:"center", gap:"8px", marginBottom:"28px", flexWrap:"wrap" }}>
      {steps.map((s, i) => (
        <div key={s.id} style={{ display:"flex", alignItems:"center", gap:"8px" }}>
          <div style={{ display:"flex", flexDirection:"column", alignItems:"center",
            background: activeStep >= s.id ? "#00ff8818" : "#111",
            border: `2px solid ${activeStep >= s.id ? "#00ff88" : "#2a2a2a"}`,
            borderRadius:"12px", padding:"12px 22px", minWidth:"110px", transition:"all 0.3s",
            boxShadow: activeStep >= s.id ? "0 0 14px #00ff8840" : "none" }}>
            <span style={{ fontSize:"24px" }}>{s.icon}</span>
            <span style={{ fontSize:"15px", color: activeStep >= s.id ? "#00ff88" : "#555",
              fontWeight: 800, marginTop:"8px" }}>
              {s.label}
            </span>
          </div>
          {i < steps.length - 1 && (
            <span style={{ color: activeStep > s.id ? "#00ff88" : "#333", fontSize:"24px", fontWeight:900 }}>→</span>
          )}
        </div>
      ))}
    </div>
  );
};

const TOP_NAV = [
  { id:"analyze",   label:"⚡ Analyze" },
  { id:"benchmark", label:"🏆 Benchmark" },
  { id:"watchlist", label:"👁 Watchlist" },
  { id:"signals",   label:"🚨 Signals" },
];

export default function App() {
  const [url, setUrl]         = useState("https://github.com/microsoft/vscode");
  const [nav, setNav]         = useState("analyze");
  const [phase, setPhase]     = useState("idle");
  const [agentStatus, setAgentStatus] = useState("waiting");
  const [report, setReport]   = useState(null);
  const [statusMsg, setMsg]   = useState("");
  const [err, setErr]         = useState("");
  const [workflowStep, setWorkflowStep] = useState(0);

  const [benchPhase, setBenchPhase] = useState("idle");
  const [benchmark, setBenchmark]   = useState(null);
  const [benchMsg, setBenchMsg]     = useState("");

  const [watchEmail, setWatchEmail]   = useState("");
  const [autoTweet, setAutoTweet]     = useState(true);
  const [watchStatus, setWatchStatus] = useState("");
  const [watchList, setWatchList]     = useState([]);
  const [watchChecking, setWatchChecking] = useState(false);

  const [signalFeed, setSignalFeed] = useState([]);
  const [autoposting, setAutoposting] = useState(false);
  const [autopostStatus, setAutopostStatus] = useState("");

  useEffect(() => { fetchWatchList(); fetchSignals(); }, []);

  const fetchWatchList = async () => {
    try { const r = await fetch(`${BACKEND}/watchlist`); const d = await r.json(); setWatchList(d.repos||[]); } catch {}
  };

  const fetchSignals = async () => {
    try { const r = await fetch(`${BACKEND}/watchlist/signals`); const d = await r.json(); setSignalFeed(d.signals||[]); } catch {}
  };

  const autoPostTweet = async (text) => {
    setAutoposting(true); setAutopostStatus("🐦 TinyFish is navigating Twitter...");
    try {
      const res = await fetch(`${BACKEND}/autopost/tweet`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ tweet_text: text }),
      });
      const data = await res.json();
      setAutopostStatus(data.success ? "✅ Tweet posted by TinyFish!" : `❌ ${data.error}`);
    } catch { setAutopostStatus("❌ Could not reach backend."); }
    setAutoposting(false);
  };

  const analyze = async () => {
    if (!url.trim() || phase==="loading") return;
    setPhase("loading"); setReport(null); setErr("");
    setAgentStatus("running"); setWorkflowStep(1);
    try {
      const res = await fetch(`${BACKEND}/analyze`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ github_url: url }),
      });
      const reader = res.body.getReader(); const dec = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read(); if (done) break;
        for (const l of dec.decode(value).split("\n").filter(l=>l.startsWith("data: "))) {
          try {
            const ev = JSON.parse(l.slice(6));
            setMsg(ev.message||"");
            if (ev.step==="merging") { setAgentStatus("done"); setWorkflowStep(2); }
            if (ev.step==="done")    { setReport(ev.report); setPhase("done"); setWorkflowStep(2); }
            if (ev.step==="error")   { setErr(ev.message); setPhase("error"); }
          } catch {}
        }
      }
    } catch(e) { setErr("Cannot connect to backend on port 8000."); setPhase("error"); }
  };

  const runBenchmark = async () => {
    if (!url.trim()) return;
    setBenchPhase("loading"); setBenchmark(null);
    setBenchMsg("Finding #1 competitor via GitHub API...");
    try {
      const res = await fetch(`${BACKEND}/benchmark`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ github_url: url }),
      });
      const reader = res.body.getReader(); const dec = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read(); if (done) break;
        for (const l of dec.decode(value).split("\n").filter(l=>l.startsWith("data: "))) {
          try {
            const ev = JSON.parse(l.slice(6));
            if (ev.message) setBenchMsg(ev.message);
            if (ev.step==="done")  { setBenchmark(ev.benchmark); setBenchPhase("done"); }
            if (ev.step==="error") { setBenchMsg(ev.message); setBenchPhase("error"); }
          } catch {}
        }
      }
    } catch { setBenchPhase("error"); }
  };

  const addToWatchlist = async () => {
    if (!url.trim() || !watchEmail.trim()) { setWatchStatus("Enter both URL and email."); return; }
    try {
      const res = await fetch(`${BACKEND}/watchlist/add`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ github_url:url, email:watchEmail, auto_tweet:autoTweet }),
      });
      const data = await res.json();
      setWatchStatus(data.message || "✅ Added!"); setWorkflowStep(3); fetchWatchList();
    } catch { setWatchStatus("Failed to add."); }
  };

  const runWatchlistCheck = async () => {
    setWatchChecking(true); setWatchStatus("🔍 Agents scanning repos...");
    try {
      await fetch(`${BACKEND}/watchlist/check`, { method:"POST" });
      setWatchStatus("✅ Signal check started! Refresh signals in ~30s.");
      setWorkflowStep(3);
      setTimeout(() => { fetchSignals(); }, 5000);
    } catch { setWatchStatus("Failed."); }
    setWatchChecking(false);
  };

  const S = { fontSize:"14px", color:"#ddd", lineHeight:1.7 };

  return (
    <div style={{ minHeight:"100vh", background:"#080808",
      fontFamily:"'Inter','Helvetica Neue',sans-serif", color:"#fff", padding:"28px 16px" }}>
      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes spin   { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        * { box-sizing:border-box; }
        button:hover { opacity:0.85; }
      `}</style>

      <div style={{ maxWidth:"980px", margin:"0 auto" }}>

        {/* Header */}
        <div style={{ textAlign:"center", marginBottom:"28px" }}>
          <h1 style={{ fontSize:"clamp(42px,7vw,72px)", fontWeight:900,
            letterSpacing:"-0.04em", lineHeight:1, margin:"0 0 10px",
            background:"linear-gradient(135deg,#ffffff 40%,#00ff88)",
            WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>
            RepoRadar
          </h1>
          <p style={{ color:"#aaa", fontSize:"15px", margin:"0 0 24px", fontWeight:500 }}>
            Autonomous web intelligence · Detects pain points · Benchmarks competitors · Fires alerts
          </p>
          <WorkflowBanner activeStep={workflowStep} />
        </div>

        {/* URL Input */}
        <div style={{ background:"#111", border:"1px solid #2a2a2a",
          borderRadius:"14px", padding:"18px", marginBottom:"16px" }}>
          <div style={{ display:"flex", gap:"10px", flexWrap:"wrap" }}>
            <div style={{ flex:1, position:"relative", minWidth:"240px" }}>
              <span style={{ position:"absolute", left:"13px", top:"50%", transform:"translateY(-50%)", color:"#666" }}>
                <GithubIcon />
              </span>
              <input value={url} onChange={e=>setUrl(e.target.value)}
                onKeyDown={e=>e.key==="Enter"&&nav==="analyze"&&analyze()}
                style={{ width:"100%", background:"#1a1a1a", border:"1px solid #333",
                  borderRadius:"10px", padding:"12px 12px 12px 40px",
                  color:"#fff", fontSize:"15px", outline:"none", fontWeight:500 }}
                onFocus={e=>e.target.style.borderColor="#00ff8877"}
                onBlur={e=>e.target.style.borderColor="#333"} />
            </div>
            {nav==="analyze" && (
              <button onClick={analyze} disabled={phase==="loading"||!url.trim()}
                style={{ background:phase==="loading"?"#111":"linear-gradient(135deg,#00ff88,#00cc66)",
                  color:phase==="loading"?"#00ff8844":"#000", border:"none",
                  borderRadius:"10px", padding:"12px 28px", fontSize:"15px",
                  fontWeight:900, cursor:phase==="loading"||!url.trim()?"not-allowed":"pointer",
                  opacity:!url.trim()?0.4:1 }}>
                {phase==="loading"?"Scanning...":"⚡ Analyze"}
              </button>
            )}
            {nav==="benchmark" && (
              <button onClick={runBenchmark} disabled={!url.trim()||benchPhase==="loading"}
                style={{ background:"linear-gradient(135deg,#f5a623,#e67e22)",
                  color:"#000", border:"none", borderRadius:"10px",
                  padding:"12px 24px", fontSize:"15px", fontWeight:900,
                  cursor:!url.trim()?"not-allowed":"pointer", opacity:!url.trim()?0.4:1 }}>
                {benchPhase==="loading"?"Benchmarking...":"🏆 Benchmark"}
              </button>
            )}
          </div>

          <div style={{ marginTop:"12px", display:"flex", gap:"6px", flexWrap:"wrap" }}>
            <span style={{ fontSize:"11px", color:"#555", alignSelf:"center", fontWeight:700 }}>QUICK SELECT:</span>
            {DEMO_REPOS.map(r => (
              <button key={r} onClick={() => setUrl(r)}
                style={{ background: url===r?"#00ff8820":"transparent",
                  border:`1px solid ${url===r?"#00ff8855":"#2a2a2a"}`,
                  borderRadius:"6px", color: url===r?"#00ff88":"#777",
                  padding:"4px 10px", fontSize:"12px", cursor:"pointer", fontWeight:600 }}>
                {r.replace("https://github.com/","")}
              </button>
            ))}
          </div>
        </div>

        {/* Top Nav */}
        <div style={{ display:"flex", gap:"8px", marginBottom:"18px", flexWrap:"wrap" }}>
          {TOP_NAV.map(n=>(
            <button key={n.id} onClick={()=>setNav(n.id)}
              style={{ background:nav===n.id?"#00ff8820":"#111",
                border:`1px solid ${nav===n.id?"#00ff8855":"#2a2a2a"}`,
                borderRadius:"9px", color:nav===n.id?"#00ff88":"#aaa",
                padding:"9px 20px", fontSize:"14px", cursor:"pointer",
                fontWeight:nav===n.id?800:600 }}>
              {n.label}
            </button>
          ))}
          {signalFeed.length>0 && (
            <div style={{ marginLeft:"auto", display:"flex", alignItems:"center" }}>
              <span style={{ background:"#ff444420", border:"1px solid #ff444444",
                borderRadius:"100px", padding:"4px 14px", color:"#ff7777",
                fontSize:"13px", fontWeight:700, animation:"pulse 2s ease-in-out infinite" }}>
                🚨 {signalFeed.length} active signals
              </span>
            </div>
          )}
        </div>

        {/* ── ANALYZE ── */}
        {nav==="analyze" && (
          <div>
            {phase==="loading" && (
              <div style={{ background:"#111", border:"1px solid #00ff8830",
                borderRadius:"14px", padding:"24px", marginBottom:"18px", animation:"fadeUp 0.3s ease" }}>
                <div style={{ fontSize:"12px", color:"#00ff88", letterSpacing:"0.1em",
                  textTransform:"uppercase", marginBottom:"16px", fontWeight:800 }}>
                  🌐 Agent Scanning GitHub Issues
                </div>
                <AgentRow icon="🐛" label="GitHub Issues — Pain Point Detection" status={agentStatus} />
                {statusMsg && <p style={{ marginTop:"12px", fontSize:"13px", color:"#666" }}>{statusMsg}</p>}
              </div>
            )}

            {phase==="error" && (
              <div style={{ background:"#1a0808", border:"1px solid #ff444433",
                borderRadius:"10px", padding:"16px", marginBottom:"16px", color:"#ff9999", fontSize:"14px" }}>
                ⚠ {err}
              </div>
            )}

            {phase==="idle" && (
              <div style={{ background:"#111", border:"1px solid #222",
                borderRadius:"14px", padding:"48px", textAlign:"center", color:"#444" }}>
                <div style={{ fontSize:"48px", marginBottom:"16px" }}>🔭</div>
                <p style={{ fontSize:"16px", color:"#666", marginBottom:"8px", fontWeight:600 }}>
                  Select a repo above and click ⚡ Analyze
                </p>
                <p style={{ fontSize:"13px", color:"#444" }}>
                  1 TinyFish agent scans GitHub Issues and detects pain points
                </p>
              </div>
            )}

            {phase==="done" && report && (
              <div style={{ animation:"fadeUp 0.4s ease" }}>
                {/* Repo header */}
                <div style={{ background:"#0c180f", border:"1px solid #00ff8830",
                  borderRadius:"12px", padding:"16px 20px", marginBottom:"16px",
                  display:"flex", gap:"14px", alignItems:"center", flexWrap:"wrap" }}>
                  <div style={{ color:"#00ff88" }}><GithubIcon /></div>
                  <div style={{ flex:1 }}>
                    <div style={{ fontWeight:900, fontSize:"16px", color:"#00ff88" }}>{report.repo_name}</div>
                  </div>
                  <Badge
                    label={report.repo_health || "unknown"}
                    color={report.repo_health==="healthy" ? "#00ff88" : report.repo_health==="struggling" ? "#f5a623" : "#ff5555"}
                  />
                </div>

                {/* Pain summary */}
                {report.pain_summary && (
                  <p style={{ ...S, background:"#1a1a1a", borderRadius:"8px",
                    padding:"12px 16px", marginBottom:"16px", border:"1px solid #2a2a2a" }}>
                    {report.pain_summary}
                  </p>
                )}

                {/* Pain points */}
                <div style={{ marginBottom:"8px" }}>
                  <Label color="#ff5555">🐛 Pain Points</Label>
                </div>
                {(report.pain_points||[]).map((p,i)=>(
                  <Card key={i} style={{ marginBottom:"10px" }}>
                    <div style={{ display:"flex", gap:"10px", alignItems:"center", marginBottom:"8px" }}>
                      <span style={{ fontWeight:800, fontSize:"15px", color:"#fff" }}>{p.title}</span>
                      <Badge label={p.frequency} color={FREQ_COLOR[p.frequency]||"#aaa"}/>
                    </div>
                    <p style={{ ...S, margin:"0 0 8px" }}>{p.description}</p>
                    {p.opportunity && (
                      <div style={{ fontSize:"13px", color:"#00dd77", background:"#00ff8810",
                        borderRadius:"6px", padding:"6px 10px", fontWeight:600 }}>
                        💡 {p.opportunity}
                      </div>
                    )}
                  </Card>
                ))}

                {/* Feature requests */}
                {(report.top_feature_requests||[]).length>0 && (
                  <div style={{ marginTop:"20px" }}>
                    <Label>Top Feature Requests</Label>
                    {report.top_feature_requests.map((f,i)=>(
                      <div key={i} style={{ ...S, padding:"5px 0", display:"flex", gap:"8px" }}>
                        <span style={{ color:"#f5a623" }}>▸</span>{f}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── BENCHMARK ── */}
        {nav==="benchmark" && (
          <div>
            {benchPhase==="idle" && (
              <div style={{ background:"#111", border:"1px solid #222",
                borderRadius:"14px", padding:"48px", textAlign:"center", color:"#555" }}>
                <div style={{ fontSize:"40px", marginBottom:"14px" }}>🏆</div>
                <p style={{ fontSize:"16px", color:"#888", fontWeight:600, marginBottom:"6px" }}>
                  Enter a GitHub URL above and click Benchmark
                </p>
                <p style={{ fontSize:"13px", color:"#555" }}>
                  Finds the #1 starred competitor in the same language · Side-by-side comparison via GitHub API
                </p>
              </div>
            )}
            {benchPhase==="loading" && (
              <div style={{ background:"#111", border:"1px solid #222",
                borderRadius:"14px", padding:"36px", textAlign:"center" }}>
                <div style={{ width:"40px", height:"40px", border:"3px solid #1a1a1a",
                  borderTop:"3px solid #f5a623", borderRadius:"50%", margin:"0 auto 16px",
                  animation:"spin 0.8s linear infinite" }}/>
                <p style={{ fontSize:"14px", color:"#888", fontWeight:600 }}>{benchMsg}</p>
              </div>
            )}
            {benchPhase==="done" && benchmark && !benchmark.error && (
              <div style={{ animation:"fadeUp 0.4s ease" }}>
                <div style={{ display:"flex", alignItems:"center", gap:"12px", marginBottom:"18px" }}>
                  <h3 style={{ margin:0, fontSize:"16px", color:"#fff", fontWeight:800 }}>vs. Top Competitor</h3>
                  {benchmark.verdict && (
                    <Badge
                      label={benchmark.verdict.star_advantage==="ahead" ? "⭐ You're Ahead" : "📈 Catching Up"}
                      color={benchmark.verdict.star_advantage==="ahead" ? "#00ff88" : "#f5a623"}
                    />
                  )}
                  {benchmark.verdict?.star_gap !== undefined && (
                    <span style={{ fontSize:"13px", color:"#555", fontWeight:600 }}>
                      {Math.abs(benchmark.verdict.star_gap).toLocaleString()} star gap
                    </span>
                  )}
                </div>

                {benchmark.benchmark_table?.headers?.length > 0 && (
                  <div style={{ overflowX:"auto", background:"#111", border:"1px solid #222",
                    borderRadius:"12px", padding:"20px", marginBottom:"18px" }}>
                    <table style={{ width:"100%", borderCollapse:"collapse", fontSize:"14px" }}>
                      <thead>
                        <tr>
                          <th style={{ padding:"10px 14px", textAlign:"left", color:"#777",
                            borderBottom:"1px solid #2a2a2a", fontWeight:700 }}>Metric</th>
                          {benchmark.benchmark_table.headers.map((h,i)=>(
                            <th key={i} style={{ padding:"10px 14px", textAlign:"center",
                              color:i===0?"#00ff88":"#aaa", borderBottom:"1px solid #2a2a2a",
                              fontWeight:i===0?900:600 }}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {benchmark.benchmark_table.rows.map((row,i)=>(
                          <tr key={i} style={{ borderBottom:"1px solid #1a1a1a" }}>
                            <td style={{ padding:"10px 14px", color:"#777", fontWeight:600 }}>{row.metric}</td>
                            {row.values.map((v,j)=>(
                              <td key={j} style={{ padding:"10px 14px", textAlign:"center",
                                color:j===0?"#fff":"#aaa", fontWeight:j===0?800:500 }}>{v}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"14px" }}>
                  {benchmark.verdict?.main_unique_strengths?.length>0 && (
                    <Card>
                      <Label color="#00ff88">✅ Your Unique Strengths</Label>
                      {benchmark.verdict.main_unique_strengths.map((s,i)=>(
                        <div key={i} style={{ fontSize:"14px", color:"#ddd", lineHeight:1.7,
                          padding:"5px 0", display:"flex", gap:"8px" }}>
                          <span style={{ color:"#00ff88" }}>▸</span>{s}
                        </div>
                      ))}
                    </Card>
                  )}
                  {benchmark.verdict?.gaps_vs_competitors?.length>0 && (
                    <Card>
                      <Label color="#f5a623">⚠️ Gaps vs Competitor</Label>
                      {benchmark.verdict.gaps_vs_competitors.map((g,i)=>(
                        <div key={i} style={{ fontSize:"14px", color:"#ddd", lineHeight:1.7,
                          padding:"5px 0", display:"flex", gap:"8px" }}>
                          <span style={{ color:"#f5a623" }}>▸</span>{g}
                        </div>
                      ))}
                    </Card>
                  )}
                </div>
              </div>
            )}
            {benchPhase==="done" && benchmark?.error && (
              <div style={{ background:"#1a1008", border:"1px solid #f5a62333",
                borderRadius:"10px", padding:"16px", color:"#f5c066", fontSize:"14px", fontWeight:600 }}>
                ⚠ {benchmark.error}
              </div>
            )}
            {benchPhase==="error" && (
              <div style={{ background:"#1a1008", border:"1px solid #f5a62333",
                borderRadius:"10px", padding:"16px", color:"#f5c066", fontSize:"14px", fontWeight:600 }}>
                ⚠ Benchmark failed. Try microsoft/vscode or facebook/react.
              </div>
            )}
          </div>
        )}

        {/* ── WATCHLIST ── */}
        {nav==="watchlist" && (
          <div>
            <div style={{ background:"#111", border:"1px solid #222",
              borderRadius:"14px", padding:"24px", marginBottom:"16px" }}>
              <h3 style={{ margin:"0 0 6px", fontSize:"16px", color:"#00ff88", fontWeight:800 }}>
                👁 Add to Watchlist
              </h3>
              <p style={{ fontSize:"13px", color:"#666", margin:"0 0 16px", fontWeight:500 }}>
                Signal detection · 8-second alerts · Auto-tweet on critical signals
              </p>
              <div style={{ display:"flex", flexDirection:"column", gap:"12px" }}>
                <input value={watchEmail} onChange={e=>setWatchEmail(e.target.value)}
                  placeholder="your@email.com"
                  style={{ background:"#1a1a1a", border:"1px solid #333", borderRadius:"10px",
                    padding:"12px 14px", color:"#fff", fontSize:"14px", outline:"none", fontWeight:500 }}
                  onFocus={e=>e.target.style.borderColor="#00ff8877"}
                  onBlur={e=>e.target.style.borderColor="#333"}/>
                <label style={{ display:"flex", alignItems:"center", gap:"10px",
                  fontSize:"14px", color:"#bbb", cursor:"pointer", fontWeight:600 }}>
                  <input type="checkbox" checked={autoTweet} onChange={e=>setAutoTweet(e.target.checked)}
                    style={{ width:"16px", height:"16px", accentColor:"#00ff88" }}/>
                  Auto-tweet when critical signal fires
                </label>
                <button onClick={addToWatchlist} disabled={!url.trim()||!watchEmail.trim()}
                  style={{ background:"linear-gradient(135deg,#00ff88,#00cc66)",
                    color:"#000", border:"none", borderRadius:"10px",
                    padding:"12px", fontSize:"15px", fontWeight:900,
                    cursor:!url.trim()||!watchEmail.trim()?"not-allowed":"pointer",
                    opacity:!url.trim()||!watchEmail.trim()?0.4:1 }}>
                  Start Watching
                </button>
              </div>
              {watchStatus && (
                <div style={{ marginTop:"12px", fontSize:"14px", color:"#00ff88",
                  padding:"10px 14px", background:"#00ff8810", borderRadius:"8px",
                  border:"1px solid #00ff8830", fontWeight:600 }}>
                  {watchStatus}
                </div>
              )}
            </div>

            {watchList.length>0 && (
              <div style={{ background:"#111", border:"1px solid #222", borderRadius:"14px", padding:"20px" }}>
                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"16px" }}>
                  <h3 style={{ margin:0, fontSize:"15px", color:"#fff", fontWeight:800 }}>
                    Currently Watching ({watchList.length})
                  </h3>
                  <button onClick={runWatchlistCheck} disabled={watchChecking}
                    style={{ background:"#0c1a0c", border:"1px solid #00ff8844",
                      borderRadius:"8px", color:"#00ff88", cursor:"pointer",
                      padding:"8px 18px", fontSize:"13px", fontWeight:800 }}>
                    {watchChecking?"🔍 Checking...":"🔍 Run Signal Check Now"}
                  </button>
                </div>
                {watchList.map((w,i)=>(
                  <div key={i} style={{ display:"flex", justifyContent:"space-between",
                    alignItems:"center", padding:"10px 0", borderBottom:"1px solid #1a1a1a", fontSize:"14px" }}>
                    <span style={{ color:"#00ff88", fontWeight:700 }}>{w.repo}</span>
                    <div style={{ display:"flex", gap:"8px", alignItems:"center" }}>
                      {w.auto_tweet && <Badge label="Auto-tweet ON" color="#9b59b6"/>}
                      <span style={{ color:"#555", fontSize:"12px" }}>{w.email}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── SIGNALS ── */}
        {nav==="signals" && (
          <div>
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"16px" }}>
              <div>
                <h3 style={{ margin:"0 0 4px", fontSize:"16px", color:"#fff", fontWeight:800 }}>🚨 Signal Feed</h3>
                <p style={{ margin:0, fontSize:"13px", color:"#666", fontWeight:500 }}>
                  Live detection · 8-second dispatch
                </p>
              </div>
              <button onClick={fetchSignals}
                style={{ background:"transparent", border:"1px solid #2a2a2a",
                  borderRadius:"8px", color:"#aaa", cursor:"pointer",
                  padding:"7px 16px", fontSize:"13px", fontWeight:700 }}>
                ↻ Refresh
              </button>
            </div>

            {signalFeed.length===0 && (
              <div style={{ background:"#111", border:"1px solid #222",
                borderRadius:"14px", padding:"48px", textAlign:"center", color:"#444" }}>
                <div style={{ fontSize:"36px", marginBottom:"12px" }}>📡</div>
                <p style={{ fontSize:"15px", color:"#666", fontWeight:600, marginBottom:"6px" }}>No signals yet.</p>
                <p style={{ fontSize:"13px" }}>
                  1. Add a repo to Watchlist<br/>
                  2. Click "Run Signal Check Now"<br/>
                  3. Signals appear here automatically
                </p>
              </div>
            )}
            {signalFeed.map((s,i)=>(
              <SignalCard key={i} signal={s} onAutoPost={autoPostTweet} autoposting={autoposting}/>
            ))}
            {autopostStatus && (
              <div style={{ fontSize:"14px", color:"#00ff88", padding:"12px 16px",
                background:"#00ff8810", borderRadius:"8px", marginTop:"10px",
                border:"1px solid #00ff8830", fontWeight:600 }}>
                {autopostStatus}
              </div>
            )}
          </div>
        )}

        <div style={{ textAlign:"center", marginTop:"36px", fontSize:"12px", color:"#222", fontWeight:600 }}>
          RepoRadar · TinyFish $2M Pre-Accelerator Hackathon · Zero External LLM · One API Key
        </div>
      </div>
    </div>
  );
}