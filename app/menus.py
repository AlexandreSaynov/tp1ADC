from datetime import datetime
from app.handlers.chats import chat_selection_loop
from app.handlers.login import handle_login, handle_logout
from app.handlers.register import handle_register_user
from app.handlers.view_users import handle_view_all_users
from app.handlers.create_group import handle_create_group
from app.handlers.view_group import handle_view_all_groups, handle_manage_my_groups
from app.handlers.roles import handle_create_role
from app.handlers.events import handle_create_event, handle_view_my_events
from app.handlers.check_user import handle_view_profile
import os
import json

with open("./vars/dev/vars.json") as file:
    config_data = json.load(file)
ALL_PERMISSIONS = config_data["ALL_PERMISSIONS"]
ROLES_JSON_FILE = config_data["ROLES_JSON_FILE"]

# ---------------------------------------------------------
# MENU DEFINITIONS
# ---------------------------------------------------------
def build_dynamic_menu_from_features(logged_user, permissions):
    """
    Builds a dynamic menu based on the IMPLEMENTED_FEATURES in vars.json.
    """
    # Load the configuration file
    with open("./vars/dev/vars.json", "r") as file:
        config_data = json.load(file)

    # Retrieve the implemented features
    implemented_features = config_data["IMPLEMENTED_FEATURES"]

    menu = []
    add = menu.append

    # If the user is not logged in, only show the login and exit options
    if logged_user is None:
        add(("handle_login", "Login", None))
        add(("exit", "Exit", None))
        return menu

    # Iterate through the features and add them to the menu
    for group, functions in implemented_features.items():
        for function, frontend_name in functions.items():
            # Check if the function requires a permission
            permission = None
            if frontend_name == "Login":
                continue  # Skip login for logged in users
            if function in config_data.get("ALL_PERMISSIONS", []):
                permission = function

            # Add the menu option
            add((function, frontend_name, permission))

    # Add the logout and exit options
    add(("handle_logout", "Logout", None))
    add(("exit", "Exit", None))

    # Filter the menu based on user permissions
    final_menu = []
    for function, label, perm in menu:
        if perm is None or permissions.has_permission(logged_user, perm):
            final_menu.append((function, label, perm))

    return final_menu


def print_dynamic_menu_from_features(logged_user, permissions):
    """
    Prints the dynamic menu built from IMPLEMENTED_FEATURES.
    """
    menu = build_dynamic_menu_from_features(logged_user, permissions)

    if logged_user:
        print(f"\nLogged in as: {logged_user.username} ({logged_user.access_level})")

    print("============== MENU ==============")
    for idx, (function, label, _) in enumerate(menu, start=1):
        print(f"{idx}. {label}")
    print("==================================\n")


def menu_loop(auth, db, permissions):
    """
    Main menu loop that dynamically handles menu options.
    """
    logged_user = None

    while True:
        menu = build_dynamic_menu_from_features(logged_user, permissions)
        print_dynamic_menu_from_features(logged_user, permissions)

        choice = input("Choose an option: ").strip()

        # Validate the choice
        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(menu):
                raise ValueError
        except ValueError:
            print("Invalid option.")
            continue

        # Retrieve the selected function
        selected_function, _, _ = menu[choice_idx]

        # Handle the selected function
        if selected_function == "handle_login":
            logged_user = handle_login(auth)
            continue
        elif selected_function == "handle_logout":
            logged_user = handle_logout()
            continue
        elif selected_function == "exit":
            print("Exiting...")
            return

        # Call the appropriate handler dynamically
        if selected_function in globals():
            globals()[selected_function](db, logged_user, permissions)
        else:
            print(f"Function '{selected_function}' is not implemented.")