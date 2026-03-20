"""Home page UI for the bootstrapped application."""

from __future__ import annotations

import streamlit as st

from singnote.bootstrap import Application


def render_home_page(app: Application) -> None:
    """Render the initial landing page for the application."""
    st.set_page_config(
        page_title=app.settings.app_name,
        page_icon="🎵",
        layout="wide",
    )
    st.title("SingNote")
    st.caption("Structured singing practice for student and teacher.")

    songs = app.repository.list_songs()
    st.subheader("Song Catalog")
    if not songs:
        st.info(
            "No songs are available yet. The authoring workflow will populate "
            "this catalog in the next task."
        )
        return

    for song in songs:
        st.markdown(f"### {song.title}")
        if song.artist:
            st.write(song.artist)
        if song.description:
            st.caption(song.description)
