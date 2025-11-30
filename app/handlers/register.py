def handle_register_user(auth):
    """
    Handle user registration through console input.

    This function prompts the user for a username, an email address, 
    and a password. The collected data is then forwarded to the 
    authentication service's :meth:`register_user` method to create a new user.

    Parameters
    ----------
    auth : AuthService
        The authentication service responsible for registering users.
    
    Notes
    -----
    - No validation is performed here; all checks occur in 
      :meth:`AuthService.register_user`.
    - Leading and trailing spaces in user input are removed.
    - Passwords are collected as plain text from console input.
    """
    print("=== Register User ===")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    auth.register_user(username, email, password)