import email_validator
import phonenumbers
from tortoise.exceptions import ValidationError

def validate_email(value):
    try:
        email_validator.validate_email(value)
    except email_validator.EmailNotValidError as e:
        raise e

def validate_phone_number(value):
    phone_number = phonenumbers.parse(value)
    if not phonenumbers.is_valid_number(phone_number):
        raise ValidationError("f{value} is not a valid phone_number")