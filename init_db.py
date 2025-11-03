from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from schema import Base, User, Group, Event  # assuming your models are in models.py
import hashlib

# --- Configuration ---
DB_URL = "sqlite:///app.db"


def hash_password(password: str) -> str:
    """Simple SHA256 hash for demonstration (use bcrypt/argon2 in real apps)."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_db(seed: bool = True):
    """Initializes the SQLite database and optionally seeds initial data."""
    engine = create_engine(DB_URL, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if seed:
        # Check if DB is already initialized
        if session.query(User).first():
            print("Database already initialized. Skipping seed data.")
            session.close()
            return

        print("Seeding initial data...")

        # Create sample users
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            access_level="admin",
            created_at=datetime.now()
        )

        user = User(
            username="john_doe",
            email="john@example.com",
            password_hash=hash_password("password123"),
            access_level="user",
            created_at=datetime.now()
        )

        moderator = User(
            username="mod_jane",
            email="jane@example.com",
            password_hash=hash_password("mod123"),
            access_level="moderator",
            created_at=datetime.now()
        )

        # Create a few groups
        group_dev = Group(group_name="Developers", created_at=datetime.now())
        group_mod = Group(group_name="Moderators", created_at=datetime.now())

        # Create sample event
        event = Event(
            event_name="Launch Party",
            description="Official launch event for our platform."
        )

        # Add relationships
        admin.groups.append(group_dev)
        moderator.groups.append(group_mod)
        user.groups.append(group_dev)

        admin.events.append(event)
        user.events.append(event)

        # Add everything to the session
        session.add_all([admin, user, moderator, group_dev, group_mod, event])

        session.commit()
        print("✅ Database initialized with sample data.")
    else:
        print("✅ Database tables created (no seed data).")

    session.close()


if __name__ == "__main__":
    init_db(seed=True)
