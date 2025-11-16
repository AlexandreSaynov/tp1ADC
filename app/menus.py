from datetime import datetime
import os


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

def handle_view_all_users(db):
    print("\n=== Users ===")
    users = db.get_all_users()
    for u in users:
        print(f"[{u.id}] {u.username} | {u.email} | {u.access_level}")

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
            handle_view_all_users(db)

        elif choice == "3":
            handle_create_group(db)

        elif choice == "4":
            handle_view_all_groups(db)

        elif choice == "5":
            handle_view_profile(logged_user)

        elif choice == "6":
            logged_user = handle_logout()

        elif choice == "9":
            print("Exiting...")
            return
