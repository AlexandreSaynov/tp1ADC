from app.handlers.edit_users import handle_edit_user
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