import os
from utils.db_connection import *
from utils.api_client import fetch_recent_matches, insert_matches


def main():
    init_db()
    API_KEY = "02625ba88bmsh71fe116f7a248c4p13458fjsn3fb967658caa"

    if not API_KEY:
        raise ValueError("RAPIDAPI_KEY not found in .env")

    print("Fetching recent matches...")
    data = fetch_recent_matches(API_KEY)
    insert_matches(data)

if __name__ == "__main__":
    main()
