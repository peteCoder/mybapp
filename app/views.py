import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from .models import (
    Account, 
    Transaction, 
    Loan, 
    Card, 
    Transfer, 
    Notification, 
    Support, 
    Payment
)
from api.email import (
    send_beautiful_html_email_create_user, 
    send_beautiful_html_email_create_account, 
    send_password_reset_email,
    send_otp_code_verification,
    send_transaction_mail,
    send_admin_mail,
    send_ordinary_user_mail,

)
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model
import json
from django.db.models import Sum, Count
from django.utils import timezone
from collections import defaultdict
import calendar
from django.db.models.functions import ExtractMonth

from django.http import Http404

from .forms import TransferForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import SignupForm
from functools import reduce

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .constants import generate_4_digit_code, go_to_inactive_state


User = get_user_model()



def get_monthly_transactions(account_type, year, user):
    transactions = Transaction.objects.filter(
        from_account__account_type=account_type,
        from_account__customer=user,
        timestamp__year=year
    ).annotate(month=ExtractMonth('timestamp')).values('month').annotate(total=Sum('amount')).order_by('month')

    monthly_data = defaultdict(lambda: 0)  # Default to 0 if no data for a month
    for transaction in transactions:
        monthly_data[transaction['month']] = transaction['total']

    # Return data as list of amounts for each month
    return [int(monthly_data[month]) for month in range(1, 13)]





# Create your views here.
def home(request):
    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response

    # user = User.objects.filter(email=request.user.email).first()
    # print(user.email)

    user = request.user

    if not user.is_authenticated:
        return redirect("login")
    
    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    

    # profile = Profile.objects.get(user=request.user)

    accounts = Account.objects.filter(customer=user).all()
    loans = Loan.objects.filter(customer=user)

    debit_cards = Card.objects.filter(user=request.user).filter(card_category="Debit").order_by("-pk")
    debit_cards_count = debit_cards.count()
    has_debit_cards = debit_cards.exists()
    credit_cards = Card.objects.filter(user=request.user).filter(card_category="Credit").order_by("-pk")
    credit_cards_count = credit_cards.count()
    has_credit_cards = credit_cards.exists()
    



    account_model_meta = {
        'model_name': Account._meta.model_name.capitalize(),  # Account model name
    }
    loan_model_meta = {
        'model_name': Loan._meta.model_name.capitalize(),  # Loan model name
    }



    has_loan = loans.count() > 0
    has_account = accounts.count() > 0

    current_year = timezone.now().year

    checking_data = get_monthly_transactions('CHECKING', current_year, user)
    savings_data = get_monthly_transactions('SAVINGS', current_year, user)
    months_data = list(calendar.month_abbr[1:])

    all_transactions = Transaction.objects.filter(user=request.user).order_by("-id")[:3]

    loan_amounts = [float(loan.amount) for loan in Loan.objects.all()]

    loan_total = sum(loan_amounts)
    
    print("loan_amounts: ", loan_amounts)
    print("loan_total: ", loan_total)



    

    return render(request, "dashboard/major/index.html", {

        "notifications": notifications,
        "notification_count": notifications.count(),

        'accounts': accounts,
        "loan": loans.first(),
        "loans": loans,
        "loan_total": loan_total,
        "has_loan": has_loan,

        "has_account": has_account,

        # Labels
        "account_model_meta": account_model_meta,
        "loan_model_meta": loan_model_meta,

        'checking_data': json.dumps(checking_data),
        'savings_data': json.dumps(savings_data),
        'months_data': json.dumps(months_data),
        'transactions': all_transactions,

        # Cards
        "debit_cards": debit_cards,
        "debit_cards_count": debit_cards_count,
        
        "credit_cards": credit_cards,
        "credit_cards_count": credit_cards_count,

        "has_credit_cards": has_credit_cards,
        "has_debit_cards": has_debit_cards,
    })


@login_required
def LogoutView(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('login')




def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")
    
    return render(request, "main/pages-sign-in.html", {})


def welcome_to_check_your_mail(request):
    return render(request, "main/check_email_upon_signin.html", {})



def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")
    
    EMPLOYMENT_STATUS = [
        "Employed",
        "Self-employed",
        "Unemployed",
        "Retired"
    ]

    

    ACCOUNT_TYPES = (
        'CHECKING',
        'SAVINGS',
        'PLATINUM', 
        'MONEY MARKET',
    )

    PREFERRED_ID_TYPE = [
        "Driver Licence",
        "National ID",
        "Passport"
    ]
    CITIZENSHIP_STATUSES = [
        'US Citizen' , 
        'Non-US Citizen'
    ]

    EMPLOYMENT_TYPE = [
        "Full-time",
        "Part-time",
        "Contract", 
        "Temporary",
    ]

    MARITAL_CHOICES = [
        "Married",
        "Single",
        "Divorced",
    ]

    return render(request, "main/pages-sign-up.html", {
        "employment_statuses": EMPLOYMENT_STATUS,
        "account_types": ACCOUNT_TYPES,
        "all_id_types": PREFERRED_ID_TYPE,
        "citizenship_statuses": CITIZENSHIP_STATUSES,
        "employment_types": EMPLOYMENT_TYPE,
        "marital_choices": MARITAL_CHOICES,
    })




@login_required
def chartpage(request):
    return render(request, "dashboard/major/charts-chartjs.html", {})

@login_required
def transactions(request):
    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response

    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    transaction_records = Transaction.objects.filter(user=request.user).order_by("-pk")[:10]
    return render(request, "dashboard/major/transactions.html", {"transactions": transaction_records, "notifications": notifications, "notification_count": notifications.count(),})

@login_required
def transfer_funds(request):
    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response

    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    transaction_records = Transaction.objects.filter(user=request.user)
    accounts = Account.objects.filter(customer=request.user, activated=True)
    
    
    return render(request, "dashboard/major/transfer_funds.html", {"notification_count": notifications.count(), 'accounts': accounts, "notifications": notifications})




@csrf_exempt
def validate_transfer(request):
    
    if request.method == 'POST':
        from_account_id = request.POST.get('from_account')
        amount = request.POST.get('amount')
        to_account = request.POST.get('to_account')

        otp_code = generate_4_digit_code()

        print(not request.user.otp_code)
        # Send OTP To mail
        if not request.user.otp_code:
            request.user.otp_code = otp_code
            request.user.save()
            send_otp_code_verification(
                to_email=request.user.email, 
                otp_code=otp_code, 
                transaction_type="transfer"
            )

        # Get the account and validate the balance
        try:
            from_account = Account.objects.get(id=from_account_id)
            if from_account.balance < float(amount):
                return JsonResponse({"success": False, "message": "Insufficient funds in the selected account."})
        except Account.DoesNotExist:
            return JsonResponse({"success": False, "message": "Selected account does not exist."})

        # Validate other details (like the existence of the to_account)
        # This is just an example, you'd implement your own logic for validating the recipient's account

        # Send OTP To mail

        return JsonResponse({"success": True, "message": "Enter your Password"})
    return JsonResponse({"success": False, "message": "Invalid request."})

@csrf_exempt
def final_process_transfer(request):

    if request.method == "POST":
        data = json.loads(request.body)


        from_account_id = data.get('from_account')
        amount = int(data.get('amount'))
        to_account = data.get('to_account')

        # Process the transfer
        from_account = Account.objects.get(id=from_account_id)
        amount = int(data.get('amount'))

        if from_account.balance < amount:
            return JsonResponse({"success": False, "message": "Insufficient funds."})

        # Deduct the amount from the sender's account
        from_account.balance -= amount
        from_account.save()

        # You'd also want to add code to credit the recipient's account

        # Log the transfer
        Transfer.objects.create(
            user=request.user,
            from_account=from_account,
            account_holder_name=data.get('beneficiary_name'),
            account_number=data.get('to_account'),
            ach_routing=data.get('ach_routing'),
            account_type=from_account.account_type,
            bank_name=data.get('bank_name'),
            amount=amount,
            address=data.get('address')
        )

        Transaction.objects.create(
            user=request.user,
            transaction_type="TRANSFER",
            from_account=from_account,
            amount=amount,
        )

        send_transaction_mail(
            to_email=request.user.email,
            message="We notice you initiated a transfer. \
                Your transaction is pending for now. \
                We are reviewing your request. \
                We will let you know the status of your transfer immediately we confirm it."
            )

        return JsonResponse({"success": True, "message": "Transfer is processing. You will be contacted in due time once it is successful."})
    
    return JsonResponse({"success": False, "message": "Invalid request."})

    

@csrf_exempt
def resend_otp_code(request):
    try:
        transaction_type = json.loads(request.body)['transaction_type']
        print("Transaction Type: ", transaction_type)

        otp_code = generate_4_digit_code()
        request.user.otp_code = otp_code
        request.user.save()
        send_otp_code_verification(
            to_email=request.user.email, 
            otp_code=otp_code, 
            transaction_type=transaction_type
        )
        return JsonResponse({"success": True, "message": "OTP was resent successfully."})
    except Exception as e:
         print(e)
         return JsonResponse({"success": False, "message": "Problem encountered resending OTP code."})

@csrf_exempt
def confirm_transfer(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    # Continue from read notification count
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    if request.method == 'POST':
        data = json.loads(request.body)
        user = request.user

        # Validate password
        password = data.get('password')
        print(password)
        user = request.user
        if not user.otp_code == password:
            return JsonResponse({"success": False, "message": "Invalid OTP."})
        
        return JsonResponse({"success": True, "message": "Successful."})


        




# @login_required
# def create_loan(request):

#     return render(request, "dashboard/major/loan_create.html", {})

# @login_required
# def loans(request):

#     return render(request, "dashboard/major/loan.html", {})

@login_required
def create_loan(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    user_all_accounts = Account.objects.filter(customer=request.user)



    if request.method == 'POST':
        account_id = request.POST['account_id']
        
        loan_type = request.POST['loan_type']
        loan_amount = request.POST['loan_amount']
        loan_term = request.POST['loan_term']


        # Get the the account instance
        try:
            current_account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            pass
        # Create loan with appropriate data
        print(
            "LOAN_TYPE: ", loan_type, 
            "\nLOAN_AMOUNT: ", loan_amount, 
            "\nLOAN_TERM: ", loan_term, 
            "\nACCOUNT_ID: ", account_id
        )

        loan = Loan.objects.create(
            customer=request.user,
            loan_type=loan_type,
            amount=loan_amount,
            loan_term=loan_term,
            account=current_account
        )

        return redirect('loan_detail', pk=loan.id)

    return render(request, "dashboard/major/loan_create.html", {
        "user_accounts": user_all_accounts, 
        "notifications": notifications, 
        "notification_count": notifications.count(),
    })

@login_required
def loans(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    user_loans = Loan.objects.filter(customer=request.user)
    loan_count = user_loans.count()
    
    return render(request, "dashboard/major/loan.html", {
        'loans': user_loans,
        'loan_count': loan_count,
        "notifications": notifications
    })

@login_required
def loan_detail(request, pk):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    loan = Loan.objects.get(id=pk, customer=request.user)
    return render(request, "dashboard/major/loan_detail.html", {'loan': loan, "notifications": notifications, "notification_count": notifications.count(),})



@login_required
def confirm_loan_activation_payment(request, pk):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    loan = Loan.objects.get(id=pk)
    
    if request.method == 'POST':
        receipt = request.FILES.get('receipt')
        
        if receipt:
            # Assuming you have a field for the receipt in the Card model
            loan.activation_receipt = receipt
            loan.applied_for_activation = True
            loan.save()

            # Send an email to the client
            send_ordinary_user_mail(
                to_email=request.user.email,
                subject="Loan Request Received",
                message="Your loan request has been received by our team. \
                    We are currently reviewing your documents and will revert \
                        back to you within a 24 hours timeframe.",

            )

            send_admin_mail(
                subject="A User Requested for Loan Approval",
                message=f"A user with email {request.user.email} made a request for loan approval. \
                    Please review their documents and confirm or reject their loan."
            )
            
            messages.success(request, 'Your loan will be activated soon. Please await further instructions.')
        else:
            messages.error(request, 'Please upload a valid receipt.')
        
        return redirect('loan_detail', pk=loan.id)

    return render(request, 'dashboard/major/loan_detail.html', {'loan': loan, "notifications": notifications, "notification_count": notifications.count(),})


@login_required
@require_http_methods(["GET", "POST"])
def profile(request):

    # inactive_redirect = go_to_inactive_state(request)
    # if inactive_redirect:
    #     return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    user = request.user
    # user_profile_image = user.profile_image.url
    # print(user.profile_image.url)

    # Print the full URL being accessed
    absolute_url = request.build_absolute_uri()  # Includes the domain and scheme
    print(f"Absolute URL: {absolute_url}")

    # Print the relative path (without the domain)
    relative_path = request.get_full_path()  # Includes the query string
    print(f"Relative Path: {relative_path}")

    domain = absolute_url.split(relative_path)[0]

    print(f"Server Host: {domain}")

    

    

    

        
    return render(request, "dashboard/major/profile.html", {"notifications": notifications, "notification_count": notifications.count(),})


@login_required
def update_personal_info(request):

    

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')
        user.save()
        return JsonResponse({'message': 'Personal information updated successfully.'})
    return JsonResponse({'error': 'Invalid request.'}, status=400)




@login_required
def update_address_info(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    if request.method == 'POST':
        user = request.user
        user.address = request.POST.get('address')
        user.city = request.POST.get('city')
        user.state = request.POST.get('state')
        user.postal_code = request.POST.get('postal_code')
        user.save()
        return JsonResponse({'message': 'Address updated successfully.'})
    return JsonResponse({'error': 'Invalid request.'}, status=400)





@login_required
def update_password(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        print(new_password)
        print(confirm_password)

        
        
        if new_password != confirm_password:
            print("New passwords do not match.")
            return JsonResponse({'error': 'New passwords do not match.'}, status=400)
        
        if not request.user.check_password(old_password):
            print("Current password is incorrect.")
            return JsonResponse({'error': 'Current password is incorrect.'}, status=400)
        
        request.user.set_password(new_password)
        request.user.save()
        # Prevents logging out after password change
        update_session_auth_hash(request, request.user)  
        print("Password updated successfully.")
        return JsonResponse({'message': 'Password updated successfully.'})
    return JsonResponse({'error': 'Invalid request.'}, status=400)



@login_required
def support_page(request):

    # inactive_redirect = go_to_inactive_state(request)
    # if inactive_redirect:
    #     return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    supports = Support.objects.filter(user=request.user).order_by("-id")[:5]
    return render(request, "dashboard/major/support_page.html", {"supports": supports,"notifications": notifications, "notification_count": notifications.count(),})

@login_required
def account_details(request, pk):


    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]


    user = request.user
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        raise Http404
    
    transactions = Transaction.objects.filter(from_account=account, user=user).order_by("-pk")[0:10]
    

    return render(
        request, 
        "dashboard/major/account_details.html", 
        {
            "account": account, 
            "transactions": transactions,
            "notifications": notifications,
            "notification_count": notifications.count(),
        }
    )


@login_required
def accounts_list(request):


    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]


    accounts = Account.objects.filter(customer=request.user)

    account_count = accounts.count()

    return render(request, "dashboard/major/account_list.html", {"accounts": accounts, 'account_count': account_count, "notifications": notifications, "notification_count": notifications.count(),})


@login_required
def create_bank_account(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    user = request.user
    existing_account_types = Account.objects.filter(customer=user).values_list('account_type', flat=True)
    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    account_types_to_create = [
        ('CHECKING', 'CHECKING'),
        ('SAVINGS', 'SAVINGS'),
        ('MONEY MARKET', 'MONEY MARKET'),
        ('PLATINUM', 'PLATINUM'),
    ]

    EMPLOYMENT_STATUS = [
        "Employed",
        "Self-employed",
        "Unemployed",
        "Retired"
    ]

    PREFERRED_ID_TYPE = [
        "National ID",
        "Driver Licence",
        "Passport"
        
    ]

    EMPLOYMENT_TYPE = [
        "Full-time",
        "Part-time",
        "Contract", 
        "Temporary",
    ]

    MARITAL_CHOICES = [
        "Married",
        "Single",
        "Divorced",
    ]

    # if request.method == "POST":
    #     selected_account_type = request.POST.get("account_type")

    #     if selected_account_type in existing_account_types:
    #         messages.warning(request, f"You already have a {selected_account_type} account.")
    #         return redirect('create_account')


    #     account = Account(
    #         customer=user,
    #         account_type=selected_account_type,
    #     )


    #     # Handle user-specific inputs for different account types
    #     if selected_account_type == "SAVINGS":
    #         account.yearly_income = request.POST.get("yearly_income")
    #         account.proof_of_funds = request.FILES.get("proof_of_funds")
    #         account.id_card_front = request.FILES.get("id_card_front")
    #         account.id_card_back = request.FILES.get("id_card_bac k")
    #         account.credit_card_image = request.FILES.get("credit_card_image")
    #         account.minimum_balance = 1000  # Assigned by the bank

    #     elif selected_account_type == "MONEY MARKET":
    #         account.initial_balance = request.POST.get("initial_balance")
    #         account.proof_of_employment = request.FILES.get("proof_of_employment")
    #         account.utility_bill = request.FILES.get("utility_bill")
    #         account.transaction_limit = 10  # Assigned by the bank

    #     elif selected_account_type == "PLATINUM":
    #         account.deposit_amount = request.POST.get("deposit_amount")
    #         account.beneficiary_name = request.POST.get("beneficiary_name")
    #         account.beneficiary_id_proof = request.FILES.get("beneficiary_id_proof")
    #         account.term_length = 12  # Assigned by the bank

    #     elif selected_account_type == "CHECKING":
    #         account.initial_deposit = request.POST.get("initial_deposit")
    #         account.overdraft_protection = request.POST.get("overdraft_protection") == 'on'
    #         account.id_card = request.FILES.get("id_card")

    #     account.save()

    #     send_beautiful_html_email_create_account(
    #         account_name=request.user.first_name + " " + request.user.last_name, 
    #         initial_deposit=account.initial_deposit,
    #         info_details= "To activate your account, please log in to your dashboard and make an initial deposit using the provided account details.",
    #         account_details={
    #             "Account Number": account.account_number,
    #             "Account Type": selected_account_type.capitalize(),
    #             "Branch": account.location,
    #             "Balance": f"${account.balance}",
    #             "ACH Routing": account.ach_routing,
    #             "Activation": "Pending",
    #         },  
    #         to_email=request.user.email
    #     )

    #     messages.success(request, f"{account.get_account_type_display()} account created successfully.")
    #     return redirect('accounts')

    return render(request, "dashboard/major/create_account.html", {
        'existing_account_types': existing_account_types,
        'account_types_to_create': account_types_to_create,
        "notifications": notifications,
        "notification_count": notifications.count(),
        "employment_statuses": EMPLOYMENT_STATUS,
        "all_id_types": PREFERRED_ID_TYPE,
        "employment_types": EMPLOYMENT_TYPE,
        "marital_choices": MARITAL_CHOICES,
    })


@login_required
def confirm_account_activation_payment(request, pk):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    account = Account.objects.get(id=pk)
    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    
    if request.method == 'POST':
        receipt = request.FILES.get('receipt')
        
        if receipt:
            # Assuming you have a field for the receipt in the Card model
            account.activation_receipt = receipt
            account.applied_for_activation = True
            account.save()

            
            
            messages.success(request, 'Your account will be activated soon.')
        else:
            messages.error(request, 'Please upload a valid receipt.')
        
        return redirect('accounts_detail', pk=account.id)

    return render(request, 'dashboard/major/account_detail.html', {'account': account, "notifications": notifications, "notification_count": notifications.count(),})


@login_required
def debit_card_list(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]


    cards = Card.objects.filter(user=request.user).filter(card_category="Debit").order_by("-pk")
    card_count = cards.count()
    return render(request, 'dashboard/major/debit/card_list.html', {'card_count': card_count,'cards': cards, "notifications": notifications, "notification_count": notifications.count(),})

@login_required
def debit_card_detail(request, pk):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    card = Card.objects.get(pk=pk)
    return render(request, 'dashboard/major/debit/card_detail.html', {'card': card, "notifications": notifications, "notification_count": notifications.count(),})


@login_required
def confirm_debit_card_payment(request, pk):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    
    card = Card.objects.get(id=pk)
    
    if request.method == 'POST':
        receipt = request.FILES.get('receipt')
        
        if receipt:
            # Assuming you have a field for the receipt in the Card model
            card.confirmation_receipt = receipt
            card.applied_for_activation = True
            card.save()
            
            messages.success(request, 'Payment confirmed! Your card will be activated soon.')
        else:
            messages.error(request, 'Please upload a valid receipt.')
        
        return redirect('debit_card_detail', pk=card.id)

    return render(request, 'dashboard/major/debit/create_card.html', {'card': card, "notifications": notifications, "notification_count": notifications.count(),})


@login_required
def create_debit_card(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    accounts = Account.objects.filter(customer=request.user)

    

    

    # Get the types of cards the user hasn't created yet
    existing_card_types = Card.objects.filter(user=request.user).values_list('card_type', flat=True)
    available_card_types = [card for card in ['MasterCard', 'Visa'] if card not in existing_card_types]

    if request.method == 'POST':
        data = request.POST
        try:
            data = json.loads(request.body)  # Parse JSON body
            card_type = data.get('card_type')
            account_type = data.get('account_type')
            passcode = data.get('passcode')
            passcode2 = data.get('passcode2')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.', 'pass': False}, status=400)
        
        print("Account Type: ", account_type)
        print("Card Type: ", card_type)

        print("Passcode: ", passcode)
        print("Passcode 2: ", passcode2)

        if passcode != passcode2:
            return JsonResponse({'error': 'Card Pin must be a match', 'pass': False}, status=400)
        
        if not len(passcode) == 4:
            return JsonResponse({'error': 'Please enter a four digit Card Pin', 'pass': False}, status=400)

        try:
            main_account = Account.objects.get(id=account_type)
        except Account.DoesNotExist:
            return JsonResponse({'error': f'Account does not exist.', 'pass': False}, status=400)
        

        # Check if the user already has a card of this type
        if Card.objects.filter(user=request.user, card_type=card_type).exists():
            return JsonResponse({'error': f'You already have a {card_type} card.'}, status=400)

        # If the user doesn't have this card type, create a new one
        card = Card(user=request.user, card_type=card_type, card_category="Debit", )
        card.account = main_account
        card.card_passcode = passcode
        card.generate_card_number()
        card.generate_cvv()
        card.generate_expiration_date()
        card.generate_fee_for_card()
        card.save()

        return JsonResponse({'message': 'Card created successfully!', 'card_id': card.id, 'pass': True})
    

    return render(request, 'dashboard/major/debit/create_card.html', {'accounts': accounts, 'available_card_types': available_card_types, "available_card_count": len(available_card_types), "notifications": notifications, "notification_count": notifications.count(),})


@login_required
def connect_debit_card(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    

    # Get the types of cards the user hasn't created yet
    # existing_card_types = Card.objects.filter(user=request.user).values_list('card_type', flat=True)
    available_card_types = ['Credit Card', 'Debit Card']

    if request.method == 'POST':
        card_type = request.POST.get('card_type')
        card_number = request.POST.get('card_number')
        cvv = request.POST.get('cvv')
        name_in_card = request.POST.get('name_in_card')
        card_expiration = request.POST.get('card_expiration')


        # Check if the user already has a card of this type
        # if Card.objects.filter(user=request.user, card_type=card_type).exists():
        #     return JsonResponse({'error': f'You already have a {card_type} card.'}, status=400)

        # If the user doesn't have this card type, create a new one
        card = Card(user=request.user)
        card.card_category = card_type
        card.state = "Connected"
        card.card_number=card_number
        card.cvv = cvv
        card.name_in_card=name_in_card 
        card.card_expiration=card_expiration
        card.is_real_card = True
        card.save()

        return JsonResponse({'message': 'Card created successfully!', 'card_id': card.id})
    

    return render(request, 'dashboard/major/debit/connect_card.html', {'available_card_types': available_card_types, "notifications": notifications, "notification_count": notifications.count(),})



@login_required
def settings(request):

    
    transactions = Transaction.objects.filter(user=request.user).order_by("-pk")[0:10]

    return render(request, 'dashboard/major/account_settings.html', {"transactions": transactions})









# ------------------------- MAIN PAGES -------------------------------------
def main_home(request):

    # inactive_redirect = go_to_inactive_state(request)
    # if inactive_redirect:
    #     return inactive_redirect  # Return the redirect response

    
    account_model_meta = {
        'model_name': Account._meta.model_name,  # Account model name
        'app_label': Account._meta.app_label,    # App name
    }

    return render(request, "main/index.html", {})

def about_page(request):
    
    return render(request, "main/about.html", {})


def cancer_page(request):
    return render(request, "main/cancerpage.html", {})

def personal_page(request):
    return render(request, "main/personal.html", {})


def business(request):
    return render(request, "main/business.html", {})


def wealth(request):
    return render(request, "main/wealth.html", {})

def call_us(request):
    return render(request, "main/call-us.html", {})


def terms_services(request):
    return render(request, "main/terms_services.html", {})

def routing_number(request):
    return render(request, "main/routing_number.html", {})

def privacy_security(request):
    return render(request, "main/privacy_security.html", {})
    

# View to handle password reset request
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        reset_email_url = request.POST.get('password_url')
        user = User.objects.filter(email=email).first()
        
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(f'/password-reset/{uid}/{token}/')
            print("Reset Email link: ", reset_email_url, "  -  ", reset_url)
            
            send_password_reset_email(to_email=user.email, reset_link=reset_url)
            return JsonResponse({'success': 'Password reset email sent'})
        else:
            return JsonResponse({'error': 'Email address not found'}, status=404)
    return render(request, 'dashboard/major/password_reset_form.html')

# View to handle password reset form submission
def password_reset_confirm(request, uidb64, token):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    
                    return JsonResponse({'success': 'Password reset successfully'})
                else:
                    return JsonResponse({'error': 'Invalid token'}, status=400)
            except Exception as e:
                return JsonResponse({'error': 'Invalid request'}, status=400)
        else:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)

    return render(request, 'dashboard/major/password_reset_confirm.html')





def password_reset_complete(request):
    return render(request, 'dashboard/major/password_reset_complete.html')



@csrf_exempt
def send_payment_transfer_confirmation_from_user(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        payment_method = request.POST.get('payment_method')
        amount = request.POST.get('amount', None)
        confirmation_receipt = request.FILES.get('confirmation_receipt')

        if not payment_method or not confirmation_receipt:
            return JsonResponse({'success': False, 'message': 'Please provide all required information.'}, status=400)

        # Save payment details in the database
        payment = Payment.objects.create(
            user=user,
            transaction_type="transfer",
            payment_method=payment_method,
            confirmation_receipt=confirmation_receipt,
            reason="Payment",
            amount=amount,
        )
        
        return JsonResponse({'success': True, 'message': 'The request to to confirm payment is processing. We will attend to it as soon as possible.'})
    return JsonResponse({'success': False, 'message': 'Unauthorized or invalid request.'}, status=403)


@csrf_exempt
def send_tax_payment_transfer_confirmation_from_user(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        payment_method = request.POST.get('payment_method')
        amount = request.POST.get('amount')
        confirmation_receipt = request.FILES.get('confirmation_receipt')

        if not payment_method or not confirmation_receipt:
            return JsonResponse({'success': False, 'message': 'Please provide all required information.'}, status=400)

        # Save payment details in the database, ensuring it's marked as a tax payment
        payment = Payment.objects.create(
            user=user,
            transaction_type="transfer",
            payment_method=payment_method,
            confirmation_receipt=confirmation_receipt,
            is_tax=True,
            reason="Tax Payment for transfer",
            amount=amount,
        )

        send_ordinary_user_mail(
            to_email=request.user.email,  
            subject="Request to confirm payments", 
            message="The request to to confirm payment is processing. We will attend to it as \
                soon as possible."
        )

        send_admin_mail(
            subject="Request to confirm payments",
            message=f"A user {request.user.email} just initiated a transfer and uploaded \
                payment receipts. Please verify the user's credentials.")

        return JsonResponse({'success': True, 'message': 'Tax payment receipt submitted successfully!'})

    return JsonResponse({'success': False, 'message': 'Unauthorized or invalid request.'}, status=403)



@login_required
def fund_account(request, account_id):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    try:
        account = Account.objects.get(pk=account_id)
    except Account.DoesNotExist:
        raise Http404
    

    
    return render(request, 'dashboard/major/fund_account.html', {"account": account}) 



@csrf_exempt
def validate_fund_account(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        print(data)

        account_id = data.get("account_id")
        amount = int(data.get("amount"))

        try:
            account = Account.objects.get(pk=account_id)
            print(account.confirmation_payment_amount)
        except Account.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Account does not exist.'})

        Transaction.objects.create(
            user=request.user,
            transaction_type="DEPOSIT REQUEST",
            from_account=account,
            amount=amount,
        )

        send_transaction_mail(
            to_email=request.user.email,
            message=f"Hi, {request.user.first_name}. We noticed you triggered a funding request. Please ensure you send your payment receipts to confirm your funding using the payment methods.", 
            subject="Request to fund account"
        )

        send_admin_mail(
            message=f"User with email: ${request.user.email} just initiated a funding request to fund their account with $${amount}. Please check the dashboard if the request payment request methods were followed. Thank you. ", 
            subject="Admin Message Alert"
        )

        return JsonResponse({'success': True, 'message': 'Worked'})
        
    else:
        return JsonResponse({'success': False, 'message': 'Wrong Method'})
    


@csrf_exempt
def validate_fund_card(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        print(data)

        card_id = data.get("card_id")
        amount = int(data.get("amount"))

        try:
            card = Card.objects.get(pk=card_id)
            # print(card.confirmation_receipt)
        except Card.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Card does not exist.'})
        
        account_for_card = card.account

        print(account_for_card)
        print(type(float(account_for_card.balance)))
        print(type(float(amount)))
        print(type(amount))

        account_balance = float(account_for_card.balance)
        fund_amount = float(amount)

        print(account_balance)
        print(fund_amount)

        if (account_balance < fund_amount):
            return JsonResponse({'success': False, 'message': f'Amount in {account_for_card.account_type} is not sufficient to fund your card.'.capitalize() })


        Transaction.objects.create(
            user=request.user,
            transaction_type="FUND CARD",
            amount=amount,
        )

        Payment.objects.create(
            user=request.user,
            transaction_type="transfer",
            payment_method="crypto",
            is_tax=False,
            reason="User Tries Funding Card",
            amount=amount,
        )

        send_transaction_mail(
            to_email=request.user.email,
            message=f"Hi, {request.user.first_name}. We noticed you triggered a card funding request. Please ensure you send your payment receipts to confirm your funding using the payment methods as provided in your dashboard.", 
            subject="Request to fund card"
        )

        send_admin_mail(
            message=f"User with email: ${request.user.email} just initiated a card funding request to fund their card with ${amount}. Please check the dashboard if the request payment request methods were followed. Thank you. ", 
            subject="Admin Message Alert"
        )

        return JsonResponse({'success': True, 'message': 'Worked'})
        
    else:
        return JsonResponse({'success': False, 'message': 'Wrong Method'})



def admin_send_mail_view(request):

    inactive_redirect = go_to_inactive_state(request)
    if inactive_redirect:
        return inactive_redirect  # Return the redirect response



    all_users = User.objects.all()

    

    return render(request, 'dashboard/major/admin_send_mail.html', {
        "all_users": all_users
    })


def account_is_inactive_view(request):
    if request.user.user_account_is_active:
        return redirect("dasboard_home")
    return render(request, 'dashboard/major/inactiveuser_page.html', {})
















