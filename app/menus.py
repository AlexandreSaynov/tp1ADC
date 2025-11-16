from datetime import datetime
import os
import json

ALL_PERMISSIONS = [
    "user.create",
    "user.view",
    "group.manage",
    "group.view",
    "role.create"
]

ROLES_JSON_FILE = "vars/dev/permissions.json"

# ---------------------------------------------------------
# MENU DEFINITIONS
# ---------------------------------------------------------
def build_menu(logged_user, permissions):

    if logged_user is None:
        return [
            ("1", "Login", None),
            ("9", "Exit", None)
        ]

    menu = []
    add = menu.append

    add(("1", "Register User", "user.create"))
    add(("2", "View All Users", "user.view"))
    add(("3", "Create Group", "group.manage"))
    add(("4", "View All Groups", "group.view"))
    add(("5", "View Profile", None))
    add(("6", "Logout", None))
    add(("7", "Create New Role", "role.create"))
    add(("9", "Exit", None))

    final = []
    for opt, label, perm in menu:
        if perm is None or permissions.has_permission(logged_user, perm):
            final.append((opt, label, perm))

    return final



def print_dynamic_menu(logged_user, permissions):
    menu = build_menu(logged_user, permissions)

    if logged_user:
        print(f"\nLogged in as: {logged_user.username} ({logged_user.access_level})")

    print("============== MENU ==============")
    for opt, label, _ in menu:
        print(f"{opt}. {label}")
    print("==================================\n")


# ---------------------------------------------------------
# HANDLERS
# ---------------------------------------------------------

def handle_login(auth):
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    return auth.login(username, password)

def handle_logout():
    print("Logging out...")
    return None

def handle_register_user(auth):
    print("=== Register User ===")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    auth.register_user(username, email, password)

def handle_view_all_users(db, auth):
    print("\n=== Users ===")
    users = db.get_all_users()
    for u in users:
        print(f"[{u.id}] {u.username} | {u.email} | {u.access_level}")

    choice = input("\nEnter the ID of the user you want to edit, or press ENTER to go back: ").strip()
    if not choice:
        return

    try:
        user_id = int(choice)
    except ValueError:
        print("Invalid ID.")
        return

    handle_edit_user(db, auth, user_id)



def handle_create_group(db):
    name = input("Group name: ").strip()
    ok, result = db.create_group(name)
    print(result if not ok else f"Group '{result.group_name}' created.")

def handle_view_all_groups(db):
    print("\n=== Groups ===")
    groups = db.get_all_groups()
    for g in groups:
        print(f"[{g.id}] {g.group_name}")

def handle_view_profile(user):
    print("\n=== Your Profile ===")
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Role: {user.access_level}")

def handle_edit_user(db, auth, user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        print("User not found.")
        return

    print(f"\n=== Edit User: {user.username} ===")
    print("[1] Change username")
    print("[2] Change email")
    print("[3] Change password")
    print("[4] Change role (access level)")
    print("[9] Cancel")

    choice = input("Choose option: ").strip()
    updates = {}

    if choice == "1":
        updates["username"] = input("New username: ").strip()
    elif choice == "2":
        updates["email"] = input("New email: ").strip()
    elif choice == "3":
        new_pwd = input("New password: ").strip()
        updates["password_hash"] = auth.hash_password(new_pwd)
    elif choice == "4":
        updates["access_level"] = input("New role/access level: ").strip()
    elif choice == "9":
        return
    else:
        print("Invalid option.")
        return

    if updates:
        ok, result = db.update_user(user_id, updates)
        if ok:
            print("User updated successfully.")
        else:
            print(f"Update failed: {result}")

def handle_create_role(permissions, logged_user):
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


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
def menu_loop(auth, db, permissions):
    logged_user = None

    while True:
        menu = build_menu(logged_user, permissions)
        print_dynamic_menu(logged_user, permissions)

        choice = input("Choose an option: ").strip()

        valid = {opt for opt, _, _ in menu}
        if choice not in valid:
            print("Invalid option.")
            continue

        if logged_user is None:
            if choice == "1":
                logged_user = handle_login(auth)
            elif choice == "9":
                print("Exiting...")
                return
            continue

        if choice == "1":
            handle_register_user(auth)

        elif choice == "2":
            handle_view_all_users(db,auth)

        elif choice == "3":
            handle_create_group(db)

        elif choice == "4":
            handle_view_all_groups(db)

        elif choice == "5":
            handle_view_profile(logged_user)

        elif choice == "6":
            logged_user = handle_logout()
        elif choice == "7":
            handle_create_role(permissions, logged_user)


        elif choice == "9":
            print("Exiting...")
            return
