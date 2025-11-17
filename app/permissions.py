import json
import os


class PermissionManager:

    def __init__(self, json_path="roles.json"):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Permission file not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.roles = {role["name"]: set(role["permissions"]) for role in data["roles"]}

    def has_permission(self, user, permission: str) -> bool:
        """
        Returns True if the user has the given permission.
        """
        if user is None:
            return False
                
        role = user.access_level  
        if role not in self.roles:
            return False

        return permission in self.roles[role]
