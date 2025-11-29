from datetime import datetime
def handle_create_event(db, logged_user, permissions):
    if not permissions.has_permission(logged_user, "event.create"):
        print("You do not have permission to create events.")
        return

    print("\n=== Create New Event ===")

    name = input("Event name: ").strip()
    description = input("Description: ").strip()
    date_str = input("Event date (YYYY-MM-DD HH:MM): ").strip()

    try:
        event_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("❌ Invalid date format.")
        return

    users = db.get_all_users()
    print("\nSelect attendees (comma-separated IDs):")
    for u in users:
        print(f"[{u.id}] {u.username} | {u.email} | {u.access_level}")

    selected = input("Attendees: ").strip()
    try:
        attendee_ids = [int(x) for x in selected.split(",")]
    except ValueError:
        print("Invalid attendee list.")
        return

    ok, event_or_msg = db.create_event(name, description, event_date)
    if not ok:
        print("❌ Error creating event:", event_or_msg)
        return

    event = event_or_msg

    for uid in attendee_ids:
        db.add_user_to_event(uid, event.id)

    print(f"✔ Event '{event.event_name}' created with {len(attendee_ids)} attendees.")

def handle_edit_event(db, event_id):
    event = db.get_event_by_id(event_id)
    if not event:
        print("Event not found.")
        return

    print(f"\n=== Edit Event: {event.event_name} ===")
    print("[1] Change event name")
    print("[2] Change description")
    print("[3] Change event date/time")
    print("[4] Edit attendees")
    print("[5] Delete this event")
    print("[9] Cancel")

    choice = input("Choose option: ").strip()
    updates = {}

    if choice == "1":
        updates["event_name"] = input("New event name: ").strip()

    elif choice == "2":
        updates["description"] = input("New description: ").strip()

    elif choice == "3":
        date_str = input("New event date (YYYY-MM-DD HH:MM): ").strip()
        try:
            updates["event_time"] = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid date format.")
            return

    elif choice == "4":
        print("\n=== Current Attendees ===")

        attendees = db.get_attendees_from_event(event_id)
        ids_current = [a.id for a in attendees]

        for uid in ids_current:
            user = db.get_user_by_id(uid)
            print(f"[{user.id}] {user.username}")

        print("\n=== All Users ===")
        users = db.get_all_users()
        for u in users:
            mark = "*" if u.id in ids_current else " "
            print(f"{mark} [{u.id}] {u.username}")

        selected = input(
            "\nEnter new attendee IDs (comma-separated): "
        ).strip()

        try:
            new_ids = [int(x) for x in selected.split(",")]
        except ValueError:
            print("Invalid attendee list.")
            return

        ok, msg = db.set_event_attendees(event_id, new_ids)
        print(msg)
        return

    elif choice == "5":
        confirm = input("Are you sure you want to delete this event? (y/n): ").lower()
        if confirm == "y":
            ok, msg = db.delete_event(event_id)
            print(msg)
        else:
            print("Delete canceled.")
        return

    elif choice == "9":
        return

    else:
        print("Invalid option.")
        return

    if updates:
        ok, result = db.update_event(event_id, updates)
        if ok:
            print("Event updated successfully.")
        else:
            print(f"Update failed: {result}")

def handle_view_my_events(db, logged_user):
    print("\n=== All Events ===")

    events = db.get_events_from_user(logged_user.id)

    if not events:
        print("No events exist.")
        return

    for e in events:
        print(f"\n[{e.id}] {e.event_name} | {e.event_time} | {e.description}")
        print("Attendees:")

        attendees = db.get_attendees_from_event(e.id)
        if not attendees:
            print("  (No attendees)")
        else:
            for u in attendees:
                print(f"  - {u.username} ({u.email})")


    choice = input("\nEnter the ID of the event to edit, or press ENTER to go back: ").strip()
    if not choice:
        return

    try:
        event_id = int(choice)
    except ValueError:
        print("Invalid ID.")
        return

    if event_id not in [e.id for e in events]:
        print("You can only edit your own events.")
        return

    handle_edit_event(db, event_id)


def handle_view_all_events(db, logged_user):
    print("\n=== All Events ===")

    events = db.get_all_events()

    if not events:
        print("No events exist.")
        return

    for e in events:
        print(f"\n[{e.id}] {e.event_name} | {e.event_time} | {e.description}")
        print("Attendees:")

        attendees = db.get_attendees_from_event(e.id)
        if not attendees:
            print("  (No attendees)")
        else:
            for u in attendees:
                print(f"  - {u.username} ({u.email})")


    choice = input("\nEnter the ID of the event to edit, or press ENTER to go back: ").strip()
    if not choice:
        return

    try:
        event_id = int(choice)
    except ValueError:
        print("Invalid ID.")
        return

    if event_id not in [e.id for e in events]:
        print("You can only edit your own events.")
        return

    handle_edit_event(db, event_id)