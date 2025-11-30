from app.handlers.edit_users import handle_edit_user
def handle_view_all_users(db, auth, permissions, logged_user):
    """
    Display all users and optionally allow editing a selected user.

    This function retrieves all users from the database and prints them in a
    formatted list showing their ID, username, email, and access level. 
    If the logged-in user has the 'user.edit_all' permission, they are prompted 
    to select a user by ID to edit. The input is validated, and control is 
    forwarded to :func:`app.handlers.edit_users.handle_edit_user`.

    Parameters
    ----------
    db : Database
        The database interface used to retrieve all users.
    auth : Auth
        The authentication handler required for editing users.
    permissions : Permissions
        The permission manager used to check if the logged-in user can edit others.
    logged_user : User
        The currently authenticated user performing the action.

    Notes
    -----
    - If the user does not have permission, only the list is displayed.
    - If input is empty or invalid, the function returns without editing.
    - Editing is delegated to :func:`app.handlers.edit_users.handle_edit_user`.
    """
    print("\n=== Users ===")
    users = db.get_all_users()
    for u in users:
        print(f"[{u.id}] {u.username} | {u.email} | {u.access_level}")

    if permissions.has_permission(logged_user, "user.edit_all"):
        choice = input("\nEnter the ID of the user you want to edit, or press ENTER to go back: ").strip()
        if not choice:
            return

        try:
            user_id = int(choice)
        except ValueError:
            print("Invalid ID.")
            return

        handle_edit_user(db, auth, user_id)
