from app.handlers._helper import helper_select_users

def handle_create_group(db, logged_user):
    name = input("Group name: ").strip()
    ok, group_or_msg = db.create_group(name, owner_id=logged_user.id)

    if not ok:
        print(group_or_msg)
        return

    group = group_or_msg
    print(f"\nGroup '{group.group_name}' created with you as owner.\n")

    member_ids = helper_select_users(db, allow_multiple=True, exclude_ids={logged_user.id})

    if not member_ids:
        print("No members added.")
        return

    for uid in member_ids:
        db.add_user_to_group(uid, group.id)

    print(f"Added {len(member_ids)} members to the group.")
