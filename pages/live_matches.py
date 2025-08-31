import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils.db_connection import get_engine
from utils.api_client import fetch_recent_matches, insert_matches

st.set_page_config(page_title="Live Matches", page_icon="🟢", layout="wide")
st.title("Live Matches")

engine = get_engine()
api_key = "02625ba88bmsh71fe116f7a248c4p13458fjsn3fb967658caa"

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### Refresh & Ingestion")
    auto = st.toggle("Auto‑refresh", value=False)
    interval = st.slider("Refresh every (seconds)", 10, 120, 30, help="How often to refresh the page")
    st.caption("Auto‑refresh only updates the page. Use the button below to pull fresh data from the API.")

    pull_now = st.button("Fetch from API & store ➜", type="primary", use_container_width=True)

# Trigger periodic refresh (non-blocking, keeps state)
if auto:
    st_autorefresh(interval=interval * 1000, key="live_refresh")

# ---------------- Actions ----------------
if not api_key:
    st.warning("`RAPIDAPI_KEY` not found in `.env`. Live fetch will be disabled.")

if pull_now:
    if not api_key:
        st.error("Add RAPIDAPI_KEY to your .env and restart the app.")
    else:
        with st.spinner("Fetching from Cricbuzz RapidAPI and storing in Postgres..."):
            data = fetch_recent_matches(api_key)
            insert_matches(data)
        st.success("Data refreshed and saved")

# ---------------- Views ----------------
st.subheader("In‑Progress & Recent Matches")
q_matches = """
SELECT
  m.match_id, m.series_name, m.match_desc, m.match_format, m.state, m.status,
  m.team1, m.team2, m.venue, m.city, m.start_date
FROM matches m
ORDER BY
  CASE WHEN m.state IN ('In Progress','Live') THEN 0 ELSE 1 END,
  m.start_date DESC NULLS LAST
LIMIT 50;
"""
try:
    df_matches = pd.read_sql(q_matches, con=engine)
    st.dataframe(df_matches, use_container_width=True, height=420)
except Exception as e:
    st.error(f"Failed to load matches: {e}")

st.subheader("Scorecards (joined with `match_scores`)")
q_scores = """
SELECT
  m.match_desc, m.match_format, m.state, m.status,
  s.team_name, s.innings, s.runs, s.wickets, s.overs,
  m.start_date, m.series_name, m.match_id
FROM match_scores s
JOIN matches m ON m.match_id = s.match_id
ORDER BY
  CASE WHEN m.state IN ('In Progress','Live') THEN 0 ELSE 1 END,
  m.start_date DESC NULLS LAST, s.team_name, s.innings;
"""
try:
    df_scores = pd.read_sql(q_scores, con=engine)
    st.dataframe(df_scores, use_container_width=True, height=520)
except Exception as e:
    st.error(f"Failed to load scorecards: {e}")

