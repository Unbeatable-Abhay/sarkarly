import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { User, WarningCircle, Tray } from "@phosphor-icons/react";
import { getHomeSchemes } from "../api/schemes";
import { useAuth } from "../auth/AuthContext";
import SchemeCard from "../components/SchemeCard";
import BottomNav from "../components/BottomNav";

const TAGLINES = [
  "Discover government schemes you qualify for and understand your legal rights — clearly, in one place.",
  "Turns confusing paperwork into simple, one-tap guidance.",
  "No forms, no fine print — just what applies to you.",
];

function useTypewriter(lines, typeSpeed = 38, deleteSpeed = 22, pauseMs = 1800) {
  const [text, setText] = useState("");

  useEffect(() => {
    let lineIndex = 0;
    let charIndex = 0;
    let deleting = false;
    let timeoutId;

    function tick() {
      const full = lines[lineIndex];

      if (!deleting) {
        charIndex++;
        setText(full.slice(0, charIndex));
        if (charIndex === full.length) {
          deleting = true;
          timeoutId = setTimeout(tick, pauseMs);
          return;
        }
      } else {
        charIndex--;
        setText(full.slice(0, charIndex));
        if (charIndex === 0) {
          deleting = false;
          lineIndex = (lineIndex + 1) % lines.length;
        }
      }
      timeoutId = setTimeout(tick, deleting ? deleteSpeed : typeSpeed);
    }

    tick();
    return () => clearTimeout(timeoutId);
  }, [lines, typeSpeed, deleteSpeed, pauseMs]);

  return text;
}

function SkeletonFeed() {
  return (
    <div className="scheme-feed">
      <div className="skeleton skeleton--featured" />
      <div className="scheme-grid">
        <div className="skeleton skeleton--grid" />
        <div className="skeleton skeleton--grid" />
        <div className="skeleton skeleton--grid" />
        <div className="skeleton skeleton--grid" />
      </div>
    </div>
  );
}

function HomePage() {
  const [schemes, setSchemes] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | ready | error
  const navigate = useNavigate();
  const { user } = useAuth();
  const tagline = useTypewriter(TAGLINES);

  const initial = (
    user?.user_metadata?.full_name ||
    user?.user_metadata?.name ||
    user?.email ||
    "?"
  ).trim()[0].toUpperCase();

  useEffect(() => {
    getHomeSchemes()
      .then((data) => {
        setSchemes(data.schemes || []);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  function openScheme(schemeName) {
    navigate(`/home/scheme/${encodeURIComponent(schemeName)}`);
  }

  return (
    <div className="page">
      <header className="home-header">
        <div>
          <p className="home-header__brand">Sarkarly</p>
          <p className="home-header__tagline" aria-live="polite">
            {tagline}
            <span className="home-header__cursor" aria-hidden="true" />
          </p>
        </div>
        <Link to="/profile" className="home-header__profile" aria-label="Profile">
          {user ? (
            <span className="home-header__initial">{initial}</span>
          ) : (
            <User size={16} color="var(--color-text-muted)" />
          )}
        </Link>
      </header>

      <div className="page__content">
        <div className="section-label">
          <span>Schemes for you</span>
          <span className="section-label__hint">Refreshes often</span>
        </div>

        <div className="scroll-area">
          {status === "loading" && <SkeletonFeed />}

          {status === "error" && (
            <div className="message-card">
              <WarningCircle size={22} color="var(--color-seal)" />
              <p>Couldn't load schemes right now. Please try again.</p>
            </div>
          )}

          {status === "ready" && schemes.length === 0 && (
            <div className="message-card">
              <Tray size={22} color="var(--color-text-muted)" />
              <p>No schemes available right now. Please check back soon.</p>
            </div>
          )}

          {status === "ready" && schemes.length > 0 && (
            <div className="scheme-feed">
              <SchemeCard
                scheme={schemes[0]}
                onClick={() => openScheme(schemes[0].scheme_name)}
                variant="featured"
              />
              <div className="scheme-grid">
                {schemes.slice(1).map((scheme, i) => (
                  <SchemeCard
                    key={scheme.scheme_name}
                    scheme={scheme}
                    onClick={() => openScheme(scheme.scheme_name)}
                    variant={(i + 1) % 3 === 0 ? "wide" : "compact"}
                  />
                ))}
              </div>
            </div>
          )}

          {status === "ready" && schemes.length > 0 && <div className="scroll-fade" />}
        </div>
      </div>

      <BottomNav />
    </div>
  );
}

export default HomePage;