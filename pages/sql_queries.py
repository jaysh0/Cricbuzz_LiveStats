import streamlit as st
import pandas as pd
from utils.db_connection import get_engine

st.set_page_config(page_title="SQL Interface", page_icon="🔍", layout="wide")
st.title("🔍 Read‑only SQL Interface")

st.info(
    "Run **SELECT** queries on `matches` and `match_scores` only. "
    "Destructive statements are blocked."
)

engine = get_engine()

ALLOWED_TABLES = {"matches", "match_scores"}
BLOCKED_TOKENS = {"insert", "update", "delete", "drop", "alter", "create", "truncate", "grant", "revoke"}

default_q = """\
-- Examples:
-- 1) Recent 20 matches
SELECT match_id, series_name, match_desc, match_format, state, status, team1, team2, start_date
FROM matches
ORDER BY start_date DESC NULLS LAST
LIMIT 20;

-- 2) Join with scores
-- SELECT m.match_desc, s.team_name, s.runs, s.wickets, s.overs
-- FROM match_scores s JOIN matches m ON m.match_id = s.match_id
-- ORDER BY m.start_date DESC NULLS LAST;
"""

sql = st.text_area("SQL (read-only allowed):", value=default_q, height=240)
run = st.button("Run Query", type="primary")

def is_safe(query: str) -> tuple[bool, str]:
    q = " ".join(query.lower().split())
    if not q.strip().startswith("select"):
        return False, "Only SELECT queries are allowed."

    # block dangerous tokens
    for tok in BLOCKED_TOKENS:
        if f" {tok} " in f" {q} ":
            return False, f"Blocked keyword detected: {tok}"

    # whitelist tables
    # crude but effective: ensure referenced table names are allowed
    used_bad = []
    for tbl in ["matches", "match_scores"]:
        pass  # allowed
    # if someone types another table name, catch (simple heuristic)
    for word in q.replace(",", " ").replace("\n", " ").split():
        if word.isidentifier() and word not in {"select","from","join","on","where","and","or","order","by","limit","as"}:
            if word in {"matches","match_scores"}:
                continue
            # rough check: if looks like a table and not aliased as m/s, we warn only if it equals a known blocked token list handled earlier
    # A stricter check: ensure 'from'/'join' targets are allowed
    import re
    for kw in ("from","join"):
        for m in re.finditer(rf"\b{kw}\s+([a-zA-Z_][\w\.]*)", q):
            t = m.group(1).split(".")[-1]
            if t not in ALLOWED_TABLES:
                return False, f"Only tables {ALLOWED_TABLES} are allowed. Found '{t}'."
    return True, ""

if run:
    ok, msg = is_safe(sql)
    if not ok:
        st.error(msg)
    else:
        try:
            df = pd.read_sql(sql, con=engine)
            st.success(f"{len(df)} row(s)")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")
