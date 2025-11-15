# db_controller.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

from schema import User, Group, UsersInGroups, Event, UsersAttendingEvents
from db.init_db import DB_URL  # Reuse DB URL from init_db

engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)


class DBController:
    def __init__(self):
        self.session = Session()

    # -----------------------------
    # USERS
    # -----------------------------

    def add_user(self, username: str, email: str, password_hash: str, access_level="user"):
        """Add a new user (hash already processed by caller)."""

        if self.session.query(User).filter_by(username=username).first():
            return False, "Username already exists."

        if self.session.query(User).filter_by(email=email).first():
            return False, "Email already exists."

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            access_level=access_level,
            created_at=datetime.now()
        )

        self.session.add(user)
        self.session.commit()
        return True, user

    def get_user_by_username(self, username: str):
        return self.session.query(User).filter_by(username=username).first()

    def get_user_by_email(self, email: str):
        return self.session.query(User).filter_by(email=email).first()

    def get_user_by_id(self, user_id: int):
        return self.session.query(User).filter_by(id=user_id).first()

    def get_all_users(self):
        return self.session.query(User).all()

    # -----------------------------
    # GROUPS
    # -----------------------------

    def create_group(self, group_name: str):
        if self.session.query(Group).filter_by(group_name=group_name).first():
            return False, "Group name already exists."

        group = Group(group_name=group_name, created_at=datetime.now())
        self.session.add(group)
        self.session.commit()
        return True, group

    def add_user_to_group(self, user_id: int, group_id: int):
        user = self.get_user_by_id(user_id)
        group = self.session.query(Group).filter_by(id=group_id).first()

        if not user:
            return False, "User not found."

        if not group:
            return False, "Group not found."

        exists = (
            self.session.query(UsersInGroups)
            .filter_by(user_id=user_id, group_id=group_id)
            .first()
        )

        if exists:
            return False, "User already in this group."

        link = UsersInGroups(user_id=user_id, group_id=group_id)
        self.session.add(link)
        self.session.commit()

        return True, "User added to group."

    def get_users_from_group(self, group_id: int):
        group = self.session.query(Group).filter_by(id=group_id).first()
        return group.users if group else None

    def get_groups_from_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        return user.groups if user else None

    # -----------------------------
    # EVENTS
    # -----------------------------

    def create_event(self, event_name: str, description: str, event_time):
        event = Event(
            event_name=event_name,
            description=description,
            event_time=event_time
        )
        self.session.add(event)
        self.session.commit()
        return event

    def add_user_to_event(self, user_id: int, event_id: int):
        exists = (
            self.session.query(UsersAttendingEvents)
            .filter_by(user_id=user_id, event_id=event_id)
            .first()
        )

        if exists:
            return False, "User already attending."

        link = UsersAttendingEvents(user_id=user_id, event_id=event_id)
        self.session.add(link)
        self.session.commit()

        return True, "User added to event."

    def close(self):
        self.session.close()
