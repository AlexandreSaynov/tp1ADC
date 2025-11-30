from app.handlers._helper import helper_select_users

def handle_create_group(db, logged_user):
    """
    Create a new user group and optionally add members.

    Prompts the user for a group name, creates the group with the
    logged-in user as the owner, and allows selecting additional members
    via :func:`helper_select_users`. Each selected user is then added to
    the newly created group.

    Parameters
    ----------
    db : Database
        Database interface used to create groups and assign members.
    logged_user : User
        The currently authenticated user who will be set as the group owner.

    Notes
    -----
    - If group creation fails, the error message from the database layer
      is displayed and the operation terminates.
    - The owner is automatically excluded from the selectable member list.
    - Invalid or empty member selection results in no users being added.
    """

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
