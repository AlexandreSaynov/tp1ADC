def handle_login(auth):
    """
    Handle user login through console input.

    This function prompts the user to enter their username and password,
    then delegates authentication to :meth:`AuthService.login`. The result
    (either a `User` object or ``None``) is returned to the caller.

    Parameters
    ----------
    auth : AuthService
        The authentication service responsible for validating credentials.

    Returns
    -------
    User or None
        The authenticated user if login is successful, otherwise ``None``.

    Notes
    -----
    - Leading and trailing whitespace is removed from all input fields.
    - Passwords are collected in plain text from console input.
    """
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    return auth.login(username, password)

def handle_logout():
    """
    Log out the current user.

    This function displays a logout message and returns ``None`` to signal
    that no user is currently authenticated.

    Returns
    -------
    None
        Always returns ``None`` to represent a logged-out session.

    Notes
    -----
    - This function performs no cleanup beyond user feedback.
    - The calling code should handle state reset if required.
    """
    print("Logging out...")
    return None