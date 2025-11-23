from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .schema import Base, User, Group, Event
import hashlib
import json

with open("./vars/dev/vars.json") as file:
    config_data = json.load(file)
DB_URL = config_data["DB_URL"]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_db(seed: bool = True):
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
