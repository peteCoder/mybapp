
from django.http import JsonResponse
from django.contrib import messages
from .models import (
    Card, 
    Notification, 
    Account,
)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json



@login_required
def credit_card_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]


    cards = Card.objects.filter(user=request.user).filter(card_category="Credit").order_by("-pk")
    card_count = cards.count()
    return render(request, 'dashboard/major/credit/card_list.html', {'card_count': card_count,'cards': cards, "notifications": notifications, "notification_count": notifications.count(),})

@login_required
def credit_card_detail(request, pk):
    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    card = Card.objects.get(pk=pk)
    return render(request, 'dashboard/major/credit/card_detail.html', {'card': card, "notifications": notifications, "notification_count": notifications.count(),})


@login_required
def confirm_credit_card_payment(request, pk):
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
        
        return redirect('credit_card_detail', pk=card.id)

    return render(request, 'dashboard/major/credit/create_card.html', {'card': card, "notifications": notifications, "notification_count": notifications.count(),})


@login_required
def create_credit_card(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-id")[:5]
    read_notifications = Notification.objects.filter(user=request.user).filter(is_read=True).order_by("-id")[:5]

    accounts = Account.objects.filter(customer=request.user)

    # Get the types of cards the user hasn't created yet
    existing_card_types = Card.objects.filter(user=request.user).values_list('card_type', flat=True)
    available_card_types = [card for card in ['Gold', 'Platinum'] if card not in existing_card_types]

    if request.method == 'POST':
        data = request.POST
        try:
            data = json.loads(request.body)  # Parse JSON body
            card_type = data.get('card_type')
            account_type = data.get('account_type')
            passcode = data.get('passcode')
            passcode2 = data.get('passcode2')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.', 'pass': True}, status=400)
        
        print("Account Type: ", account_type)
        print("Card Type: ", card_type)
        print("Passcode: ", passcode)
        print("Passcode: ", passcode2)

        if passcode != passcode2:
            return JsonResponse({'error': 'Card Pin must be a match', 'pass': False}, status=400)
        
        if not len(passcode) == 4:
            return JsonResponse({'error': 'Please enter a four digit Card Pin', 'pass': False}, status=400)

        try:
            main_account = Account.objects.get(id=account_type)
        except Account.DoesNotExist:
            return JsonResponse({'error': f'Account does not exist.', 'pass': True}, status=400)


        # Check if the user already has a card of this type
        if Card.objects.filter(user=request.user, card_type=card_type).exists():
            return JsonResponse({'error': f'You already have a {card_type} card.', 'pass': True}, status=400)

        # If the user doesn't have this card type, create a new one
        card = Card(user=request.user, card_type=card_type, card_category="Credit")
        card.account = main_account
        card.card_passcode = passcode
        card.generate_card_number()
        card.generate_cvv()
        card.generate_expiration_date()
        card.generate_fee_for_card()
        card.save()

        return JsonResponse({'message': 'Card created successfully!', 'card_id': card.id, 'pass': True})
    

    return render(request, 'dashboard/major/credit/create_card.html', {
        'accounts': accounts, 
        'available_card_types': available_card_types, 
        "notifications": notifications, 
        "notification_count": notifications.count(),
    })


@login_required
def connect_credit_card(request):
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
    

    return render(request, 'dashboard/major/credit/connect_card.html', {'available_card_types': available_card_types, "available_card_count": len(available_card_types), "notifications": notifications, "notification_count": notifications.count(),})



