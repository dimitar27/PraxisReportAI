import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load .env file explicitly from the parent directory of this file (project root)
env_path = Path(__file__).resolve().parent.parent / ".env"
loaded = load_dotenv(dotenv_path=env_path)

# --- Database connection setup ---

# Retrieve the database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure the URL is set; otherwise raise an error
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment or .env file")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True   # Enables SQLAlchemy 2.0-style usage
)

# Create a session factory for DB sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    """
    Yield a database session and ensure it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
