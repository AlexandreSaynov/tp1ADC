"""
Menu System and Dynamic Feature Loader
======================================

This module implements a dynamic, permission-aware command-line menu
system. Menus and submenus are built from configuration data (feature
groups, permission maps), and visibility is controlled by user
authentication and permission checks. Entries correspond to handler
functions imported from various modules, and a flexible dispatcher
(`call_handler`) automatically passes only the expected arguments.

Main features:
- Top-level and nested menus generated dynamically.
- Menu entries filtered by user permissions.
- Automatic handler invocation using function signature inspection.
- Login/logout integration.
- Configurable feature groups through JSON (`vars.json`).
"""

from datetime import datetime
from math import perm
from app.handlers.chats import chat_selection_loop, handle_create_chat
from app.handlers.login import handle_login, handle_logout
from app.handlers.register import handle_register_user
from app.handlers.view_users import handle_view_all_users
from app.handlers.create_group import handle_create_group
from app.handlers.view_group import handle_view_all_groups, handle_manage_my_groups, handle_view_group, handle_edit_group, handle_manage_group_members
from app.handlers.roles import handle_create_role
from app.handlers.events import handle_create_event, handle_view_my_events, handle_view_all_events, handle_edit_event
from app.handlers.check_user import handle_view_profile
import os
import json
import inspect


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "vars/dev/vars.json")) as file:
    config_data = json.load(file)
ALL_PERMISSIONS = config_data["ALL_PERMISSIONS"]
ROLES_JSON_FILE = config_data["ROLES_JSON_FILE"]


def build_dynamic_menu_from_features(logged_user, permissions):
    """
    Build the top-level menu based on configuration and the login state.

    This loads all feature groups from ``IMPLEMENTED_FEATURES`` and
    returns a list of menu entries. If no user is logged in, only
    ``Login`` and ``Exit`` options are shown.

    Parameters
    ----------
    logged_user : object or None
        The current authenticated user.
    permissions : object
        Permission manager that exposes ``has_permission(user, perm)``.

    Returns
    -------
    list[tuple]
        List of tuples in the form ``(function_name, label, permission)``.
    """
    with open("./vars/dev/vars.json", "r") as file:
        config_data = json.load(file)

    implemented_features = config_data["IMPLEMENTED_FEATURES"]

    menu = []
    add = menu.append

    if logged_user is None:
        add(("handle_login", "Login", None))
        add(("exit", "Exit", None))
        return menu

    for group in implemented_features.keys():
        add((group, group, None))

    add(("handle_logout", "Logout", None))
    add(("exit", "Exit", None))

    return menu


def build_submenu(group, logged_user, permissions):
    """
    Build a submenu for a given feature group, filtering entries
    according to user permissions.

    Parameters
    ----------
    group : str
        Feature group name as defined in configuration.
    logged_user : object
        The currently authenticated user.
    permissions : object
        Permission manager used to verify access.

    Returns
    -------
    list[tuple]
        Submenu entries, each a tuple ``(function_name, label, permission)``.
    """
    with open("./vars/dev/vars.json", "r") as file:
        config_data = json.load(file)

    implemented_features = config_data["IMPLEMENTED_FEATURES"]
    group_features = implemented_features.get(group, {})

    submenu = []
    add = submenu.append

    for function, frontend_name in group_features.items():

        permission = config_data["PERMISSION_MAP"].get(function)

        if permission is None or permissions.has_permission(logged_user, permission):
            add((function, frontend_name, permission))

    add(("back", "Back", None))

    return submenu


def print_menu(menu, title="MENU"):
    """
    Print a formatted menu to the console.

    Parameters
    ----------
    menu : list[tuple]
        A list of menu option tuples ``(function, label, permission)``.
    title : str, optional
        Text to display above the menu.
    """
    print(f"============== {title} ==============")
    for idx, (function, label, _) in enumerate(menu, start=1):
        print(f"{idx}. {label}")
    print("==================================\n")


def menu_loop(auth, db, permissions):
    """
    Main interactive loop for the menu system.

    Displays the top-level menu, handles user input, navigates through
    submenus, and dispatches handler functions with appropriate
    arguments. Login/logout updates the session state.

    Parameters
    ----------
    auth : object
        Authentication module for login/logout.
    db : object
        Database or persistence interface (passed to handlers as needed).
    permissions : object
        Permission manager controlling user access.
    """
    logged_user = None

    while True:
        os.system("cls")
        menu = build_dynamic_menu_from_features(logged_user, permissions)
        print_menu(menu, title="MAIN MENU")

        choice = input("Choose a category: ").strip()

        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(menu):
                raise ValueError
        except ValueError:
            print("Invalid option.")
            continue

        selected_function, label, _ = menu[choice_idx]

        if selected_function == "handle_login":
            logged_user = handle_login(auth)
            continue
        elif selected_function == "handle_logout":
            logged_user = handle_logout()
            continue
        elif selected_function == "exit":
            print("Exiting...")
            return

        if selected_function in config_data["IMPLEMENTED_FEATURES"]:
            while True:
                submenu = build_submenu(selected_function, logged_user, permissions)
                print_menu(submenu, title=f"{label.upper()} MENU")

                sub_choice = input("Choose an option: ").strip()

                try:
                    sub_choice_idx = int(sub_choice) - 1
                    if sub_choice_idx < 0 or sub_choice_idx >= len(submenu):
                        raise ValueError
                except ValueError:
                    print("Invalid option.")
                    continue

                sub_function, sub_label, _ = submenu[sub_choice_idx]

                if sub_function == "back":
                    break
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
    """
    Call a handler function by passing only the parameters it accepts.

    Uses :mod:`inspect` to match keyword arguments from ``possible_args``
    to the function’s signature.

    Parameters
    ----------
    func : callable
        The handler function to invoke.
    **possible_args
        All arguments that *might* be passed; only those matching the
        handler signature are forwarded.

    Returns
    -------
    Any
        Whatever the handler function returns.
    """
    sig = inspect.signature(func)
    accepted = {
        name: value for name, value in possible_args.items()
        if name in sig.parameters
    }
    return func(**accepted)
