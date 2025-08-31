import requests
import datetime
from utils.db_connection import SessionLocal, Match, MatchScore

API_HOST = "cricbuzz-cricket.p.rapidapi.com"

# Fetch data from Cricbuzz API
def fetch_recent_matches(api_key: str):
    url = f"https://{API_HOST}/matches/v1/recent"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": API_HOST
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

# Insert into DB
def insert_matches(data):
    session = SessionLocal()
    try:
        for match_group in data.get("typeMatches", []):
            for series in match_group.get("seriesMatches", []):
                series_wrapper = series.get("seriesAdWrapper")
                if not series_wrapper:
                    continue

                for m in series_wrapper.get("matches", []):
                    match_info = m.get("matchInfo", {})
                    match_id = str(match_info.get("matchId"))
                    if not match_id:
                        continue

                    # Convert epoch → datetime
                    start_date = datetime.datetime.fromtimestamp(
                        int(match_info.get("startDate", 0)) / 1000
                    ) if match_info.get("startDate") else None

                    end_date = datetime.datetime.fromtimestamp(
                        int(match_info.get("endDate", 0)) / 1000
                    ) if match_info.get("endDate") else None

                    # Insert Match
                    match_obj = Match(
                        match_id=match_id,
                        series_id=match_info.get("seriesId"),
                        series_name=match_info.get("seriesName"),
                        match_desc=match_info.get("matchDesc"),
                        match_format=match_info.get("matchFormat"),
                        start_date=start_date,
                        end_date=end_date,
                        state=match_info.get("state"),
                        status=match_info.get("status"),
                        team1=match_info.get("team1", {}).get("teamName"),
                        team2=match_info.get("team2", {}).get("teamName"),
                        venue=match_info.get("venueInfo", {}).get("ground"),
                        city=match_info.get("venueInfo", {}).get("city"),
                    )
                    session.merge(match_obj)

                    # Insert Scores
                    match_score = m.get("matchScore", {})
                    for team_key in ["team1Score", "team2Score"]:
                        team_score = match_score.get(team_key, {})
                        if "inngs1" in team_score:
                            inn = team_score["inngs1"]
                            score_obj = MatchScore(
                                match_id=match_id,
                                team_name=match_info.get(team_key.replace("Score", ""), {}).get("teamName"),
                                innings=inn.get("inningsId"),
                                runs=inn.get("runs"),
                                wickets=inn.get("wickets"),
                                overs=inn.get("overs")
                            )
                            session.add(score_obj)

        session.commit()
        print("Data inserted successfully")
    except Exception as e:
        session.rollback()
        print(f"DB Insert Error: {e}")
    finally:
        session.close()
