"""
Database Initialization and Utilities Module.

This module provides functionality to initialize the database, 
seed it with sample data, and perform basic utility operations 
like password hashing.

Modules
-------
- sqlalchemy: ORM for database interactions.
- datetime: Date and time handling.
- hashlib: Password hashing using SHA-256.
- json, os: Configuration file loading and path handling.

Functions
---------
- hash_password(password: str) -> str
    Hashes a password using SHA-256.
- init_db(seed: bool = True)
    Initializes the database and optionally seeds it with initial data.

Notes
-----
- Configuration data is read from "vars/dev/vars.json".
- The database URL must be defined under the "DB_URL" key.
- This module can be run as a script to initialize the database directly.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .schema import Base, User, Group, Event
import hashlib
import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "vars/dev/vars.json")) as file:
    config_data = json.load(file)
DB_URL = config_data["DB_URL"]


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.

    Parameters
    ----------
    password : str
        The plain-text password to hash.

    Returns
    -------
    str
        The hexadecimal SHA-256 hash of the password.

    Notes
    -----
    - No salting is applied; this is a simple SHA-256 hash.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_db(seed: bool = True):
    """
    Initialize the database and optionally seed it with sample data.

    Parameters
    ----------
    seed : bool, optional
        Whether to populate the database with sample users and events 
        (default is True).

    Notes
    -----
    - Creates all tables defined in the SQLAlchemy Base metadata.
    - Seeds with a root user and a sample event if the database is empty.
    - If the database already contains users, seeding is skipped.
    - Commits changes to the database and closes the session.
    - Can be executed directly via `python <this_module>.py`.
    """
    engine = create_engine(DB_URL, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if seed:
        if session.query(User).first():
            print("Database already initialized. Skipping seed data.")
            session.close()
            return

        print("Seeding initial data...")

        root = User(
            username="root",
            email="root@example.com",
            password_hash=hash_password("root123"),
            access_level="root",
            created_at=datetime.now()
        )


        event = Event(
            event_name="Launch Party",
            description="Official launch event for our platform.",
            event_time=datetime.now()
        )

        root.events.append(event)

        session.add_all([root, event])

        session.commit()
        print("✅ Database initialized with sample data.")
    else:
        print("✅ Database tables created (no seed data).")

    session.close()


if __name__ == "__main__":
    init_db(seed=True)
