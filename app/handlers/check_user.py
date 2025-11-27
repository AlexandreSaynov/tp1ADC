def handle_view_profile(user):
    print("\n=== Your Profile ===")
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Role: {user.access_level}")