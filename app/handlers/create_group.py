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

