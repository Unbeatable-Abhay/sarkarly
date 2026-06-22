import { useState } from "react"

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";

// Each tab maps to its own backend route.
const TAB_ROUTES = {
  matcher: `${API_BASE}/scheme_match`,
  legal: `${API_BASE}/legal_advisory`,
  directory: `${API_BASE}/scheme_directory`,
}

const OCCUPATIONS = ["Farmer", "Student", "Daily Wage Worker", "Small Business Owner", "Senior Citizen", "Women"]

const STATES = [
  "Andhra Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Delhi",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
]

const MATCHER_CATEGORIES = ["General", "SC/ST", "OBC", "Women", "Minority"]

const LAND_OPTIONS = ["None", "Less than 2 acres", "2-5 acres", "5+ acres"]

const DIRECTORY_CATEGORIES = ["Agriculture", "Education", "Women", "Health", "Housing", "Employment", "Business"]

// Purely visual landing grid. Picking a card just jumps to the directory
// tab and pre-fills the category - no new backend routes involved.
const LANDING_CATEGORIES = [
  { id: "Housing", label: "Housing", icon: "🏠" },
  { id: "Education", label: "Education", icon: "🎓" },
  { id: "Health", label: "Health", icon: "🩺" },
  { id: "Agriculture", label: "Agriculture", icon: "🌾" },
]

const DISCLAIMER =
  "This information is for awareness purposes only. Please verify through official government portals and consult a legal expert before taking action."

// Convert simple markdown-like text into HTML and extract source links as chips.
function formatAnswer(text) {
  if (!text) return { html: "", links: [] }

  // Collect URLs to render as clickable chips.
  const urlRegex = /(https?:\/\/[^\s)\]]+)/g
  const links = []
  const seen = {}
  let match
  while ((match = urlRegex.exec(text)) !== null) {
    let url = match[1].replace(/[.,;]+$/, "")
    if (!seen[url]) {
      seen[url] = true
      links.push(url)
    }
  }

  let html = text
    // Escape HTML to avoid injection from the backend response.
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")

  // Bold: **text** -> <strong>text</strong>
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
  // Newlines -> <br>
  html = html.replace(/\n/g, "<br>")

  return { html, links }
}

function Spinner() {
  return <span className="spinner" aria-hidden="true" />
}

function ResponseCard({ loading, error, answer }) {
  if (loading) {
    return (
      <div className="response-card loading-card" role="status" aria-live="polite">
        <Spinner />
        <p className="loading-text">Searching official government portals...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="response-card error-card" role="alert">
        <p>Something went wrong. Please try again.</p>
      </div>
    )
  }

  if (!answer) return null

  const { html, links } = formatAnswer(answer)

  return (
    <div className="response-card" aria-live="polite">
      <h3 className="response-title">Result</h3>
      <div className="response-body" dangerouslySetInnerHTML={{ __html: html }} />

      {links.length > 0 && (
        <div className="chips">
          {links.map((url, i) => (
            <a key={i} className="chip" href={url} target="_blank" rel="noopener noreferrer">
              {(() => {
                try {
                  return new URL(url).hostname.replace("www.", "")
                } catch {
                  return "Source"
                }
              })()}
            </a>
          ))}
        </div>
      )}

      <p className="disclaimer">{DISCLAIMER}</p>
    </div>
  )
}

// Static landing section shown above the tabs. Clicking a category card
// jumps straight to the directory tab with that category pre-selected.
function CategoryLanding({ onPickCategory }) {
  return (
    <section className="landing" aria-label="Browse by category">
      <div className="landing-stat">
        <p className="landing-stat-label">Schemes covered</p>
        <p className="landing-stat-value">7 categories</p>
        <p className="landing-stat-sub">Searched live from official government portals</p>
      </div>

      <p className="landing-label">Browse by category</p>
      <div className="category-grid">
        {LANDING_CATEGORIES.map((c) => (
          <button key={c.id} className="category-card" onClick={() => onPickCategory(c.id)}>
            <span className="category-icon" aria-hidden="true">
              {c.icon}
            </span>
            <p className="category-name">{c.label}</p>
            <p className="category-sub">View schemes</p>
          </button>
        ))}
      </div>
    </section>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState("matcher")

  // Scheme Matcher state
  const [occupation, setOccupation] = useState("")
  const [matcherState, setMatcherState] = useState("")
  const [matcherCategory, setMatcherCategory] = useState("")
  const [land, setLand] = useState("")
  const [details, setDetails] = useState("")

  // Legal Advisor state
  const [situation, setSituation] = useState("")

  // Scheme Directory state
  const [dirCategory, setDirCategory] = useState("")
  const [dirState, setDirState] = useState("")

  // Shared request state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)
  const [answer, setAnswer] = useState("")

  async function sendQuery(query, url) {
    setLoading(true)
    setError(false)
    setAnswer("")
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      })
      if (!res.ok) throw new Error("Request failed")
      const data = await res.json()
      setAnswer(data.Answer || "")
    } catch (err) {
      console.log("[v0] Request error:", err.message)
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  function handleMatcherSubmit(e) {
    e.preventDefault()
    const landPart = occupation === "Farmer" ? `${land || "None"}` : "None"
    const query = `I am a ${occupation || "citizen"} from ${matcherState || "India"}, category ${
      matcherCategory || "General"
    }, ${landPart} land. Additional info: ${details || "None"}`
    sendQuery(query, TAB_ROUTES.matcher)
  }

  function handleLegalSubmit(e) {
    e.preventDefault()
    sendQuery(situation, TAB_ROUTES.legal)
  }

  function handleDirectorySubmit(e) {
    e.preventDefault()
    const query = `List all ${dirCategory || "government"} government schemes available in ${
      dirState || "India"
    } with how to apply for each`
    sendQuery(query, TAB_ROUTES.directory)
  }

  function switchTab(tab) {
    setActiveTab(tab)
    setAnswer("")
    setError(false)
    setLoading(false)
  }

  // Used by the category landing cards - jumps to directory tab
  // with that category already chosen.
  function handlePickCategory(categoryId) {
    setDirCategory(categoryId)
    switchTab("directory")
  }

  const tabs = [
    { id: "matcher", label: "Scheme Matcher" },
    { id: "legal", label: "Legal Advisor" },
    { id: "directory", label: "Scheme Directory" },
  ]

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <span className="brand-mark" aria-hidden="true">
              GA
            </span>
            <div className="brand-text">
              <h1 className="brand-title">Gov Awareness</h1>
              <p className="brand-tagline">Empowering citizens with knowledge</p>
            </div>
          </div>
        </div>
      </header>

      <CategoryLanding onPickCategory={handlePickCategory} />

      <nav className="tabs" role="tablist" aria-label="Sections">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`tab ${activeTab === tab.id ? "tab-active" : ""}`}
            onClick={() => switchTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="main">
        {activeTab === "matcher" && (
          <section className="panel" aria-labelledby="matcher-heading">
            <h2 id="matcher-heading" className="panel-title">
              Find Government Schemes For You
            </h2>
            <p className="panel-subtitle">Tell us about yourself and we&apos;ll match you with relevant schemes.</p>

            <form className="form" onSubmit={handleMatcherSubmit}>
              <div className="field">
                <label htmlFor="occupation">Occupation</label>
                <select id="occupation" value={occupation} onChange={(e) => setOccupation(e.target.value)}>
                  <option value="">Select occupation</option>
                  {OCCUPATIONS.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label htmlFor="matcher-state">State</label>
                <select id="matcher-state" value={matcherState} onChange={(e) => setMatcherState(e.target.value)}>
                  <option value="">Select state</option>
                  {STATES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label htmlFor="matcher-category">Category</label>
                <select
                  id="matcher-category"
                  value={matcherCategory}
                  onChange={(e) => setMatcherCategory(e.target.value)}
                >
                  <option value="">Select category</option>
                  {MATCHER_CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              {occupation === "Farmer" && (
                <div className="field">
                  <label htmlFor="land">Land owned</label>
                  <select id="land" value={land} onChange={(e) => setLand(e.target.value)}>
                    <option value="">Select land owned</option>
                    {LAND_OPTIONS.map((l) => (
                      <option key={l} value={l}>
                        {l}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="field field-full">
                <label htmlFor="details">Any additional details? (optional)</label>
                <textarea
                  id="details"
                  rows="3"
                  placeholder="e.g. I have a disability, I am a widow, I run a dairy farm..."
                  value={details}
                  onChange={(e) => setDetails(e.target.value)}
                />
              </div>

              <button type="submit" className="btn" disabled={loading}>
                {loading ? "Searching..." : "Find Matching Schemes"}
              </button>
            </form>

            <ResponseCard loading={loading} error={error} answer={answer} />
          </section>
        )}

        {activeTab === "legal" && (
          <section className="panel" aria-labelledby="legal-heading">
            <h2 id="legal-heading" className="panel-title">
              Know Your Legal Rights
            </h2>
            <p className="panel-subtitle">Describe your situation and learn what rights protect you.</p>

            <form className="form" onSubmit={handleLegalSubmit}>
              <div className="field field-full">
                <label htmlFor="situation">Describe your situation</label>
                <textarea
                  id="situation"
                  rows="5"
                  placeholder="e.g. I got stopped by a police officer while riding my bike..."
                  value={situation}
                  onChange={(e) => setSituation(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn" disabled={loading || !situation.trim()}>
                {loading ? "Searching..." : "Know My Rights"}
              </button>
            </form>

            <ResponseCard loading={loading} error={error} answer={answer} />
          </section>
        )}

        {activeTab === "directory" && (
          <section className="panel" aria-labelledby="directory-heading">
            <h2 id="directory-heading" className="panel-title">
              Browse the Scheme Directory
            </h2>
            <p className="panel-subtitle">Explore schemes by category and state.</p>

            <form className="form" onSubmit={handleDirectorySubmit}>
              <div className="field">
                <label htmlFor="dir-category">Category</label>
                <select id="dir-category" value={dirCategory} onChange={(e) => setDirCategory(e.target.value)}>
                  <option value="">Select category</option>
                  {DIRECTORY_CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label htmlFor="dir-state">State</label>
                <select id="dir-state" value={dirState} onChange={(e) => setDirState(e.target.value)}>
                  <option value="">Select state</option>
                  {STATES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <button type="submit" className="btn" disabled={loading}>
                {loading ? "Searching..." : "Browse Schemes"}
              </button>
            </form>

            <ResponseCard loading={loading} error={error} answer={answer} />
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Data sourced from official Indian government portals</p>
      </footer>
    </div>
  )
}
