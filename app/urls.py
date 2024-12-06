from django.urls import path
from .views import (
    home as dasboard_home, 
    main_home, 
    debit_card_list, 
    create_bank_account, 
    confirm_account_activation_payment, 
    confirm_loan_activation_payment,
    confirm_debit_card_payment, 
    debit_card_detail, 
    profile, 
    
    support_page, 
    register, 
    login_view, 
    create_debit_card, 
    LogoutView, 
    transfer_funds, 
    loans, 
    create_loan,
    loan_detail,
    account_details, 
    accounts_list, 
    connect_debit_card,
    transactions, 
    chartpage, validate_transfer, confirm_transfer,
    update_personal_info, update_address_info, update_password, settings,
    welcome_to_check_your_mail, about_page, cancer_page,
    personal_page,
    business, wealth, call_us, terms_services, 
    routing_number, privacy_security,
    resend_otp_code, send_payment_transfer_confirmation_from_user,
    send_tax_payment_transfer_confirmation_from_user,
    final_process_transfer, fund_account,
    validate_fund_account,
    validate_fund_card,
    password_reset_request, password_reset_confirm, password_reset_complete,
    admin_send_mail_view,
    account_is_inactive_view,

)

from .alternative_views import (
    confirm_credit_card_payment,
    connect_credit_card,
    create_credit_card, 
    credit_card_detail, 
    credit_card_list,
)
urlpatterns = [
    
    path('', main_home, name="main_home"),
    path('about/', about_page, name="about_page"),
    path('cancer/', cancer_page, name="cancer_page"),
    path('personal/', personal_page, name="personal_page"),
    path('business/', business, name="business"),
    path('wealth/', wealth, name="wealth"),
    path('call-us/', call_us, name="call_us"),
    path('terms-services/', terms_services, name="terms_services"),
    path('routing-numbers/', routing_number, name="routing_number"),
    path('privacy-security/', privacy_security, name="privacy_security"),






    path('login/', login_view, name="login"),
    path('logout/', LogoutView, name="logout"),
    path('register/', register, name="register"),

     path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', password_reset_complete, name='password_reset_complete'),

    
    path('welcome/', welcome_to_check_your_mail, name="welcome_to_check_your_mail"),


    path('chart/', chartpage, name="chartpage"),

    path('dashboard/', dasboard_home, name="dashboard_home"),
    path('dashboard/accounts/<int:pk>/', account_details, name="accounts_detail"),
    path('dashboard/accounts/fund/<int:account_id>/', fund_account, name="fund_account"),
    path('dashboard/accounts/fund/validate-fund-account/', validate_fund_account, name="validate_fund_account"),
    path('dashboard/accounts/', accounts_list, name="accounts"),
    path('dashboard/accounts/create/', create_bank_account, name="create_bank_account"),
    path('dashboard/confirm-account-payment/<int:pk>/', confirm_account_activation_payment, name="confirm_account_activation_payment"),

    path('dashboard/transactions/', transactions, name="transactions"),
    path('dashboard/transfer/', transfer_funds, name="transfer_funds"),


    path('dashboard/loans/', loans, name="loans"),
    path('dashboard/create-loan/', create_loan, name="create_loan"),
    path('dashboard/loan/<int:pk>/', loan_detail, name="loan_detail"),
    path('dashboard/confirm-loan-activation-payment/<int:pk>/', confirm_loan_activation_payment, name="confirm_loan_activation_payment"),



    path('dashboard/profile/', profile, name="profile"),
    path('dashboard/update_personal_info/', update_personal_info, name="update_personal_info"),
    path('dashboard/update_address_info/', update_address_info, name="update_address_info"),
    path('dashboard/update_password/', update_password, name="update_password"),



    path('dashboard/support/', support_page, name="support"),

    # Debit Card
    path('dashboard/create-debit-card/', create_debit_card, name="create_debit_card"),
    path('dashboard/connect-debit-card/', connect_debit_card, name="connect_debit_card"),
    path('dashboard/cards/debit/', debit_card_list, name="debit_card_list"),
    path('dashboard/validate-fund-card/', validate_fund_card, name="validate_fund_card"),
    path('dashboard/confirm-debit-card-payment/<int:pk>/', confirm_debit_card_payment, name="confirm_debit_card_payment"),
    path('dashboard/cards/debit/<int:pk>/', debit_card_detail, name="debit_card_detail"),
    
    # Credit Card
    path('dashboard/create-credit-card/', create_credit_card, name="create_credit_card"),
    path('dashboard/connect-credit-card/', connect_credit_card, name="connect_credit_card"),
    path('dashboard/cards/credit/', credit_card_list, name="credit_card_list"),
    path('dashboard/confirm-credit-card-payment/<int:pk>/', confirm_credit_card_payment, name="confirm_credit_card_payment"),
    
    path('dashboard/cards/credit/<int:pk>/', credit_card_detail, name="credit_card_detail"),



    path('dashboard/validate-transfer/', validate_transfer, name="validate_transfer"),
    path('dashboard/confirm-transfer/', confirm_transfer, name="confirm_transfer"),
    path('dashboard/resend-otp/', resend_otp_code, name="resend_otp_code"),
    path('dashboard/send-payment-transfer-confirmation-from-user/', send_payment_transfer_confirmation_from_user, name="send_payment_transfer_confirmation_from_user"),
    path('dashboard/send-tax-payment-transfer-confirmation-from-user/', send_tax_payment_transfer_confirmation_from_user, name="send_tax_payment_transfer_confirmation_from_user"),
    path('dashboard/final-process-transfer/', final_process_transfer, name="final_process_transfer"),



    path('dashboard/settings/', settings, name="settings"),


    # Admin send email 
    path('dashboard/send/mail/', admin_send_mail_view, name="admin_send_mail"),
    path('dashboard/account/inactive/', account_is_inactive_view, name="account_is_inactive_view"),



]



