
from django.urls import path
from .views import( 
    create_user, 
    generate_transaction_chart, 
    create_support_request, 
    login_with_bank_id_api, 
    ConfirmAccountActivationAPIView,
    # RegisterAPIView,
    connect_new_card,register_api_view, get_all_account_data, create_account_view_api,
    confirm_new_card_activation,
)

urlpatterns = [
    path('users/', create_user, name="create_user"),
    path('charts/', generate_transaction_chart, name="generate_transaction_chart"),


    path('accounts/list/', get_all_account_data, name='get_all_account_data'),
    path('accounts/create/', create_account_view_api, name='create_account_view_api'),

    path('login/', login_with_bank_id_api, name="login_with_bank_id_api"),
    path("register/", register_api_view, name="api_register"),
    path("connect-new-card/", connect_new_card, name="connect_new_card"),
    path("confirm-card-activation/<int:pk>/", confirm_new_card_activation, name="confirm_new_card"),
    

    path('support/', create_support_request, name='create_support_request'),
    path('confirm-account-activation/<int:pk>/', ConfirmAccountActivationAPIView, name='confirm_account_activation'),
]