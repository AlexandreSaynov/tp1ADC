"""
Authentication Service
======================

Provides simple authentication utilities including password hashing,
user registration with automatic root assignment for the first user,
and credential validation during login. Interaction with persistence is
handled through a ``DBController`` instance passed into ``AuthService``.

Main features:
- Secure password hashing (SHA-256)
- User registration with automatic "root" role for first user
- Login validation against stored password hashes
- Clean separation between authentication logic and storage backend
"""

import hashlib
from db.db_controller import DBController


def hash_password(password: str) -> str:
    """
    Compute a SHA-256 hash of the given password.

    Parameters
    ----------
    password : str
        The plaintext password to hash.

    Returns
    -------
    str
        Hex-encoded SHA-256 password hash.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class AuthService:
    """
    Authentication service providing user registration and login.

    This class acts as a layer on top of :class:`DBController`, handling
    password hashing and basic authentication flow (register, login,
    close). It does not manage permissions or session state — only
    identity validation and creation.
    """

    def __init__(self, db_controller):
        """
        Initialize the authentication service.

        Parameters
        ----------
        db_controller : DBController
            Instance responsible for database operations such as
            retrieving and persisting user records.
        """
        self.db = db_controller

    def register_user(self, username: str, email: str, password: str, access_level="user"):
        """
        Register a new user in the database.

        If this is the first user in the system, they are automatically
        assigned the ``root`` access level. Passwords are hashed using
        :func:`hash_password`.

        Parameters
        ----------
        username : str
            Desired username.
        email : str
            User email address.
        password : str
            Plaintext password, to be hashed before storage.
        access_level : str, optional
            Initial access level; defaults to ``"user"``.

        Returns
        -------
        bool
            ``True`` if the user was registered successfully, otherwise
            ``False``.
        """
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
        """
        Authenticate a user by username and password.

        Parameters
        ----------
        username : str
            Username to authenticate.
        password : str
            Plaintext password to verify.

        Returns
        -------
        object or None
            The user object on successful login, or ``None`` on failure.
        """
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
        """
        Close the underlying database connection.

        This method simply delegates to :meth:`DBController.close`.
        """
        self.db.close()
