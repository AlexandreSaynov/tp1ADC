"""
auth_service.py
-----------------   

This module provides authentication utilities, including password hashing and
a service class that communicates with the database layer to handle user
registration, login, and session closure.

The module exposes:
- ``hash_password``: A helper function to securely hash user passwords.
- ``AuthService``: A class responsible for managing authentication operations.

Dependencies
- ``hashlib``: Used for SHA-256 hashing.
- ``DBController``: External dependency responsible for database operations.
"""
import hashlib
from db.db_controller import DBController


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class AuthService:
    def __init__(self,db_controller):
        self.db = db_controller

    def register_user(self, username: str, email: str, password: str, access_level="user"):
        if len(self.db.get_all_users()) == 0:
            access_level = "root"
            print("⚠ Creating first user as ROOT")

        ok, result = self.db.add_user(
            username=username,
            email=email,
            password_hash=hash_password(password),
            access_level=access_level
        )

        if not ok:
            print(result)
            return False

        print(f"User '{username}' registered successfully.")
        return True

    def login(self, username: str, password: str):
        user = self.db.get_user_by_username(username)

        if not user:
            print("User not found.")
            return None

        if user.password_hash != hash_password(password):
            print("Incorrect password.")
            return None

        print(f"Welcome {user.username}! ({user.access_level})")
        return user

    def close(self):
        self.db.close()
