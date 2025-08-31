import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.db_connection import get_engine

st.set_page_config(page_title="Top Stats", page_icon="📊", layout="wide")
st.title("📊 Top Statistics")

engine = get_engine()

# Helper: convert "overs" like 19.6 (19 overs + 6 balls) → balls integer
def overs_to_balls(overs_float):
    if overs_float is None:
        return None
    o = int(overs_float)
    balls_part = int(round((overs_float - o) * 10))
    # cap at 6
    balls_part = min(balls_part, 6)
    return o * 6 + balls_part

@st.cache_data(ttl=30)
def load_scores():
    q = """
    SELECT s.*, m.match_desc, m.match_format, m.state, m.start_date
    FROM match_scores s
    JOIN matches m ON m.match_id = s.match_id
    """
    df = pd.read_sql(q, con=engine)
    return df

df = load_scores()
if df.empty:
    st.warning("No data yet. Go to **Live Matches** and click *Fetch from API & Store*.")
    st.stop()

# Compute run rate (per over)
df["balls"] = df["overs"].apply(overs_to_balls)
df["run_rate"] = np.where(df["balls"] > 0, df["runs"] / (df["balls"] / 6.0), np.nan)

colA, colB = st.columns(2)

with colA:
    st.subheader("Top 10 Innings by Runs")
    top_runs = df.sort_values("runs", ascending=False).head(10)
    fig1 = px.bar(top_runs, x="team_name", y="runs", color="match_format",
                  hover_data=["match_desc", "state", "start_date"])
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    st.subheader("Best Run Rates (>= 60 balls)")
    rr = df[(df["balls"] >= 60) & df["run_rate"].notna()].sort_values("run_rate", ascending=False).head(10)
    fig2 = px.bar(rr, x="team_name", y="run_rate", color="match_format",
                  hover_data=["runs", "wickets", "match_desc"])
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Format-wise Summary")
summary = (
    df.groupby("match_format")
      .agg(innings=("id", "count"),
           avg_runs=("runs", "mean"),
           avg_rr=("run_rate", "mean"))
      .reset_index()
      .sort_values("innings", ascending=False)
)
st.dataframe(summary, use_container_width=True)
