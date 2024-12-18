import random
from django.shortcuts import render, redirect


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





def go_to_inactive_state(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.user_account_is_active:
        return redirect("account_is_inactive_view")