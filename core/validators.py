from django.core.exceptions import ValidationError


def validate_national_number(value):
    if not (value.isdigit() and len(value) == 10):
        return ValidationError(
            "Invalid National Number! Please Enter Valid National Number (10-Digits)"
        )
        