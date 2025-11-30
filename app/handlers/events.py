from datetime import datetime
from app.handlers._helper import helper_select_users

def handle_create_event(db, logged_user, permissions):
    """
    Create a new event through console input.

    This function guides the user through the process of creating a new event.  
    It validates permissions, collects event details, parses the date/time,  
    selects attendees, and finally delegates event creation to the database layer.

    Parameters
    ----------
    db : DBController
        The database controller responsible for event and user operations.

    logged_user : User
        The user currently logged in. Used for permission validation.

    permissions : Permissions
        Permission manager used to verify whether the user is allowed
        to create events.

    Notes
    -----
    - If the user lacks the ``event.create`` permission, the function exits immediately.
    - Event date/time must follow the format ``YYYY-MM-DD HH:MM``.
    - Attendees are selected via :func:`helper_select_users`.
    - If the date format is invalid, no event is created.
    - Attendee selection may return an empty list, which is allowed.
    - Actual creation occurs through :meth:`DBController.create_event`.
    """
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

    attendee_ids = helper_select_users(db, allow_multiple=True, exclude_ids=set())

    if attendee_ids is None:
        attendee_ids = []

    ok, event_or_msg = db.create_event(name, description, event_date)
    if not ok:
        print("❌ Error creating event:", event_or_msg)
        return

    event = event_or_msg

    for uid in attendee_ids:
        db.add_user_to_event(uid, event.id)

    print(f"✔ Event '{event.event_name}' created with {len(attendee_ids)} attendees.")


def handle_edit_event(db, event_id):
    """
    Display an interactive menu for editing an existing event.

    This function loads the event by ID and presents several editing options:
    updating the event name, description, date/time, attendee list, or deleting
    the event entirely.

    Parameters
    ----------
    db : DBController
        Database controller used to access, update, and delete events.

    event_id : int
        The unique ID of the event to edit.

    Notes
    -----
    - If the event does not exist, the function terminates immediately.
    - Date parsing requires the ``YYYY-MM-DD HH:MM`` format.
    - Editing attendees uses :func:`helper_select_users`.
    - Attendee updates are applied using :meth:`DBController.set_event_attendees`.
    - Event deletion requires confirmation from the user.
    - Updates are committed using :meth:`DBController.update_event`.
    """
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
        print("\n=== Edit Attendees ===")

        new_ids = helper_select_users(db, allow_multiple=True, exclude_ids=set())

        if not new_ids:
            print("No attendees selected.")
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
    """
    Display all events associated with the logged-in user.

    This function shows a list of events the user is attending or owning,
    along with attendee details. The user may optionally select an event to edit.

    Parameters
    ----------
    db : DBController
        Database controller used to retrieve events and attendees.

    logged_user : User
        The user whose events will be displayed.

    Notes
    -----
    - If the user has no events, a message is shown and the function exits.
    - Each event lists its name, date, description, and attendee list.
    - The user may enter an event ID to access :func:`handle_edit_event`.
    - Only events belonging to the user can be edited.
    - Invalid or non-numeric IDs are rejected.
    """
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
    """
    Display every event in the system.

    This function lists all registered events, regardless of ownership,
    and allows the user to select one for editing, assuming permissions.

    Parameters
    ----------
    db : DBController
        The database controller responsible for fetching events and attendees.

    logged_user : User
        The user attempting to view or edit system-wide events.

    Notes
    -----
    - If no events exist, the function exits immediately.
    - For each event, the list displays name, date/time, description, 
      and attendees.
    - Selecting an event ID forwards the user to :func:`handle_edit_event`.
    - Invalid IDs or those outside the available list are rejected.
    """
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