import secrets


def generate_invite_token() -> str:
    """
    Generate a cryptographically secure invite token.
    """

    return secrets.token_urlsafe(32)


def build_invite_url(
    token: str,
) -> str:
    """
    Relative URL used by the PWA.

    The frontend can later prepend:
    https://splitkaro.app
    """

    return f"/join/{token}"