import streamlit as st

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="",
    layout="wide",
)

st.title("LiveStats")
st.markdown(
    """
Welcome to **Cricbuzz LiveStats** — a live cricket analytics dashboard.

**What you can do**
-Live Scorecards*: See in‑progress and recent matches.
-Top Statistics*: Quick visuals from stored innings.
-SQL Interface*: Run read‑only SQL on `matches` & `match_scores`.

Use the left **Pages** sidebar to navigate.
"""
)
