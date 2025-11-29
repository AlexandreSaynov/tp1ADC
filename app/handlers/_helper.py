def helper_select_users(db, allow_multiple=True, exclude_ids=None):
    exclude_ids = exclude_ids or set()

    print("\n=== Select Users ===")

    users = db.get_all_users()
    for u in users:
        if u.id not in exclude_ids:
            print(f"[{u.id}] {u.username}")

    if allow_multiple:
        ids_str = input("Enter user IDs separated by commas: ").strip()
        try:
            selected = [int(x) for x in ids_str.split(",") if x.strip()]
        except:
            print("Invalid input.")
            return []

        return selected

    else:
        uid = input("Enter user ID: ").strip()
        if uid.isdigit():
            return [int(uid)]
        else:
            print("Invalid ID.")
            return []
