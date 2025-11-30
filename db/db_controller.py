"""
Database controller providing high-level CRUD operations for users, groups,
and events. This module abstracts SQLAlchemy interactions and exposes a
simple API for authentication systems, group management, and event handling.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from .schema import User, Group, UsersInGroups, Event, UsersAttendingEvents
from .init_db import DB_URL

engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)


class DBController:
    """
    High-level interface to the application's database, wrapping SQLAlchemy
    models and sessions to perform user, group, and event operations.
    """

    def __init__(self):
        """
        Initialize a new SQLAlchemy session for database operations.
        """
        self.session = Session()

    # -----------------------------
    # USERS
    # -----------------------------

    def add_user(self, username: str, email: str, password_hash: str, access_level="user"):
        """
        Create and persist a new user.

        :param str username: The desired username.
        :param str email: User's email address.
        :param str password_hash: Pre-hashed password.
        :param str access_level: Permission role (default: ``"user"``).
        :returns: ``(True, User)`` on success, otherwise ``(False, message)``.
        :rtype: tuple
        """
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
        """
        Retrieve a user by username.

        :param str username: Username to query.
        :returns: User object or ``None``.
        """
        print(self.session.query(User).filter_by(username=username).first())
        return self.session.query(User).filter_by(username=username).first()

    def get_user_by_email(self, email: str):
        """
        Retrieve a user by email.

        :param str email: Email address.
        :returns: User object or ``None``.
        """
        return self.session.query(User).filter_by(email=email).first()

    def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by database ID.

        :param int user_id: User ID.
        :returns: User object or ``None``.
        """
        return self.session.query(User).filter_by(id=user_id).first()

    def get_all_users(self):
        """
        Get all user entries.

        :returns: List of all :class:`User` objects.
        :rtype: list
        """
        return self.session.query(User).all()
    
    def update_user(self, user_id: int, updates: dict):
        """
        Update fields of an existing user.

        :param int user_id: User ID.
        :param dict updates: Mapping of field names to new values.
        :returns: ``(True, user)`` on success, otherwise ``(False, message)``.
        :rtype: tuple
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found."
        
        if "username" in updates:
            if self.session.query(User).filter_by(username=updates["username"]).first():
                return False, "Username already exists."
        if "email" in updates:
            if self.session.query(User).filter_by(email=updates["email"]).first():
                return False, "Email already exists."

        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                return False, f"Invalid field: {key}"

        self.session.commit()
        return True, user

    # -----------------------------
    # GROUPS
    # -----------------------------

    def get_group_by_id(self, group_id: int):
        """
        Retrieve a group by ID.

        :param int group_id: Group identifier.
        :returns: Group object or ``None``.
        """
        return self.session.query(Group).filter_by(id=group_id).first()

    def get_all_groups(self):
        """
        Retrieve all groups.

        :returns: List of groups.
        :rtype: list
        """
        return self.session.query(Group).all()

    def create_group(self, group_name: str, owner_id: int = None):
        """
        Create a new group.

        :param str group_name: Name of the group.
        :param int owner_id: Optional ID of the group's owner.
        :returns: ``(True, Group)`` or ``(False, message)``.
        :rtype: tuple
        """
        if self.session.query(Group).filter_by(group_name=group_name).first():
            return False, "Group name already exists."
        
        group = Group(
            group_name=group_name,
            owner_id=owner_id,
            created_at=datetime.now()
        )

        self.session.add(group)
        self.session.commit()
        return True, group

    def add_user_to_group(self, user_id: int, group_id: int):
        """
        Add a user to a group.

        :param int user_id: User identifier.
        :param int group_id: Group identifier.
        :returns: ``(True, message)`` or ``(False, message)``.
        :rtype: tuple
        """
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
        """
        Retrieve users that belong to a specific group.

        :param int group_id: Group identifier.
        :returns: List of users or ``None``.
        """
        group = self.session.query(Group).filter_by(id=group_id).first()
        return group.users if group else None

    def get_groups_from_user(self, user_id: int):
        """
        Retrieve groups that a user belongs to.

        :param int user_id: User identifier.
        :returns: List of groups or ``None``.
        """
        user = self.get_user_by_id(user_id)
        return user.groups if user else None
    
    def update_group_name(self, group_id, new_name):
        """
        Rename a group.

        :param int group_id: Group identifier.
        :param str new_name: New group name.
        :returns: ``(True, group)`` or ``(False, message)``.
        """
        group = self.get_group_by_id(group_id)
        if not group:
            return False, "Group not found."

        group.group_name = new_name
        self.session.commit()
        return True, group
    
    def remove_user_from_group(self, user_id, group_id):
        """
        Remove a user from a group.

        :param int user_id: User identifier.
        :param int group_id: Group identifier.
        :returns: ``(True, message)`` or ``(False, message)``.
        """
        link = (
            self.session.query(UsersInGroups)
            .filter_by(user_id=user_id, group_id=group_id)
            .first()
        )

        if not link:
            return False, "User is not in this group."

        self.session.delete(link)
        self.session.commit()
        return True, "User removed from group."

    def delete_group(self, group_id):
        """
        Delete a group and its membership links.

        :param int group_id: Group identifier.
        :returns: ``(True, message)`` or ``(False, message)``.
        """
        group = self.session.query(Group).filter_by(id=group_id).first()
        if not group:
            return False, "Group not found."

        self.session.query(UsersInGroups).filter_by(group_id=group_id).delete()
        self.session.delete(group)
        self.session.commit()

        return True, "Group deleted successfully."

    def get_groups_by_owner(self, owner_id):
        """
        Retrieve groups that belong to a specific owner.

        :param int owner_id: Owner identifier.
        :returns: List of groups.
        """
        return self.session.query(Group).filter_by(owner_id=owner_id).all()

    def get_groups_by_member(self, user_id):
        """
        Retrieve groups a user is a member of.

        :param int user_id: User identifier.
        :returns: List of groups.
        """
        return (
            self.session.query(Group)
            .join(UsersInGroups)
            .filter(UsersInGroups.user_id == user_id)
            .all()
        )

    # -----------------------------
    # EVENTS
    # -----------------------------

    def create_event(self, event_name: str, description: str, event_time):
        """
        Create a new event.

        :param str event_name: Title of the event.
        :param str description: Event description.
        :param datetime event_time: Scheduled time.
        :returns: ``(True, Event)``.
        """
        event = Event(
            event_name=event_name,
            description=description,
            event_time=event_time
        )
        self.session.add(event)
        self.session.commit()
        return True, event

    def add_user_to_event(self, user_id: int, event_id: int):
        """
        Add a user as an event attendee.

        :param int user_id: User identifier.
        :param int event_id: Event identifier.
        :returns: ``(True, message)`` or ``(False, message)``.
        """
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

    def get_events_from_user(self, user_id: int):
        """
        Retrieve events associated with a user.

        :param int user_id: User identifier.
        :returns: List of events or ``None``.
        """
        user = self.get_user_by_id(user_id)
        return user.events if user else None
    
    def get_all_events(self):
        """
        Retrieve all events.

        :returns: List of events.
        """
        return self.session.query(Event).all()
    
    def update_event(self, event_id: int, updates: dict):
        """
        Update an event's fields.

        :param int event_id: Event identifier.
        :param dict updates: Field/value mappings.
        :returns: ``(True, event)`` or ``(False, message)``.
        """
        event = self.session.query(Event).filter_by(id=event_id).first()
        if not event:
            return False, "Event not found."
        
        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)
            else:
                return False, f"Invalid field: {key}"

        self.session.commit()
        return True, event
    
    def get_event_by_id(self, event_id: int):
        """
        Retrieve an event by ID.

        :param int event_id: Event identifier.
        :returns: Event object or ``None``.
        """
        return self.session.query(Event).filter_by(id=event_id).first()
    
    def get_attendees_from_event(self, event_id: int):
        """
        Get all users attending a specific event.

        :param int event_id: Event identifier.
        :returns: List of attendees or ``None``.
        """
        event = self.get_event_by_id(event_id)
        if not event:
            return None

        attendees = (
            self.session.query(User)
            .join(UsersAttendingEvents, UsersAttendingEvents.user_id == User.id)
            .filter(UsersAttendingEvents.event_id == event_id)
            .all()
        )
        return attendees
    
    def set_event_attendees(self, event_id: int, new_attendee_ids: list[int]):
        """
        Replace all attendees of an event.

        :param int event_id: Event identifier.
        :param list[int] new_attendee_ids: User IDs to assign.
        :returns: ``(True, message)``.
        """
        self.session.query(UsersAttendingEvents).filter_by(event_id=event_id).delete()

        for uid in new_attendee_ids:
            self.session.add(UsersAttendingEvents(user_id=uid, event_id=event_id))

        self.session.commit()
        return True, "Attendees updated successfully."

    def delete_event(self, event_id: int):
        """
        Delete an event.

        :param int event_id: Event identifier.
        :returns: ``(True, message)`` or ``(False, message)``.
        """
        event = self.get_event_by_id(event_id)
        if not event:
            return False, "Event not found."

        self.session.delete(event)
        self.session.commit()
        return True, "Event deleted."

    def close(self):
        """
        Close the active database session.
        """
        self.session.close()
