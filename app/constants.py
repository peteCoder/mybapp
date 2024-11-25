import random



ACCOUNT_DETAILS = {
    "Account Number": "",
    "Account Type": "",
    "Branch": "",
    "Balance": "",
    "ACH Routing": "",
}


# Generate user 4 digits verification code
def generate_4_digit_code():
    return str(random.randint(1000, 9999))
