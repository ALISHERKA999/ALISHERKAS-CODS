from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^996\d{9}$',
    message='Номер должен начинаться с 996 и содержать 12 цифр.'
)


def validate_phone_number(value):
    if not value:
        raise ValidationError('Номер телефона обязателен.')

    phone_validator(value)
    return value
