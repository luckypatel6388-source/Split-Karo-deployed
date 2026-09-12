import hashlib
import secrets


def generate_session_token() -> str:
    """
    Generate a cryptographically secure session token.
    """

    return secrets.token_urlsafe(48)


def hash_session_token(token: str) -> str:
    """
    Hash a session token before storing it in the database.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()