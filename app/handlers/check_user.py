def handle_view_profile(logged_user):
    print("\n=== Your Profile ===")
    print(f"ID: {logged_user.id}")
    print(f"Username: {logged_user.username}")
    print(f"Email: {logged_user.email}")
    print(f"Role: {logged_user.access_level}")