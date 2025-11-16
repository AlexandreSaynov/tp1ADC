# menus.py

from datetime import datetime
import os


def print_menu(logged_user):
    if logged_user != None:
        print(f"Logged in as: {logged_user.username}")
        print("============ MENU ============")
        print("1. Register User")
        print("2. Login")
        print("3. Create Group")
        print("4. Add User to Group")
        print("5. List Users in Group")
        print("6. List All Users")
        print("7. Create Event")
        print("8. Add User to Event")
        print("9. Exit")
        print("==============================\n")
    else:
        print("\n============ MENU ============")
        print("1. Register User")
        print("2. Login")
        print("9. Exit")
        print("==============================\n")


def handle_register(auth):
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    auth.register_user(username, email, password)


def handle_login(auth):
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    return auth.login(username, password)


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

    if users is None:
        print("Group not found.")
        return

    if len(users) == 0:
        print("No users in this group.")
        return

    print(f"Users in group {group_id}:")
    for u in users:
        print(f" - {u.id}: {u.username} ({u.access_level})")


def handle_list_all_users(db):
    users = db.get_all_users()
    print("\nRegistered Users:")
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


def menu_loop(auth, db):
    """Handles the main menu loop and user interactions."""
    logged_user = None

    while True:
        os.system("cls")
        print_menu(logged_user)
        choice = input("Choose an option: ").strip()
        if(logged_user!=None): # logged in menu
            if choice == "1":
                handle_register(auth)
            elif choice == "2":
                logged_user = handle_login(auth) # change to logout
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
                return  # exit loop
            else:
                print("Invalid option.")
        else: # logged out menu
            if choice == "1":
                handle_register(auth)
            elif choice == "2":
                logged_user = handle_login(auth)
            elif choice == "9":
                print("Exiting application...")
                return
            else:
                print("Invalid option")
            
