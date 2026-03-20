"""Shared visual styling helpers for the Streamlit UI."""

from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    """Apply the SingNote visual system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        :root {
          --sn-ink: #1f2937;
          --sn-muted: #5b6475;
          --sn-paper: #f6f0e6;
          --sn-card: rgba(255, 251, 245, 0.88);
          --sn-line: rgba(46, 58, 78, 0.12);
          --sn-accent: #b6642c;
          --sn-accent-soft: rgba(182, 100, 44, 0.12);
          --sn-forest: #2d5a4c;
          --sn-shadow: 0 16px 48px rgba(36, 33, 28, 0.10);
        }

        .stApp {
          background:
            radial-gradient(
              circle at top left,
              rgba(182, 100, 44, 0.16),
              transparent 32%
            ),
            radial-gradient(
              circle at top right,
              rgba(45, 90, 76, 0.14),
              transparent 28%
            ),
            repeating-linear-gradient(
              to bottom,
              transparent 0,
              transparent 39px,
              rgba(46, 58, 78, 0.05) 39px,
              rgba(46, 58, 78, 0.05) 40px
            ),
            var(--sn-paper);
          color: var(--sn-ink);
        }

        html, body, [class*="css"] {
          font-family: "IBM Plex Sans", sans-serif;
        }

        h1, h2, h3, h4 {
          font-family: "Fraunces", serif;
          color: var(--sn-ink);
          letter-spacing: -0.03em;
        }

        [data-testid="stHeader"] {
          background: transparent;
        }

        [data-testid="stAppViewContainer"] > .main {
          background: transparent;
        }

        .block-container {
          max-width: 1120px;
          padding-top: 1.5rem;
          padding-bottom: 4rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
          border: 1px solid var(--sn-line);
          border-radius: 24px;
          background: var(--sn-card);
          box-shadow: var(--sn-shadow);
        }

        div[data-testid="stExpander"] {
          border-radius: 24px;
          border: 1px solid var(--sn-line);
          background: rgba(255, 251, 245, 0.78);
          box-shadow: var(--sn-shadow);
        }

        div[data-testid="stMetric"] {
          background: rgba(255, 251, 245, 0.82);
          border: 1px solid var(--sn-line);
          border-radius: 22px;
          padding: 0.75rem;
          box-shadow: var(--sn-shadow);
        }

        .stButton > button,
        .stForm button,
        [data-testid="baseButton-secondary"] {
          border-radius: 999px;
          border: 1px solid transparent;
          background: linear-gradient(135deg, var(--sn-ink), #314057);
          color: white;
          min-height: 2.9rem;
          font-weight: 600;
          box-shadow: 0 10px 24px rgba(31, 41, 55, 0.18);
        }

        .stButton > button:hover,
        .stForm button:hover {
          border-color: rgba(255, 255, 255, 0.18);
          background: linear-gradient(135deg, #18202d, #2a3549);
        }

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox select {
          border-radius: 18px;
          background: rgba(255, 251, 245, 0.92);
        }

        .stTabs [data-baseweb="tab-list"] {
          gap: 0.35rem;
          padding: 0.35rem;
          border-radius: 999px;
          background: rgba(31, 41, 55, 0.06);
        }

        .stTabs [data-baseweb="tab"] {
          border-radius: 999px;
          min-height: 2.6rem;
          padding: 0 1rem;
        }

        .stTabs [aria-selected="true"] {
          background: linear-gradient(135deg, var(--sn-accent), #cc7a3f);
          color: white;
        }

        .sn-hero {
          padding: 1.35rem 1.4rem;
          border: 1px solid var(--sn-line);
          border-radius: 28px;
          background: linear-gradient(
            140deg,
            rgba(255, 251, 245, 0.94),
            rgba(248, 238, 223, 0.88)
          );
          box-shadow: var(--sn-shadow);
          margin-bottom: 1rem;
        }

        .sn-kicker {
          text-transform: uppercase;
          letter-spacing: 0.16em;
          font-size: 0.73rem;
          color: var(--sn-forest);
          font-weight: 600;
          margin-bottom: 0.5rem;
        }

        .sn-hero h1 {
          margin: 0 0 0.45rem;
          font-size: clamp(2.25rem, 5vw, 4.6rem);
        }

        .sn-hero p {
          margin: 0;
          max-width: 42rem;
          color: var(--sn-muted);
          font-size: 1rem;
          line-height: 1.65;
        }

        .sn-badge-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.55rem;
          margin-top: 1rem;
        }

        .sn-badge {
          border-radius: 999px;
          padding: 0.45rem 0.8rem;
          background: var(--sn-accent-soft);
          color: var(--sn-ink);
          font-size: 0.85rem;
          font-weight: 600;
        }

        .sn-song-sheet {
          border: 1px solid var(--sn-line);
          border-radius: 28px;
          background:
            linear-gradient(
              180deg,
              rgba(255, 251, 245, 0.98),
              rgba(249, 241, 229, 0.94)
            );
          box-shadow: var(--sn-shadow);
          padding: 1.25rem 1rem 1.35rem;
        }

        .sn-sheet-section + .sn-sheet-section {
          margin-top: 1.4rem;
          padding-top: 1.25rem;
          border-top: 1px dashed rgba(46, 58, 78, 0.12);
        }

        .sn-sheet-section-title {
          display: inline-block;
          margin-bottom: 0.85rem;
          padding: 0.25rem 0.55rem;
          border-radius: 999px;
          background: rgba(182, 100, 44, 0.12);
          color: var(--sn-forest);
          font-size: 0.73rem;
          font-weight: 700;
          letter-spacing: 0.12em;
          text-transform: uppercase;
        }

        .sn-sheet-line + .sn-sheet-line {
          margin-top: 0.95rem;
        }

        .sn-sheet-chords {
          display: flex;
          flex-wrap: wrap;
          gap: 0.45rem;
          margin-bottom: 0.22rem;
          color: var(--sn-accent);
          font-family: "IBM Plex Sans", sans-serif;
          font-size: 0.82rem;
          font-weight: 700;
          line-height: 1.35;
        }

        .sn-sheet-chord {
          white-space: nowrap;
        }

        .sn-sheet-lyric {
          color: var(--sn-ink);
          font-family: "Fraunces", serif;
          font-size: clamp(1.05rem, 2vw, 1.3rem);
          line-height: 1.4;
        }

        .sn-melody-package {
          min-height: 6.2rem;
          margin-bottom: 0.35rem;
          border: 1px solid rgba(46, 58, 78, 0.10);
          border-radius: 16px;
          background: rgba(255, 251, 245, 0.94);
          padding: 0.7rem 0.75rem 0.8rem;
        }

        .sn-melody-package-notes {
          color: #7b8494;
          font-family: "IBM Plex Sans", sans-serif;
          font-size: 0.74rem;
          letter-spacing: 0.14em;
          line-height: 1.35;
          margin-bottom: 0.55rem;
          text-transform: uppercase;
        }

        .sn-melody-package-text {
          color: var(--sn-ink);
          font-family: "Fraunces", serif;
          font-size: clamp(0.95rem, 1.5vw, 1.18rem);
          line-height: 1.25;
          word-break: break-word;
        }

        @media (max-width: 720px) {
          .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
          }

          .sn-song-sheet {
            padding: 1rem 0.85rem 1.1rem;
          }

          .sn-sheet-lyric {
            font-size: 1.02rem;
          }

          .sn-melody-package {
            min-height: 5.4rem;
            padding: 0.62rem 0.68rem 0.72rem;
          }

          .sn-melody-package-notes {
            font-size: 0.7rem;
            letter-spacing: 0.1em;
            margin-bottom: 0.45rem;
          }

          .sn-melody-package-text {
            font-size: 0.98rem;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(song_count: int) -> None:
    """Render the main app introduction block."""
    st.markdown(
        f"""
        <section class="sn-hero">
          <div class="sn-kicker">Shared practice workspace</div>
          <h1>SingNote</h1>
          <p>
            A mobile-first lesson board for harmony, melody, and rhythm
            dictation. Keep one shared login, open a song card, and adjust
            notes in place while teaching.
          </p>
          <div class="sn-badge-row">
            <span class="sn-badge">{song_count} song card(s)</span>
            <span class="sn-badge">Package-based melody editing</span>
            <span class="sn-badge">SQLite-backed local persistence</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
