import streamlit as st
from datetime import datetime
from utils.db_connection import get_engine
import pandas as pd

st.title("Home")

st.info(
    "Tip: Visit **Live Matches** to pull fresh data from the Cricbuzz RapidAPI and "
    "store it into Postgres, then browse **Top Stats** or the **SQL Interface**."
)

engine = get_engine()

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Latest Matches (table view)")
    try:
        df = pd.read_sql(
            """
            SELECT match_id, series_name, match_desc, match_format, state, status, team1, team2, venue, start_date
            FROM matches
            ORDER BY start_date DESC NULLS LAST
            LIMIT 15
            """,
            con=engine,
        )
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not query DB yet: {e}")

with col2:
    st.subheader("Data Freshness")
    try:
        ts = pd.read_sql("SELECT NOW() AS server_time", con=engine)
        st.metric("DB Time (UTC)", ts.iloc[0,0].strftime("%Y-%m-%d %H:%M:%S"))
    except Exception:
        st.metric("DB Time (UTC)", "—")
