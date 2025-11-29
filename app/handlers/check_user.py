from app.handlers.edit_users import handle_edit_user
import db


def handle_view_profile(auth,logged_user,permission):
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

    