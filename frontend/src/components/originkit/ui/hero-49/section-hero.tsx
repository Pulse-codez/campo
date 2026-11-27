// Delivered by Originkit · stack: nextjs · styling: tailwind
/* eslint-disable */
// @ts-nocheck
"use client"
import FibreArc from "@/components/originkit/ui/hero-49/fibre-arc";

export function SectionHero() {
  return (
    <div className="hero-49">
    <>
      <div id="fibre">
        <FibreArc
          background="#01030A"
          baseColor="#1B4FD8"
          accentColor="#6FC8FF"
          highlight="#FFFFFF"
          density={26}
          speed={100}
          direction={0}
          hover={200}
          reach={23}
          bundle={{ curve: 20, spread: 100, thickness: 100, comb: 170 }}
          style={{ width: "100%", height: "100%" }}
        />
      </div>
      <div className="scrim" />
      <header className="nav">
        <div className="brand">Campus Support</div>
        <nav className="links">
          <a href="#features">What you can do</a>
          <a href="#conditions">Topics</a>
          <a href="#facts">How it is built</a>
          <a href="/register">Sign up</a>
        </nav>
        <a className="cta" href="/login">
          Log in
        </a>
      </header>
      <main className="hero">
        <span className="eyebrow">
          <b>Confidential</b>Student-led · Free
        </span>
        <h1>
          Support that meets you where you are, <em>on campus.</em>
        </h1>
        <p className="sub">
          A private space for university students in Kenya to find campus
          resources, plan around your energy, and reach a human when you need
          one — no judgment, no waiting.
        </p>
        <div className="buttons">
          <a className="btn" href="/register">
            Get support{" "}
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
            >
              <path d="M3 8h10M9 4l4 4-4 4" />
            </svg>
          </a>
          <a className="link" href="#facts">
            <i>
              <svg width="10" height="12" viewBox="0 0 10 12" fill="#6FC8FF">
                <path d="M0 0l10 6-10 6z" />
              </svg>
            </i>
            How it keeps you safe
          </a>
        </div>
        <div className="sources">
          <span>Resources</span>
          <ul>
            <li>Counselling</li>
            <li>Health clinic</li>
            <li>Peer support</li>
            <li>Legal aid</li>
            <li>Emergency</li>
          </ul>
        </div>
      </main>
    </>
    </div>
  );
}
