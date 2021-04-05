import re


def is_email(email: str) -> bool:

    return bool(re.match(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email))


def is_password(password: str) -> bool:
    """Checks password requirements"""
    return bool(
        len(password) >= 8
        and re.search("[0-9]", password) is not None
        and re.search("[a-z]", password) is not None
        and re.search("[A-Z]", password) is not None
    )


def is_url(url: str) -> bool:
    return bool(re.match(r"^https?://.+$", url))
