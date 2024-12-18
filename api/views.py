from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .constants import ACCOUNTS

from django.contrib.auth import update_session_auth_hash
import json

from .email import (
    send_beautiful_html_email_create_account, 
    send_admin_mail, 
    send_ordinary_user_mail,
    send_mail_from_admin_to_user,
    send_mail_for_payment_options,
)

from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from .helpers import check_email, is_valid_password

from rest_framework.views import APIView

from django.contrib.auth import authenticate, login

from django.shortcuts import render
from app.models import Account, Transaction, Loan, Card

from django.contrib.auth import get_user_model

from django.db.models import Sum, Count
from django.utils import timezone
from collections import defaultdict
import calendar
from django.db.models.functions import ExtractMonth

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.models import Support
from .serializers import SupportSerializer, AccountActivationSerializer
from app.models import CustomUser
from django.contrib import messages

from django.conf import settings


from .email import send_beautiful_html_email_create_user


User = get_user_model()


@api_view(['POST'])
def register_api_view(request):
    if request.method == 'POST':

        print(request.data)

        required_fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'ssn',
            'annual_income', 'employment_status',
            'profile_image', 'front_id_image', 'back_id_image',
            'password', 'password_confirmation'
        ]


        first_name=request.data.get('first_name')
        last_name=request.data.get('last_name')
        email=request.data.get('email')       
        phone_number=request.data.get('phone_number')
        ssn=request.data.get('ssn')       
        annual_income=request.data.get('annual_income')

        
        employment_type = request.data.get("employment_type")
        employer_name = request.data.get("employer_name")
        employer_phone = request.data.get("employer_phone")
        job_start_date = request.data.get("job_start_date")
        job_end_date = request.data.get("job_end_date")
        employment_status=request.data.get('employment_status')
        job_title=request.data.get('job_title')
        
        proof_of_employment = request.FILES.get("proof_of_employment")
        proof_of_income = request.FILES.get("proof_of_income")

        tax_identity_number = request.FILES.get("tax_identity_number")

        

        
        


        country=request.data.get('country')
        state=request.data.get('state')
        postal_code=request.data.get('postal_code')
        dob=request.data.get('dob')
        city=request.data.get('city')
        address=request.data.get('address')
        government_id_type=request.data.get('government_id_type')
        citizenship_status=request.data.get('citizenship_status')
        government_id_number=request.data.get('government_id_number')
        profile_image=request.FILES.get('profile_image')
        front_id_image=request.FILES.get('front_id_image')
        back_id_image=request.FILES.get('back_id_image')
        password=request.data.get('password')
        
        password_confirmation=request.data.get('password_confirmation')

        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            return Response({"error": "User with email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        

        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != password_confirmation:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            print(dob)
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,

                ssn=ssn,
                tax_identity_number=tax_identity_number,
                annual_income=annual_income,
                employment_status=employment_status,
                job_title=job_title,
                city=city,
                postal_code=postal_code,
                dob=dob,
                address=address,
                country=country,
                state=state,
                profile_image=profile_image,
                front_id_image=front_id_image,
                back_id_image=back_id_image,
                government_id_type=government_id_type,
                citizenship_status=citizenship_status,
                government_id_number=government_id_number,

                employment_type=employment_type,
                employer_name=employer_name,
                employer_phone=employer_phone,
                job_start_date=job_start_date,
                job_end_date=job_end_date,
                proof_of_employment=proof_of_employment,
                proof_of_income=proof_of_income,
                
            )
            user.set_password(password)
            user.save()

            


            send_beautiful_html_email_create_user(
                bank_id=user.bank_id,
                account_details=f"Account Type: {user.preferred_account_type}, Balance: $0",
                to_email=user.email,
            )

            send_admin_mail(
                subject="New user Alert",
                message="Hi, a new user just registered and is ready for activation",
            )

            return Response({"message": "User registered successfully. Check your email for details."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        





@api_view(['POST'])
def login_with_bank_id_api(request):
    bank_id = request.data.get('bank_id')
    password = request.data.get('password')

    

    print(f"Details {bank_id} {password}")

    try:
        user = CustomUser.objects.get(bank_id=bank_id)
        user = authenticate(request, email=user.email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            send_admin_mail(
                subject="Login Alert",
                message=f"User with email: {request.user.email} just logged into the app."
            )
            send_ordinary_user_mail(
                to_email=request.user.email,
                subject="Login Alert",
                message="We noticed a login attempt you made. Please know we take security very seriously at \
                    FirstCitizen Bank and we are dedicated to giving you the best banking experience."
            )

            # Change the redirect url here if you change the dashboard
            return Response({'message': 'Login successful', 'redirect_url': '/dashboard'}, status=status.HTTP_200_OK)
        else:
            messages.success(request, "Invalid credentials")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



def get_monthly_transactions(account_type, year, user):
    transactions = Transaction.objects.filter(
        from_account__account_type=account_type,
        timestamp__year=year
    ).annotate(month=ExtractMonth('timestamp')).values('month').annotate(total=Sum('amount')).order_by('month')

    monthly_data = defaultdict(lambda: 0)  # Default to 0 if no data for a month
    for transaction in transactions:
        monthly_data[transaction['month']] = transaction['total']

    # Return data as list of amounts for each month
    return [int(monthly_data[month]) for month in range(1, 13)]



@api_view(['GET'])
def generate_transaction_chart(request):

    current_year = timezone.now().year

    checking_data = get_monthly_transactions('CHECKING', current_year)
    savings_data = get_monthly_transactions('SAVINGS', current_year)

    return Response({
        'checking_data': checking_data,
        'savings_data': savings_data,
        'months': list(calendar.month_abbr[1:]),
    }, status=status.HTTP_200_OK)




# Create your views here.
@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        first_name =  request.data.get("first_name")
        last_name =  request.data.get("last_name")
        id_card_front =  request.FILES.get("id_card_front") 
        id_card_back =  request.FILES.get("id_card_back") 
        ssn =  request.data.get("ssn") 
    
        email = request.data.get("email")
        password = request.data.get("password")
        password_confirm = request.data.get("password_confirm")

        if password != password_confirm:
            return Response({
                "detail": "Passwords must match."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({
                "detail": "Email is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        elif not password:
            return Response({
                "detail": "Password is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Check if email and password are valid entry
            email_valid_status = check_email(email)
            password_valid_status = is_valid_password(password)

            if password_valid_status.status == False:
                return Response({
                    "detail": "".join([
                        error_message for error_message in password_valid_status.error_messages
                    ])
                }, status=status.HTTP_400_BAD_REQUEST)

            if email_valid_status.status == False:
                return Response({
                    "detail": "".join([
                        error_message for error_message in email_valid_status.error_messages
                    ])
                }, status=status.HTTP_400_BAD_REQUEST)
            
    return Response({"message": "This is working"})




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_support_request(request):
    serializer = SupportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        send_admin_mail(
                subject="Login Alert",
                message=f"User with email {request.user.email} just logged into the app."
        )
        send_ordinary_user_mail(
            to_email=request.user.email,
                subject="Login Alert",
                message="We noticed a login attempt you made. Please know we take security very seriously at \
                    FirstCitizen Bank and we are dedicated to giving you the best banking experience."
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ConfirmAccountActivationAPIView(request, pk):

    receipt = request.FILES.get("receipt")
    try:
        account = Account.objects.get(id=pk, customer=request.user)
        print("Account: ", account.id)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    account.receipt = receipt
    account.applied_for_activation = True
    send_beautiful_html_email_create_account(
        account_name=request.user.first_name + " " + request.user.last_name, 
        initial_deposit=account.deposit_amount,
        info_details= "Your Activation Request for your account was sent successfully. We are reviewing your documents and payment snapshots. We get back to you within a 24 hours timeframe.",
        account_details={
            # "Account Number": account.account_number,
            "Account Type": account.account_type.capitalize(),
            # "Branch": account.location,
            "Balance": f"${account.balance}",
            # "ACH Routing": account.ach_routing,
            "Activation": "Pending",
            "Status": "RED"
        },  
        to_email=request.user.email
    )

    print("Email will be sent")

    account.save()
    return Response({'success': 'Payment confirmed! Your account will be activated soon.'}, status=status.HTTP_200_OK)



import json

@api_view(['POST'])
def connect_new_card(request):
    if request.method == 'POST':
    
        data = request.data
        
        card_category = data.get('card_category')
        card_type = data.get('card_type')
        card_number = data.get('card_number')
        cvv = data.get('cvv')
        name_in_card = data.get('name_in_card')
        card_expiration = data.get('card_expiration')
        state = data.get('state')
        passcode = data.get('passcode')

        print("DATA: ",card_category, card_type, card_number, cvv, name_in_card, card_expiration)

        # Check if the user already has a card of this type
        # if Card.objects.filter(user=request.user, card_category=card_category).exists():
        #     return Response({'error': f'You already have a {card_category} card.'}, status=status.HTTP_400_BAD_REQUEST)

        # If the user doesn't have this card type, create a new one

        if not len(passcode) == 4:
            return Response({'error': 'Please enter your 4 digit card pin.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not len(cvv) == 3:
            return Response({'error': 'CVV is the 3 digit pin at the back of your Card'}, status=status.HTTP_400_BAD_REQUEST)
        
        card = Card.objects.create(
            user=request.user,
            card_type=card_type,
            card_category=card_category,
            card_number=card_number,
            cvv=cvv,
            state=state,
            name_in_card=name_in_card,
            card_expiration=card_expiration,
            is_real_card = True,
        )
        
        
        return Response({'message': 'Card created successfully!', 'card_id': card.id}, status=status.HTTP_201_CREATED)



@api_view(['GET'])
def get_all_account_data(request):
    
    # Return the accounts as a JSON response
    # Get the deposit amounts for the accounts
    # new_acct = list(map(lambda account: {
    #     "account_type": account["account_type"], 
    #     "amount_to_deposit": account["amount_to_deposit"],
    #     }, ACCOUNTS))
    # i = list(filter(lambda account: account["amount_to_deposit"] > 4000, new_acct))
    # print(i)
    return Response({'data': ACCOUNTS}, status=status.HTTP_200_OK)



@api_view(['POST'])
def create_account_view_api(request):

    account_type = request.data.get("account_type")

    government_id_type = request.data.get("government_id_type")
    government_id_number = request.data.get("government_id_number")
    citizenship_status = request.data.get("citizenship_status")

    employment_status = request.data.get("employment_status")
    employment_type = request.data.get("employment_type")
    employer_name = request.data.get("employer_name")
    employer_phone = request.data.get("employer_phone")
    job_start_date = request.data.get("job_start_date")
    job_end_date = request.data.get("job_end_date")

    credit_score = request.data.get("credit_score")

    annual_income = request.data.get("annual_income")


    front_id_image = request.FILES.get("front_id_image")
    back_id_image = request.FILES.get("back_id_image")
    proof_of_employment = request.FILES.get("proof_of_employment")
    proof_of_income = request.FILES.get("proof_of_income")
    utility_bill = request.FILES.get("utility_bill")
    address = request.data.get("address")



    # Joint Account
    joint_account_holder_first_name = request.data.get("joint_account_holder_first_name")
    joint_account_holder_last_name = request.data.get("joint_account_holder_last_name")
    joint_account_holder_ssn = request.data.get("joint_account_holder_ssn")
    joint_account_holder_address = request.data.get("joint_account_holder_address")
    joint_account_holder_email = request.data.get("joint_account_holder_email")
    joint_account_holder_phone = request.data.get("joint_account_holder_phone")
    joint_account_holder_government_id_type = request.data.get("joint_account_holder_government_id_type")
    joint_account_holder_government_id_number = request.data.get("joint_account_holder_government_id_number")
    joint_account_holder_front_id_image = request.data.get("joint_account_holder_front_id_image")
    joint_account_holder_back_id_image = request.data.get("joint_account_holder_back_id_image")

    #   Check if account already exists
    account_exists = Account.objects.filter(account_type=account_type, customer=request.user).exists()

    if account_exists:
        return Response({
            "message": f"You already have a {account_type} Account. \
                         You cannot create one again. Check if the account is an active account.", 
                         "success": False,
            }, status=status.HTTP_200_OK)



    try:
        # Create account but make it inactive or red
        account = Account.objects.create(
            account_type=account_type,
            customer=request.user,

            
            # applied_for_activation=True,
            utility_bill=utility_bill,
            address=address,
            credit_score=credit_score,

            # government_id_type=government_id_type,
            # government_id_number=government_id_number,
            # # Files
            # front_id_image=front_id_image,
            # back_id_image=back_id_image,


            # citizenship_status=citizenship_status,

            # Employment
            employment_status=employment_status,
            employment_type=employment_type,
            employer_name=employer_name,
            employer_phone=employer_phone,
            job_start_date=job_start_date,
            job_end_date=job_end_date,
            proof_of_employment=proof_of_employment,
            proof_of_income=proof_of_income,
            annual_income=annual_income,

            # Joint account holder
            joint_account_holder_first_name=joint_account_holder_first_name,
            joint_account_holder_last_name=joint_account_holder_last_name,
            joint_account_holder_ssn=joint_account_holder_ssn,
            joint_account_holder_address=joint_account_holder_address,
            joint_account_holder_email=joint_account_holder_email,
            joint_account_holder_phone=joint_account_holder_phone,
            joint_account_holder_government_id_type=joint_account_holder_government_id_type,
            joint_account_holder_government_id_number=joint_account_holder_government_id_number,
            joint_account_holder_front_id_image=joint_account_holder_front_id_image,
            joint_account_holder_back_id_image=joint_account_holder_back_id_image,
        )

        account.generate_deposite_amount()
        account.save()

        return Response({"message": "Account was created. In order to activate account you must pay \
                         a fixed amount to activate using one of the payment method",
                         "account_id": account.id,
                         "success": True,
                        }, status=status.HTTP_200_OK)
        # Tell the user to deposit a given amount to the account

        pass
    except Exception as e:
        print(e)
        return Response({"message": f"Bad Input: {e}"}, status=status.HTTP_400_BAD_REQUEST)
    

    



@api_view(['POST'])
def confirm_new_card_activation(request, pk):

    print(request.data)

    card = Card.objects.get(id=pk)
    
    if request.method == 'POST':
        receipt = request.FILES.get('receipt')
        
        if receipt:
            # Assuming you have a field for the receipt in the Card model
            card.confirmation_receipt = receipt
            card.applied_for_activation = True
            card.save()
            
            # messages.success(request, 'Payment confirmed! Your card will be activated soon.')
            return Response({"success": True, "message":"Payment confirmed! Your card will be activated soon."})
        else:
            # messages.error(request, 'Please upload a valid receipt.')
            return Response({"success": False, "message":"Please upload a valid receipt."})

    
    return Response({"success": False, "message":" Bad Request"})




@api_view(['POST'])
def api_send_admin_mail(request):
    if request.method == 'POST':
        email = request.data.get("email")
        body = request.data.get("body")
        subject = request.data.get("subject")

        try:

            send_mail_from_admin_to_user(
                to_email=email,
                subject=subject,
                message=body,
            )

            print(f"Email: {email}; \n Subject: {subject}; \n Body: {body} \n" )
        
            return Response({"success": True, "message":f"Your email is has been sent to {email}"}, status=status.HTTP_200_OK)
        except:
            return Response({"success": False, "message":f"Server error email could not go through"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"success": False, "message":f"Http Method is not allowed!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def change_password_api_view(request):
    data = request.data
    new_password = data.get("new_password")
    old_password = data.get("old_password")
    confirm_password = data.get("confirm_password")

    user = request.user

    if new_password != confirm_password:
        print("New passwords do not match.")
        return Response({'error': 'New passwords do not match.', 'success': False}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user old_password is correct
    if not user.check_password(old_password):
        return Response({'error': 'Current password is incorrect.', 'success': False}, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.set_password(new_password)
    request.user.save()
    # Prevents logging out after password change
    update_session_auth_hash(request, request.user)


    return Response({'message': 'Password updated successfully.', 'success': True}, status=status.HTTP_201_CREATED)



@api_view(['POST'])
def update_profile_api_view(request):
    if request.method == "POST":
        data = request.data
        files = request.FILES

        user = request.user

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        state = data.get("state")
        city = data.get("city")
        country = data.get("country")
        address = data.get("address")
        profile_image = files.get("profile_image")

        user.first_name = first_name
        user.last_name = last_name
        user.state = state
        user.city = city
        user.country = country
        user.address = address

        if profile_image:
            user.profile_image = profile_image

        user.save()

        return Response({"message": "Profile updated successfully.", 'success': True}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Method is not allowed.", 'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['POST'])
def request_payment_method_api_view(request):

    # send_mail_for_payment_options(
    #     to_email=request.user.email,
    #     message="Here are your payment options. You can pay using the following payment options: ",
    #     subject="Payment options",
    # )

    
    
    return Response({"message": "An email has been sent to you containing the payment options.", 'success': True}, status=status.HTTP_200_OK)






















