def handle_login(auth):
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    return auth.login(username, password)