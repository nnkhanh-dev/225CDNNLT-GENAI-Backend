import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
	# load .env for local development if present
	from dotenv import load_dotenv

	env_path = Path(__file__).resolve().parents[1] / ".env"
	if env_path.exists():
		load_dotenv(env_path)
	else:
		load_dotenv()
except Exception:
	# dotenv is optional in production (container env vars are preferred)
	pass

DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql+psycopg2://postgres:password@postgres:5432/optionsdb",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
