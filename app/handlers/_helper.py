def helper_select_users(db, allow_multiple=True, exclude_ids=None):
    """
    Prompt the user to select one or more users from the database.

    Displays all users except those listed in ``exclude_ids`` and accepts either
    a single ID or multiple comma-separated IDs, depending on the value of
    ``allow_multiple``. Returns a list of selected user IDs, or an empty list if
    the input is invalid.

    Parameters
    ----------
    db : Database
        Database interface used to retrieve all users.
    allow_multiple : bool, optional
        If ``True`` (default), allows selecting multiple users via
        comma-separated input. If ``False``, only a single ID may be selected.
    exclude_ids : set[int], optional
        A set of user IDs to exclude from the selection list. Defaults to an
        empty set.

    Returns
    -------
    list[int]
        A list of selected user IDs. Returns an empty list if input is invalid
        or if no valid IDs are provided.

    Notes
    -----
    - Non-numeric input results in an empty list.
    - Excluded users are not shown in the selection menu.
    """
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
