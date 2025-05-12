import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file explicitly from the parent directory of this file (project root)
env_path = Path(__file__).resolve().parent.parent / ".env"
print(f">>> Loading .env from: {env_path}")
loaded = load_dotenv(dotenv_path=env_path)
print(">>> .env loaded:", loaded)
print(">>> DATABASE_URL:", os.getenv("DATABASE_URL"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment or .env file")

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
