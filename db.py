from pathlib import Path  # Import the modern path library

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Configuration ---
# 1. Get the directory where this 'db.py' file is located
DB_DIR = Path(__file__).resolve().parent

# 2. Define the database file name relative to this directory
DB_FILE = DB_DIR / "hyrox.db"

# 3. Construct the absolute URI for SQLAlchemy
# Note: three slashes are required for absolute paths in SQLite URI:
# sqlite:///absolute/path/to/file.db
DB_URI = f"sqlite:///{DB_FILE}"
# ---------------------

Base = declarative_base()


def init_db():
    """Initializes the database using the absolute path relative to this file."""
    # Use the pre-calculated absolute DB_URI
    engine = create_engine(DB_URI)

    # Ensure all models are imported before calling create_all
    # (Assuming all models are imported elsewhere and registered with Base)
    # If not, you might need a local import, e.g., from . import models
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()

# --- OLD CODE REFERENCE (No longer needed) ---
# The function signature no longer needs the db_uri argument.
# def init_db(db_uri: str = "sqlite:///hyrox.db"):
# -----------------------------------------------
