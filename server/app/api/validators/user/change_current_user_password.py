from typing import Dict

from app.api.validators.shared import ValidationException, is_password
from app.models import User


def validate_passwords(request_body: Dict, current_user: User) -> str:
    if ("password1" not in request_body.keys()) or ("password2" not in request_body.keys()) or ("old_password" not in request_body.keys()):
        raise ValidationException("Missing data")

    if not is_password(request_body["password1"]):
        raise ValidationException("Password must be at least 8 characters and contain a uppercase letter, a lowercase letter and a number")

    if request_body["password1"] != request_body["password2"]:
        raise ValidationException("Passwords don't match")

    if not current_user.check_password(request_body["old_password"]):
        raise ValidationException("Old password is incorrect")

    return request_body["password1"]
