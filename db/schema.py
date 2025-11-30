"""
Database Models (SQLAlchemy ORM)
================================

Defines all SQLAlchemy ORM models used by the application, including
users, groups, events, and the association tables for many-to-many
relationships. The module loads the database URL from the project
configuration and initializes a SQLite engine, creating all tables
automatically at import time.

Main features:
- User accounts with roles, passwords, timestamps.
- Groups owned by users, with user membership via association table.
- Events owned by users, with attendee tracking via association table.
- Automatic table creation through SQLAlchemy declarative base.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "vars/dev/vars.json")) as file:
    config_data = json.load(file)
DB_URL = config_data["DB_URL"]

Base = declarative_base()


class User(Base):
    """
    Represent a user account.

    Stores username, email, hashed password, role (access_level),
    and creation timestamp. Users participate in many-to-many
    relationships with groups and events.

    Relationships
    -------------
    groups : list[Group]
        Groups the user is a member of.
    events : list[Event]
        Events the user is attending.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    access_level = Column(String, nullable=False)

    groups = relationship(
        'Group',
        secondary='users_in_groups',
        back_populates='users'
    )
    events = relationship(
        'Event',
        secondary='users_attending_events',
        back_populates='users'
    )


class Group(Base):
    """
    Group entity representing collections owned by users.

    Attributes
    ----------
    group_name : str
        Name of the group.
    created_at : datetime
        Auto-populated creation timestamp.
    owner_id : int or None
        The user who created/owns the group.

    Relationships
    -------------
    users : list[User]
        Users belonging to the group.
    """

    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    owner_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    users = relationship(
        'User',
        secondary='users_in_groups',
        back_populates='groups'
    )


class UsersInGroups(Base):
    """
    Association table linking users and groups.

    This is a pure junction table implementing a many-to-many
    relationship between :class:`User` and :class:`Group`.
    """

    __tablename__ = 'users_in_groups'

    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    group_id = Column(
        Integer,
        ForeignKey('groups.id', ondelete='CASCADE'),
        primary_key=True
    )


class Event(Base):
    """
    Event model representing scheduled activities created by a user.

    Attributes
    ----------
    event_name : str
        Title of the event.
    description : str
        Text description of the event.
    event_time : datetime
        When the event will occur.
    owner_id : int or None
        User who created the event.

    Relationships
    -------------
    users : list[User]
        Users attending the event.
    """

    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String)
    description = Column(String)
    event_time = Column(DateTime, default=datetime.now())
    owner_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    users = relationship(
        'User',
        secondary='users_attending_events',
        back_populates='events'
    )


class UsersAttendingEvents(Base):
    """
    Association table linking users and events.

    Implements a many-to-many relationship between :class:`User`
    and :class:`Event`.
    """

    __tablename__ = 'users_attending_events'

    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    event_id = Column(
        Integer,
        ForeignKey('events.id', ondelete='CASCADE'),
        primary_key=True
    )


# --- Create SQLite database ---
engine = create_engine(DB_URL, echo=True)
Base.metadata.create_all(engine)
