from datetime import datetime
from math import perm
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
import inspect


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

    # Add the major categories to the menu
    for group in implemented_features.keys():
        add((group, group, None))  # Add the group name as a menu option

    # Add the logout and exit options
    add(("handle_logout", "Logout", None))
    add(("exit", "Exit", None))

    return menu


def build_submenu(group, logged_user, permissions):
    """
    Builds a submenu for a specific group based on the IMPLEMENTED_FEATURES in vars.json.
    """
    # Load the configuration file
    with open("./vars/dev/vars.json", "r") as file:
        config_data = json.load(file)

    # Retrieve the implemented features for the selected group
    implemented_features = config_data["IMPLEMENTED_FEATURES"]
    group_features = implemented_features.get(group, {})

    submenu = []
    add = submenu.append

    # Add the features of the selected group to the submenu
    for function, frontend_name in group_features.items():

        permission = config_data["PERMISSION_MAP"].get(function)

        if permission is None or permissions.has_permission(logged_user, permission):
            add((function, frontend_name, permission))


    # Add a "Back" option to return to the main menu
    add(("back", "Back", None))

    return submenu


def print_menu(menu, title="MENU"):
    """
    Prints a menu with the given title.
    """
    print(f"============== {title} ==============")
    for idx, (function, label, _) in enumerate(menu, start=1):
        print(f"{idx}. {label}")
    print("==================================\n")


def menu_loop(auth, db, permissions):
    """
    Main menu loop that dynamically handles menu options.
    """
    logged_user = None

    while True:
        # Build and display the main menu
        menu = build_dynamic_menu_from_features(logged_user, permissions)
        print_menu(menu, title="MAIN MENU")

        choice = input("Choose a category: ").strip()

        # Validate the choice
        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(menu):
                raise ValueError
        except ValueError:
            print("Invalid option.")
            continue

        # Retrieve the selected function or group
        selected_function, label, _ = menu[choice_idx]

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

        # If a group is selected, open its submenu
        if selected_function in config_data["IMPLEMENTED_FEATURES"]:
            while True:
                submenu = build_submenu(selected_function, logged_user, permissions)
                print_menu(submenu, title=f"{label.upper()} MENU")

                sub_choice = input("Choose an option: ").strip()

                # Validate the submenu choice
                try:
                    sub_choice_idx = int(sub_choice) - 1
                    if sub_choice_idx < 0 or sub_choice_idx >= len(submenu):
                        raise ValueError
                except ValueError:
                    print("Invalid option.")
                    continue

                # Retrieve the selected submenu function
                sub_function, sub_label, _ = submenu[sub_choice_idx]

                # Handle the submenu function
                if sub_function == "back":
                    break  # Return to the main menu
                elif sub_function in globals():
                    call_handler(
                        globals()[sub_function],
                        db=db,
                        logged_user=logged_user,
                        permissions=permissions,
                        auth=auth
                    )
                else:
                    print(f"Function '{sub_function}' is not implemented.")


def call_handler(func, **possible_args):
    sig = inspect.signature(func)
    accepted = {
        name: value for name, value in possible_args.items()
        if name in sig.parameters
    }
    return func(**accepted)
