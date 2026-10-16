
from datetime import date

from rest_framework.exceptions import ValidationError


def validate_product_birthdate(request):
    token = request.auth
    payload = getattr(token, "payload", {}) if token else {}
    birthdate = payload.get("birthdate")

    if not birthdate:
        raise ValidationError(
            "Укажите дату рождения, чтобы создать продукт."
        )

    try:
        birthdate = date.fromisoformat(birthdate)
    except (ValueError, TypeError):
        raise ValidationError(
            "Укажите корректную дату рождения."
        )

    today = date.today()
    age = today.year - birthdate.year

    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1

    if age < 18:
        raise ValidationError(
            "Вам должно быть 18 лет, чтобы создать продукт."
        )


