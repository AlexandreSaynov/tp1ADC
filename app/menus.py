# menus.py
import os
from datetime import datetime


# ---------------------------------------------------------
# MENU DEFINITIONS (dynamic pages)
# ---------------------------------------------------------
def build_menu(logged_user, permissions):
    """
    Returns a list of menu entries based on the user's permissions.
    """
    if logged_user is None:
        return [
            ("1", "Register User", None),
            ("2", "Login", None),
            ("9", "Exit", None)
        ]
    
    items = []

    add = items.append

    add(("1", "Register User",  "user.create"))
    add(("2", "Logout",         None))
    add(("3", "Create Group",   "group.manage"))
    add(("4", "Add User to Group", "group.manage"))
    add(("5", "List Users in Group", "group.view"))
    add(("6", "List All Users", "user.view"))
    add(("7", "Create Event",   "event.manage"))
    add(("8", "Add User to Event", "event.manage"))
    add(("9", "Exit", None))

    final_menu = []
    for opt, label, perm in items:
        if perm is None or permissions.has_permission(logged_user, perm):
            final_menu.append((opt, label, perm))

    return final_menu


def print_dynamic_menu(logged_user, permissions):
    menu = build_menu(logged_user, permissions)

    if logged_user:
        print(f"Logged in as: {logged_user.username} ({logged_user.access_level})")

    print("============== MENU ==============")
    for opt, label, _ in menu:
        print(f"{opt}. {label}")
    print("==================================\n")


# ---------------------------------------------------------
# HANDLERS
# ---------------------------------------------------------

def handle_register(auth):
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    auth.register_user(username, email, password)


def handle_login(auth):
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    return auth.login(username, password)


def handle_logout():
    print("Logging out...")
    return None


def handle_create_group(db):
    group_name = input("Group name: ").strip()
    ok, result = db.create_group(group_name)
    print(result if not ok else f"Group '{result.group_name}' created.")


def handle_add_user_to_group(db):
    user_id = int(input("User ID: "))
    group_id = int(input("Group ID: "))
    ok, msg = db.add_user_to_group(user_id, group_id)
    print(msg)


def handle_list_users_in_group(db):
    group_id = int(input("Group ID: "))
    users = db.get_users_from_group(group_id)

    if not users:
        print("No users or group not found.")
        return

    print(f"Users in group {group_id}:")
    for u in users:
        print(f" - {u.id}: {u.username} ({u.access_level})")


def handle_list_all_users(db):
    users = db.get_all_users()
    for u in users:
        print(f"[{u.id}] {u.username} | {u.email} | {u.access_level}")


def handle_create_event(db):
    name = input("Event name: ").strip()
    desc = input("Description: ").strip()
    date_str = input("Event date (dd/mm/yyyy HH:MM:SS): ").strip()

    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
    except ValueError:
        print("Invalid date format.")
        return

    event = db.create_event(name, desc, dt)
    print(f"Event '{event.event_name}' created.")


def handle_add_user_to_event(db):
    user_id = int(input("User ID: "))
    event_id = int(input("Event ID: "))
    ok, msg = db.add_user_to_event(user_id, event_id)
    print(msg)


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
def menu_loop(auth, db, permissions):
    logged_user = None

    while True:

        menu = build_menu(logged_user, permissions)
        print_dynamic_menu(logged_user, permissions)

        choice = input("Choose an option: ").strip()

        valid_options = {opt for opt, _, _ in menu}
        if choice not in valid_options:
            print("Invalid option.")
            continue

        if choice == "1":
            handle_register(auth)
        elif choice == "2":
            if logged_user:
                logged_user = handle_logout()
            else:
                logged_user = handle_login(auth)
        elif choice == "3":
            handle_create_group(db)
        elif choice == "4":
            handle_add_user_to_group(db)
        elif choice == "5":
            handle_list_users_in_group(db)
        elif choice == "6":
            handle_list_all_users(db)
        elif choice == "7":
            handle_create_event(db)
        elif choice == "8":
            handle_add_user_to_event(db)
        elif choice == "9":
            print("Exiting application...")
            return
