import { useState } from "react"
import "./App.css"

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000"

const TAB_ROUTES = {
  matcher: `${API_BASE}/scheme_match`,
  legal: `${API_BASE}/legal_advisory`,
  directory: `${API_BASE}/scheme_directory`,
}

const OCCUPATIONS = [
  "Farmer", "Student", "Daily Wage Worker",
  "Small Business Owner", "Senior Citizen", "Women",
]

const STATES = [
  "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Delhi",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
  "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
  "Meghalaya", "Odisha", "Punjab", "Rajasthan", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
]

const MATCHER_CATEGORIES = ["General", "SC/ST", "OBC", "Women", "Minority"]
const LAND_OPTIONS = ["None", "Less than 2 acres", "2–5 acres", "5+ acres"]
const DIRECTORY_CATEGORIES = ["Agriculture", "Education", "Women", "Health", "Housing", "Employment", "Business"]

const LANDING_CARDS = [
  { id: "Housing",    label: "Housing",    icon: "🏠", color: "#E8F4FD" },
  { id: "Education",  label: "Education",  icon: "🎓", color: "#EDF7ED" },
  { id: "Health",     label: "Health",     icon: "🩺", color: "#FEF3F2" },
  { id: "Agriculture",label: "Agriculture",icon: "🌾", color: "#FEF9E8" },
  { id: "Employment", label: "Employment", icon: "💼", color: "#F3EFFE" },
  { id: "Business",   label: "Business",   icon: "📊", color: "#E8F8F5" },
]

const DISCLAIMER = "For awareness only. Verify through official government portals before applying."

function LinkChip({ url, label }) {
  let host = label
  if (!host) {
    try { host = new URL(url).hostname.replace("www.", "") } catch { host = "Source" }
  }
  return (
    <a className="chip" href={url} target="_blank" rel="noopener noreferrer">{host}</a>
  )
}

function Spinner() {
  return (
    <div className="spinner-wrap">
      <div className="ios-spinner" />
      <p className="spinner-label">Searching official portals…</p>
    </div>
  )
}

function ResponseCard({ loading, error, result, type }) {
  if (loading) return <Spinner />
  if (error) {
    return (
      <div className="result-card result-error">
        <span className="result-error-icon">⚠️</span>
        <p>Something went wrong. Please try again.</p>
      </div>
    )
  }
  if (!result) return null
  if (type === "legal") return <LegalResultCard result={result} />
  return <SchemeResultCard result={result} />
}

function SchemeResultCard({ result }) {
  const schemes = result.schemes || []

  if (schemes.length === 0) {
    return (
      <div className="result-card">
        <div className="result-body">No matching schemes found. Try adjusting your details.</div>
      </div>
    )
  }

  return (
    <div className="result-list">
      {schemes.map((s, i) => (
        <div className="result-card" key={i}>
          <div className="result-header">
            <span className="result-dot" />
            <span className="result-title">{s.scheme_name}</span>
          </div>

          {(s.category || s.ministry) && (
            <div className="scheme-meta">
              {s.category && <span className="meta-tag">{s.category}</span>}
              {s.ministry && <span className="meta-tag meta-tag-muted">{s.ministry}</span>}
            </div>
          )}

          {s.description && <div className="result-body">{s.description}</div>}

          {s.eligibility?.length > 0 && (
            <div className="result-section">
              <p className="result-section-label">Who Can Apply</p>
              <ul className="result-ul">
                {s.eligibility.map((e, j) => <li key={j}>{e}</li>)}
              </ul>
            </div>
          )}

          {s.benefits?.length > 0 && (
            <div className="result-section">
              <p className="result-section-label">Benefits</p>
              <ul className="result-ul">
                {s.benefits.map((b, j) => <li key={j}>{b}</li>)}
              </ul>
            </div>
          )}

          {s.how_to_apply?.steps?.length > 0 && (
            <div className="result-section">
              <p className="result-section-label">
                How to Apply{s.how_to_apply.mode ? ` (${s.how_to_apply.mode})` : ""}
              </p>
              <ol className="result-ol">
                {s.how_to_apply.steps.map((step, j) => <li key={j}>{step}</li>)}
              </ol>
            </div>
          )}

          {s.documents_required?.length > 0 && (
            <div className="result-section">
              <p className="result-section-label">Documents Required</p>
              <ul className="result-ul">
                {s.documents_required.map((d, j) => <li key={j}>{d}</li>)}
              </ul>
            </div>
          )}

          {(s.official_link || s.application_link) && (
            <div className="result-links">
              <p className="result-links-label">Links</p>
              <div className="chips">
                {s.official_link && <LinkChip url={s.official_link} label="Official Portal" />}
                {s.application_link && <LinkChip url={s.application_link} label="Apply Now" />}
              </div>
            </div>
          )}
        </div>
      ))}
      <p className="disclaimer">{result.disclaimer || DISCLAIMER}</p>
    </div>
  )
}

function LegalResultCard({ result }) {
  return (
    <div className="result-card">
      <div className="result-header">
        <span className="result-dot" />
        <span className="result-title">{result.topic || "Result"}</span>
      </div>

      {result.explanation && <div className="result-body">{result.explanation}</div>}

      {result.citizen_rights?.length > 0 && (
        <div className="result-section">
          <p className="result-section-label">Your Rights</p>
          <ul className="result-ul">
            {result.citizen_rights.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </div>
      )}

      {result.authority_limits?.length > 0 && (
        <div className="result-section">
          <p className="result-section-label">Limits on Authority</p>
          <ul className="result-ul">
            {result.authority_limits.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </div>
      )}

      {result.relevant_provisions?.length > 0 && (
        <div className="result-section">
          <p className="result-section-label">Relevant Legal Provisions</p>
          <ul className="result-ul">
            {result.relevant_provisions.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </div>
      )}

      {result.sources?.length > 0 && (
        <div className="result-links">
          <p className="result-links-label">Sources</p>
          <div className="chips">
            {result.sources.map((url, i) => <LinkChip url={url} key={i} />)}
          </div>
        </div>
      )}

      <p className="disclaimer">{result.disclaimer || DISCLAIMER}</p>
    </div>
  )
}

function SelectField({ id, label, value, onChange, options, placeholder }) {
  return (
    <div className="field">
      <label className="field-label" htmlFor={id}>{label}</label>
      <div className="select-wrap">
        <select id={id} className="ios-select" value={value} onChange={e => onChange(e.target.value)}>
          <option value="">{placeholder}</option>
          {options.map(o => <option key={o} value={o}>{o}</option>)}
        </select>
        <span className="select-arrow">›</span>
      </div>
    </div>
  )
}

function MatcherTab({ loading, error, result, onSubmit }) {
  const [occupation, setOccupation] = useState("")
  const [state, setState] = useState("")
  const [category, setCategory] = useState("")
  const [land, setLand] = useState("")
  const [details, setDetails] = useState("")

  function handleSubmit(e) {
    e.preventDefault()
    const landPart = occupation === "Farmer" ? (land || "None") : "None"
    const query = `I am a ${occupation || "citizen"} from ${state || "India"}, category ${category || "General"}, ${landPart} land. Additional info: ${details || "None"}`
    onSubmit(query, TAB_ROUTES.matcher)
  }

  return (
    <div className="tab-panel">
      <div className="panel-header">
        <h2 className="panel-title">Find Schemes For You</h2>
        <p className="panel-subtitle">Tell us about yourself and we'll match you with relevant government schemes.</p>
      </div>
      <form className="ios-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <SelectField id="occupation" label="Occupation" value={occupation} onChange={setOccupation}
            options={OCCUPATIONS} placeholder="Select occupation" />
          <SelectField id="state" label="State" value={state} onChange={setState}
            options={STATES} placeholder="Select state" />
          <SelectField id="category" label="Category" value={category} onChange={setCategory}
            options={MATCHER_CATEGORIES} placeholder="Select category" />
          {occupation === "Farmer" && (
            <SelectField id="land" label="Land Owned" value={land} onChange={setLand}
              options={LAND_OPTIONS} placeholder="Select land owned" />
          )}
          <div className="field">
            <label className="field-label" htmlFor="details">Additional Details <span className="field-optional">(optional)</span></label>
            <textarea id="details" className="ios-textarea" rows={3}
              placeholder="e.g. I have a disability, I am a widow, I run a dairy farm…"
              value={details} onChange={e => setDetails(e.target.value)} />
          </div>
        </div>
        <button type="submit" className="ios-btn" disabled={loading}>
          {loading ? "Searching…" : "Find Matching Schemes"}
        </button>
      </form>
      <ResponseCard loading={loading} error={error} result={result} type="scheme" />
    </div>
  )
}

function LegalTab({ loading, error, result, onSubmit }) {
  const [situation, setSituation] = useState("")

  function handleSubmit(e) {
    e.preventDefault()
    onSubmit(situation, TAB_ROUTES.legal)
  }

  return (
    <div className="tab-panel">
      <div className="panel-header">
        <h2 className="panel-title">Know Your Rights</h2>
        <p className="panel-subtitle">Describe your situation and learn what legal protections apply to you.</p>
      </div>
      <form className="ios-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <div className="field">
            <label className="field-label" htmlFor="situation">Describe your situation</label>
            <textarea id="situation" className="ios-textarea" rows={5}
              placeholder="e.g. A police officer stopped me while riding my bike and asked for documents…"
              value={situation} onChange={e => setSituation(e.target.value)} required />
          </div>
        </div>
        <button type="submit" className="ios-btn" disabled={loading || !situation.trim()}>
          {loading ? "Searching…" : "Know My Rights"}
        </button>
      </form>
      <ResponseCard loading={loading} error={error} result={result} type="legal" />
    </div>
  )
}

function DirectoryTab({ loading, error, result, onSubmit, initCategory }) {
  const [category, setCategory] = useState(initCategory || "")
  const [state, setState] = useState("")

  function handleSubmit(e) {
    e.preventDefault()
    const query = `List all ${category || "government"} government schemes available in ${state || "India"} with how to apply for each`
    onSubmit(query, TAB_ROUTES.directory)
  }

  return (
    <div className="tab-panel">
      <div className="panel-header">
        <h2 className="panel-title">Scheme Directory</h2>
        <p className="panel-subtitle">Browse and explore schemes by category and state.</p>
      </div>
      <form className="ios-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <SelectField id="dir-category" label="Category" value={category} onChange={setCategory}
            options={DIRECTORY_CATEGORIES} placeholder="Select category" />
          <SelectField id="dir-state" label="State" value={state} onChange={setState}
            options={STATES} placeholder="All of India" />
        </div>
        <button type="submit" className="ios-btn" disabled={loading}>
          {loading ? "Searching…" : "Browse Schemes"}
        </button>
      </form>
      <ResponseCard loading={loading} error={error} result={result} type="scheme" />
    </div>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState("home")
  const [directoryCategory, setDirectoryCategory] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)
  const [result, setResult] = useState(null)

  async function sendQuery(query, url) {
    setLoading(true)
    setError(false)
    setResult(null)
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      })
      const data = await res.json()
      if (!res.ok || data.error) throw new Error(data.error || "Request failed")
      setResult(data)
    } catch (err) {
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  function switchTab(tab) {
    setActiveTab(tab)
    setResult(null)
    setError(false)
    setLoading(false)
  }

  function handlePickCategory(id) {
    setDirectoryCategory(id)
    switchTab("directory")
  }

  const tabs = [
    { id: "home",      label: "Home",      icon: "⊞" },
    { id: "matcher",   label: "Schemes",   icon: "✦" },
    { id: "legal",     label: "Legal",     icon: "⚖" },
    { id: "directory", label: "Directory", icon: "☰" },
  ]

  return (
    <div className="app">
      <div className="nav-bar">
        <div className="nav-inner">
          <div className="nav-brand">
            <div className="nav-logo">S</div>
            <span className="nav-title">Sarkarly</span>
          </div>
          <nav className="nav-links">
            {tabs.map(tab => (
              <button key={tab.id} className={`nav-link ${activeTab === tab.id ? "nav-link-active" : ""}`}
                onClick={() => switchTab(tab.id)}>
                {tab.label}
              </button>
            ))}
          </nav>
          <span className="nav-badge">India</span>
        </div>
      </div>

      <main className="main-content">
        {activeTab === "home" && (
          <div className="home-view">
            <div className="hero">
              <p className="hero-eyebrow">For Every Indian Citizen</p>
              <h1 className="hero-title">Your Government<br />Rights & Schemes</h1>
              <p className="hero-sub">Discover schemes you qualify for, understand your legal rights, and get step-by-step guidance — all in one place.</p>
            </div>

            <div className="quick-actions">
              <button className="quick-card quick-primary" onClick={() => switchTab("matcher")}>
                <span className="quick-icon">✦</span>
                <div className="quick-text">
                  <span className="quick-label">Scheme Matcher</span>
                  <span className="quick-desc">Find what you qualify for</span>
                </div>
                <span className="quick-arrow">›</span>
              </button>
              <button className="quick-card quick-secondary" onClick={() => switchTab("legal")}>
                <span className="quick-icon">⚖</span>
                <div className="quick-text">
                  <span className="quick-label">Legal Advisor</span>
                  <span className="quick-desc">Know your rights</span>
                </div>
                <span className="quick-arrow">›</span>
              </button>
            </div>

            <div className="section">
              <div className="section-header">
                <span className="section-title">Browse by Category</span>
                <button className="section-link" onClick={() => switchTab("directory")}>See all ›</button>
              </div>
              <div className="category-grid">
                {LANDING_CARDS.map(c => (
                  <button key={c.id} className="category-card"
                    style={{ "--card-color": c.color }}
                    onClick={() => handlePickCategory(c.id)}>
                    <span className="cat-icon">{c.icon}</span>
                    <span className="cat-label">{c.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="section">
              <div className="stats-row">
                <div className="stat-item">
                  <span className="stat-num">7</span>
                  <span className="stat-label">Categories</span>
                </div>
                <div className="stat-divider" />
                <div className="stat-item">
                  <span className="stat-num">25+</span>
                  <span className="stat-label">States</span>
                </div>
                <div className="stat-divider" />
                <div className="stat-item">
                  <span className="stat-num">Live</span>
                  <span className="stat-label">Data</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "matcher" && (
          <MatcherTab loading={loading} error={error} result={result} onSubmit={sendQuery} />
        )}
        {activeTab === "legal" && (
          <LegalTab loading={loading} error={error} result={result} onSubmit={sendQuery} />
        )}
        {activeTab === "directory" && (
          <DirectoryTab loading={loading} error={error} result={result}
            onSubmit={sendQuery} initCategory={directoryCategory} />
        )}
      </main>

      <nav className="tab-bar">
        {tabs.map(tab => (
          <button key={tab.id} className={`tab-item ${activeTab === tab.id ? "tab-active" : ""}`}
            onClick={() => switchTab(tab.id)}>
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}