from app.handlers.edit_users import handle_edit_user
import db


def handle_view_profile(auth, logged_user, permission):
    """
    Display and optionally edit the logged-in user's profile.

    Shows basic account information (ID, username, email, and role)
    and allows the user to enter the profile editor through
    :func:`handle_edit_user`.

    Parameters
    ----------
    auth : Auth
        Authentication/authorization handler, used when editing the user.
    logged_user : User
        The currently authenticated user whose profile is shown.
    permission : Permission
        Permission handler used to validate edit actions.

    Notes
    -----
    - Editing redirects to :func:`handle_edit_user`.
    - Invalid numeric input results in a validation message and exit.
    """

    print("\n=== Your Profile ===")
    print(f"ID: {logged_user.id}")
    print(f"Username: {logged_user.username}")
    print(f"Email: {logged_user.email}")
    print(f"Role: {logged_user.access_level}")
    choice = input("\nIf you would like to edit your user, enter 1. Else, press ENTER to go back: ").strip()
    if not choice:
        return
    try:
        choice = int(choice)
        if choice == 1:
            handle_edit_user(db, auth, logged_user.id,permission)
        else:
            return
    except ValueError:
        print("Invalid input.")
        return

    