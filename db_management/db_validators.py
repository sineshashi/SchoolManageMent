import email_validator
import phonenumbers
from tortoise.exceptions import ValidationError
from fastapi import HTTPException

def validate_email(value):
    try:
        email_validator.validate_email(value)
    except email_validator.EmailNotValidError as e:
        raise HTTPException(405, "Email is not Valid")

def validate_phone_number(value):
    try:
        phone_number = phonenumbers.parse(value)
    except:
        raise HTTPException(405, "Phone Number is not valid")
    if not phonenumbers.is_valid_number(phone_number):
        raise HTTPException(405, "Phone Number is not valid")