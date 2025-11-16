import json

class PermissionManager:
    def __init__(self, json_path):
        with open(json_path) as f:
            data = json.load(f)

        self.role_permissions = {
            role["name"]: set(role["permissions"])
            for role in data["roles"]
        }

    def has_permission(self, user, permission: str):
        if not user:
            return False
        
        role = user.access_level.lower()

        if role not in self.role_permissions:
            return False

        return permission in self.role_permissions[role]

    def get_permissions_of(self, user):
        role = user.access_level.lower()
        return self.role_permissions.get(role, set())
