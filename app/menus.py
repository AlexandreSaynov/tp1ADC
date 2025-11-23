from datetime import datetime
from app.chats import chat_selection_loop
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


def handle_chat_selection_loop(logged_user):
    chat_selection_loop(logged_user)

def handle_create_group(db, logged_user):
    name = input("Group name: ").strip()
    ok, group_or_msg = db.create_group(name, owner_id=logged_user.id)
    if not ok:
        print(group_or_msg)
        return

    group = group_or_msg
    print(f"Group '{group.group_name}' created with you as owner.")
    
    users = db.get_all_users()
    print("\nSelect members to add (comma-separated IDs), or ENTER to skip:")
    for u in users:
        if u.id != logged_user.id:
            print(f"[{u.id}] {u.username}")

    selected = input("Members: ").strip()
    if selected:
        try:
            member_ids = [int(x) for x in selected.split(",")]
            for uid in member_ids:
                db.add_user_to_group(uid, group.id)
            print(f"Added {len(member_ids)} members to the group.")
        except ValueError:
            print("Invalid input. No members added.")


def handle_view_all_groups(db, logged_user, permissions):
    if not permissions.has_permission(logged_user, "group.view_all"):
        print("You do not have permission to view all groups.")
        return

    print("\n=== All Groups (Admin) ===")
    groups = db.get_all_groups()
    if not groups:
        print("No groups available.")
        return

    for g in groups:
        members = db.get_users_from_group(g.id)
        member_list = ", ".join(u.username for u in members) if members else "(No members)"
        owner = db.get_user_by_id(g.owner_id).username if g.owner_id else "(No owner)"
        print(f"[{g.id}] {g.group_name} | Owner: {owner} | Members: {member_list}")

    choice = input("\nEnter the ID of the group to manage, or press ENTER to go back: ").strip()
    if not choice:
        return

    try:
        group_id = int(choice)
    except ValueError:
        print("Invalid ID.")
        return

    handle_view_group(db, group_id)


def handle_view_group(db, group_id, logged_user=None):
    group = db.get_group_by_id(group_id)
    if not group:
        print("Group not found.")
        return

    print(f"\n=== Group: {group.group_name} ===")
    users = db.get_users_from_group(group_id)
    if not users:
        print("(No members)")
    else:
        print("Members:")
        for u in users:
            print(f" - [{u.id}] {u.username} ({u.email})")

    is_owner = logged_user and group.owner_id == logged_user.id

    print("\nOptions:")
    print("[9] Back")
    if is_owner:
        print("[1] Edit Group")
        print("[2] Manage Members")
        print("[3] Delete Group")

    choice = input("Choose option: ").strip()

    if choice == "1" and is_owner:
        handle_edit_group(db, group_id)
    elif choice == "2" and is_owner:
        handle_manage_group_members(db, group_id)
    elif choice == "3" and is_owner:
        confirm = input("Delete this group? (y/n): ").lower()
        if confirm == "y":
            ok, msg = db.delete_group(group_id)
            print(msg)
    elif choice == "9":
        return
    else:
        print("Invalid option or insufficient permissions.")



def handle_manage_my_groups(db, logged_user):
    print("\n=== My Groups ===")
    groups_owner = db.get_groups_by_owner(logged_user.id)
    groups_member = db.get_groups_by_member(logged_user.id)

    groups_dict = {g.id: g for g in groups_owner + groups_member}
    groups = list(groups_dict.values())

    if not groups:
        print("You are not part of any groups.")
        return

    for g in groups:
        members = db.get_users_from_group(g.id)
        member_list = ", ".join(u.username for u in members) if members else "(No members)"
        owner = db.get_user_by_id(g.owner_id).username if g.owner_id else "(No owner)"
        role = "Owner" if g.owner_id == logged_user.id else "Member"
        print(f"[{g.id}] {g.group_name} | Owner: {owner} | Members: {member_list} | Your role: {role}")

    choice = input("\nEnter the ID of the group to manage, or press ENTER to go back: ").strip()
    if not choice:
        return

    try:
        group_id = int(choice)
    except ValueError:
        print("Invalid ID.")
        return

    handle_view_group(db, group_id, logged_user)



def handle_edit_group(db, group_id):
    group = db.get_group_by_id(group_id)
    if not group:
        print("Group not found.")
        return

    print(f"\n=== Edit Group: {group.group_name} ===")
    new_name = input("New group name: ").strip()

    if not new_name:
        print("Group name cannot be empty.")
        return

    group.group_name = new_name
    db.session.commit()
    print("Group name updated.")



def handle_manage_group_members(db, group_id):
    group = db.get_group_by_id(group_id)
    if not group:
        print("Group not found.")
        return

    print(f"\n=== Manage Members for Group: {group.group_name} ===")

    current_members = db.get_users_from_group(group_id)
    current_ids = {u.id for u in current_members}

    print("\nCurrent members:")
    if not current_members:
        print("  (No members)")
    else:
        for u in current_members:
            print(f" - [{u.id}] {u.username}")

    print("\nAll users:")
    users = db.get_all_users()
    for u in users:
        mark = "*" if u.id in current_ids else " "
        print(f"{mark} [{u.id}] {u.username}")

    print("\n[1] Add user to group")
    print("[2] Remove user from group")
    print("[9] Back")

    action = input("Choose option: ").strip()

    if action == "1":
        uid = int(input("User ID to add: "))
        ok, msg = db.add_user_to_group(uid, group_id)
        print(msg)

    elif action == "2":
        uid = int(input("User ID to remove: "))
        ok, msg = db.remove_user_from_group(uid, group_id)
        print(msg)

    elif action == "9":
        return

    else:
        print("Invalid option.")

        

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

def handle_create_event(db, logged_user, permissions):
    if not permissions.has_permission(logged_user, "event.create"):
        print("You do not have permission to create events.")
        return

    print("\n=== Create New Event ===")

    name = input("Event name: ").strip()
    description = input("Description: ").strip()
    date_str = input("Event date (YYYY-MM-DD HH:MM): ").strip()

    try:
        event_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("❌ Invalid date format.")
        return

    users = db.get_all_users()
    print("\nSelect attendees (comma-separated IDs):")
    for u in users:
        print(f"[{u.id}] {u.username} | {u.email} | {u.access_level}")

    selected = input("Attendees: ").strip()
    try:
        attendee_ids = [int(x) for x in selected.split(",")]
    except ValueError:
        print("Invalid attendee list.")
        return

    ok, event_or_msg = db.create_event(name, description, event_date)
    if not ok:
        print("❌ Error creating event:", event_or_msg)
        return

    event = event_or_msg

    for uid in attendee_ids:
        db.add_user_to_event(uid, event.id)

    print(f"✔ Event '{event.event_name}' created with {len(attendee_ids)} attendees.")

def handle_edit_event(db, event_id):
    event = db.get_event_by_id(event_id)
    if not event:
        print("Event not found.")
        return

    print(f"\n=== Edit Event: {event.event_name} ===")
    print("[1] Change event name")
    print("[2] Change description")
    print("[3] Change event date/time")
    print("[4] Edit attendees")
    print("[5] Delete this event")
    print("[9] Cancel")

    choice = input("Choose option: ").strip()
    updates = {}

    if choice == "1":
        updates["event_name"] = input("New event name: ").strip()

    elif choice == "2":
        updates["description"] = input("New description: ").strip()

    elif choice == "3":
        date_str = input("New event date (YYYY-MM-DD HH:MM): ").strip()
        try:
            updates["event_time"] = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid date format.")
            return

    elif choice == "4":
        print("\n=== Current Attendees ===")

        attendees = db.get_attendees_from_event(event_id)
        ids_current = [a.id for a in attendees]

        for uid in ids_current:
            user = db.get_user_by_id(uid)
            print(f"[{user.id}] {user.username}")

        print("\n=== All Users ===")
        users = db.get_all_users()
        for u in users:
            mark = "*" if u.id in ids_current else " "
            print(f"{mark} [{u.id}] {u.username}")

        selected = input(
            "\nEnter new attendee IDs (comma-separated): "
        ).strip()

        try:
            new_ids = [int(x) for x in selected.split(",")]
        except ValueError:
            print("Invalid attendee list.")
            return

        ok, msg = db.set_event_attendees(event_id, new_ids)
        print(msg)
        return

    elif choice == "5":
        confirm = input("Are you sure you want to delete this event? (y/n): ").lower()
        if confirm == "y":
            ok, msg = db.delete_event(event_id)
            print(msg)
        else:
            print("Delete canceled.")
        return

    elif choice == "9":
        return

    else:
        print("Invalid option.")
        return

    if updates:
        ok, result = db.update_event(event_id, updates)
        if ok:
            print("Event updated successfully.")
        else:
            print(f"Update failed: {result}")



def handle_view_my_events(db, logged_user):
    print("\n=== My Events ===")

    events = db.get_events_from_user(logged_user.id)

    if not events:
        print("You have no events.")
        return

    for e in events:
        print(f"\n[{e.id}] {e.event_name} | {e.event_time} | {e.description}")
        print("Attendees:")

        attendees = db.get_attendees_from_event(e.id)
        if not attendees:
            print("  (No attendees)")
        else:
            for u in attendees:
                print(f"  - {u.username} ({u.email})")


    choice = input("\nEnter the ID of the event to edit, or press ENTER to go back: ").strip()
    if not choice:
        return

    try:
        event_id = int(choice)
    except ValueError:
        print("Invalid ID.")
        return

    if event_id not in [e.id for e in events]:
        print("You can only edit your own events.")
        return

    handle_edit_event(db, event_id)




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
