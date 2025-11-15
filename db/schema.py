from sqlalchemy import (create_engine, Column, Integer, String, DateTime, ForeignKey, CheckConstraint)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    access_level = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("access_level IN ('root','admin', 'user', 'moderator')"),
    )

    groups = relationship('Group', secondary='users_in_groups', back_populates='users')
    events = relationship('Event', secondary='users_attending_events', back_populates='users')


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    users = relationship('User', secondary='users_in_groups', back_populates='groups')


class UsersInGroups(Base):
    __tablename__ = 'users_in_groups'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String)
    description = Column(String)
    event_time = Column(DateTime, default=datetime.now)

    users = relationship('User', secondary='users_attending_events', back_populates='events')


class UsersAttendingEvents(Base):
    __tablename__ = 'users_attending_events'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), primary_key=True)


# --- Create SQLite database ---
engine = create_engine("sqlite:///app.db", echo=True)
Base.metadata.create_all(engine)
