from typing import List
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from pydantic import BaseModel
import random
import requests
import json



# Define Pydantic
class ValidationResult(BaseModel):
    message: str
    status: bool
    error_messages: List[str]

def is_valid_email(email: str) -> bool:
    try:
        # Use Django's validate_email to check if the email is valid
        validate_email(email)
        return True
    except ValidationError:
        return False

def check_email(email: str) -> ValidationResult:
    if is_valid_email(email):
        return ValidationResult(
            message="Valid email", 
            status=True, 
            error_messages=[]
        )
    else:
        return ValidationResult(
            message="Invalid email", 
            status=False, 
            error_messages=['Please enter a valid email address']
        )

def is_valid_password(password: str) -> ValidationResult:
    try:
        # Use Django's validate_password to check if the password is valid
        validate_password(password)
        return ValidationResult(
            message="Valid password", 
            status=True, 
            error_messages=[]
        )
    except ValidationError as e:
        # If validation fails, we can print or handle the error messages
        error_messages = [message for message in e.messages]
        return ValidationResult(
            message="Invalid password", 
            status=False, 
            error_messages=error_messages
        )


# Generate user 4 digits verification code
def generate_4_digit_code():
    return str(random.randint(1000, 9999))

# Send 4 digits verification code to user's email
def send_registration_code_mail(code, email):
    url = ""
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, data=json.dumps({"userCode": code, "email": email}), headers=headers)
        return response.status_code
    except requests.Timeout:
        # Handle timeout error
        return 408  # HTTP 408 Request Timeout
    except requests.RequestException as e:
        # Handle other request exceptions
        # print(f"Request exception: {e}")
        return 400
    
        

def check_if_code_matches(userCode, code):
    # assert userCode == int(userCode) and int(code) == code, "codes must be valid integers"
    if userCode == code:
        return True
    else:
        return False
    

    