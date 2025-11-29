def handle_edit_user(db, auth, user_id,permission):
    user = db.get_user_by_id(user_id)
    if not user:
        print("User not found.")
        return

    print(f"\n=== Edit User: {user.username} ===")
    print("[1] Change username")
    print("[2] Change email")
    print("[3] Change password")
    print("[4] Change role (access level)") if permission.has_permission(user, "user.edit_role") else None
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
    elif choice == "4" and permission.has_permission(user, "user.edit_role"):
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
