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

    handle_view_group(db, group_id, logged_user,permissions)


def handle_view_group(db, group_id, logged_user=None,permissions=None):
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

    if choice == "1" and (is_owner or permissions.has_permission(logged_user, "group.edit_all")):
        handle_edit_group(db, group_id)
    elif choice == "2" and (is_owner or permissions.has_permission(logged_user, "group.edit_all")):
        handle_manage_group_members(db, group_id)
    elif choice == "3" and (is_owner or permissions.has_permission(logged_user, "group.edit_all")):
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

        