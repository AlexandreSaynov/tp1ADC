from datetime import datetime
from app.handlers.chats import chat_selection_loop
from app.handlers import handle_login, handle_logout, handle_register_user, handle_view_all_users, handle_create_group, handle_view_all_groups, handle_manage_my_groups, handle_create_role, handle_create_event, handle_view_my_events, handle_view_profile
import os
import json

with open("./vars/dev/vars.json") as file:
    config_data = json.load(file)
ALL_PERMISSIONS = config_data["ALL_PERMISSIONS"]
ROLES_JSON_FILE = config_data["ROLES_JSON_FILE"]

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
    add(("3", "Create Group", "group.create"))
    add(("4", "View All Groups", "group.view_all")) 
    add(("5", "Manage My Groups", "group.manage_own"))
    add(("6", "View Profile", None))
    add(("7", "Create New Role", "role.create"))
    add(("8", "Create New Event", "event.create"))
    add(("9", "View my Events", None))
    add(("10", "Logout", None))
    add(("0", "Exit", None))

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

        # ---------- LOGGED IN ----------
        if choice == "1":
            handle_register_user(auth)

        elif choice == "2":
            handle_view_all_users(db, auth)

        elif choice == "3":
            handle_create_group(db,logged_user)

        elif choice == "4":
            handle_view_all_groups(db,logged_user,permissions)

        elif choice == "5":
            handle_manage_my_groups(db,logged_user)

        elif choice == "6":
            handle_view_profile(logged_user)

        elif choice == "7":
            handle_create_role(permissions, logged_user)
        elif choice == "8":
            chat_selection_loop(logged_user)


        elif choice == "8":
            handle_create_event(db, logged_user, permissions)

        elif choice == "9":
            handle_view_my_events(db, logged_user)

        elif choice == "10":
            logged_user = handle_logout()

        elif choice == "0":
            print("Exiting...")
            return
