import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
import "./App.css"

const root = ReactDOM.createRoot(document.getElementById("root"))
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

/* ── Register Service Worker (PWA) ─────────────────────── */
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js", { scope: "/" })
      .then(reg => {
        console.log("[SW] Registered:", reg.scope)
        reg.onupdatefound = () => {
          const installing = reg.installing
          if (!installing) return
          installing.onstatechange = () => {
            if (installing.state === "installed" && navigator.serviceWorker.controller) {
              console.log("[SW] New content available — refresh to update.")
            }
          }
        }
      })
      .catch(err => console.warn("[SW] Registration failed:", err))
  })
}
