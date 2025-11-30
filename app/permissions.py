"""
Permission Management
=====================

Provides a lightweight permission-management system based on role
definitions stored in a JSON file. Permissions are associated with
roles, and users are assumed to have a ``access_level`` attribute
corresponding to one of these roles.

Main features:
- Load role-to-permission mappings from a JSON configuration file.
- Quickly check whether a user has a specific permission.
- Simple integration with authentication and menu subsystems.
"""

import json
import os


class PermissionManager:
    """
    Manage user role permissions loaded from a JSON file.

    The JSON structure is expected to contain a top-level `"roles"`
    key, with each role defining a `"name"` and a list of `"permissions"`.
    Example::

        {
            "roles": [
                { "name": "user", "permissions": ["view_profile"] },
                { "name": "admin", "permissions": ["edit_users", "delete_users"] }
            ]
        }
    """

    def __init__(self, json_path="roles.json"):
        """
        Initialize the permission manager and load role definitions.

        Parameters
        ----------
        json_path : str, optional
            Path to the roles JSON file. Defaults to ``"roles.json"``.

        Raises
        ------
        FileNotFoundError
            If the roles file does not exist.
        ValueError
            If the JSON structure is missing the required ``roles`` field.
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Permission file not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "roles" not in data:
            raise ValueError("Invalid roles file: missing 'roles' key.")

        # Map: role_name -> set(permissions)
        self.roles = {role["name"]: set(role["permissions"]) for role in data["roles"]}

    def has_permission(self, user, permission: str) -> bool:
        """
        Check whether a user has a given permission.

        Parameters
        ----------
        user : object or None
            A user object expected to have an ``access_level`` attribute.
            If ``None``, permission is automatically denied.
        permission : str
            The permission string to check.

        Returns
        -------
        bool
            ``True`` if the user has the given permission, otherwise ``False``.
        """
        if user is None:
            return False

        role = user.access_level

        if role not in self.roles:
            return False

        return permission in self.roles[role]
