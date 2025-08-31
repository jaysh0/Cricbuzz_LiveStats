from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Load env vars (DATABASE_URL)
load_dotenv()
DATABASE_URL="postgresql://appuser:appsecret@localhost:5432/cricketdb"
DB_URL = DATABASE_URL

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# --- Tables ---
class Match(Base):
    __tablename__ = "matches"
    match_id = Column(String, primary_key=True)
    series_id = Column(Integer)
    series_name = Column(String)
    match_desc = Column(String)
    match_format = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    state = Column(String)
    status = Column(String)
    team1 = Column(String)
    team2 = Column(String)
    venue = Column(String)
    city = Column(String)

class MatchScore(Base):
    __tablename__ = "match_scores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String, ForeignKey("matches.match_id"))
    team_name = Column(String)
    innings = Column(Integer)
    runs = Column(Integer)
    wickets = Column(Integer)
    overs = Column(Float)

# --- Initialize DB ---
def init_db():
    Base.metadata.create_all(bind=engine)

def get_engine():
    return engine

def get_session():
    return SessionLocal()

