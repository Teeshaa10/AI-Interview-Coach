class AuthError(Exception):
    """Base class for every authentication-related domain error. Catching
    this in one place (see exceptions/handlers.py) lets us add new auth
    exceptions later without touching the exception-handling wiring."""


class UserAlreadyExistsError(AuthError):
    """Raised when registration is attempted with an email that's already
    in the users collection."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"A user with email '{email}' already exists")


class InvalidCredentialsError(AuthError):
    """
    Raised for any login failure — wrong password AND unknown email both
    raise this same exception, on purpose. If "unknown email" returned a
    different error than "wrong password," an attacker could use the
    login endpoint to discover which email addresses have accounts on the
    system. One generic error for both cases closes that information leak.
    """

    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotFoundError(AuthError):
    """Raised when a user id that should exist (e.g. from a validated JWT)
    can't be found. In practice this means the user's account was deleted
    after their token was issued."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"No user found with id '{user_id}'")
