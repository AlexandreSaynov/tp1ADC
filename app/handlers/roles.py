import json
def handle_create_role(permissions, logged_user,ALL_PERMISSIONS,ROLES_JSON_FILE):
    if not permissions.has_permission(logged_user, "role.create"):
        print("You do not have permission to create roles.")
        return

    role_name = input("Enter new role name: ").strip()
    if not role_name:
        print("Role name cannot be empty.")
        return

    print("\nSelect permissions for this role (comma-separated numbers):")
    for idx, perm in enumerate(ALL_PERMISSIONS, start=1):
        print(f"[{idx}] {perm}")

    selected = input("Your choice: ").strip()
    if not selected:
        print("No permissions selected. Role not created.")
        return

    try:
        selected_indexes = [int(s) - 1 for s in selected.split(",")]
    except ValueError:
        print("Invalid selection.")
        return

    new_perms = []
    for i in selected_indexes:
        if 0 <= i < len(ALL_PERMISSIONS):
            new_perms.append(ALL_PERMISSIONS[i])

    if not new_perms:
        print("No valid permissions selected. Role not created.")
        return

    try:
        with open(ROLES_JSON_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"roles": []}

    data["roles"].append({
        "name": role_name,
        "permissions": new_perms
    })

    with open(ROLES_JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Role '{role_name}' created with permissions: {new_perms}")