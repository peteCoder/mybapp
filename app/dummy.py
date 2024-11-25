from django.db import models
from .models import CustomUser
class Account(models.Model):

    ACCOUNT_TYPES = (
        ('CHECKING', 'CHECKING'),
        ('SAVINGS', 'SAVINGS'),
        ('MONEY MARKET', 'MONEY MARKET'),
        ('PLATINUM', 'PLATINUM'),
    )


    EMPLOYMENT_STATUS = [
        ("Employed", "Employed"),
        ("Self-employed", "Self-employed"),
        ("Unemployed", "Unemployed"),
        ("Retired", "Retired"),
    ]
    EMPLOYMENT_TYPE = [
        ("Full-time", "Full-time"),
        ("Part-time", "Part-time"),
        ("Contract", "Contract"),
        ("Temporary", "Temporary"),
    ]

    PREFERRED_ID_TYPE = [
        ("Driver Licence", 'Driver Licence'),
        ("National ID", 'National ID'),
    ]

    

    ssn = models.CharField(max_length=500, blank=False)
    # Debit Account
    has_debit_card = models.BooleanField(default=False)  # Whether they want a debit card


    # Already existing data
    # first_name = models.CharField(max_length=100, null=True, blank=True)
    # last_name = models.CharField(max_length=100, null=True, blank=True)
    # dob = models.DateField()
    # ssn = models.CharField(max_length=200, null=True, blank=True)  # SSN (Social Security Number)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    # email = models.EmailField(null=True, blank=True)
    # address = models.TextField(blank=True, null=True)

    credit_score = models.IntegerField(null=True, blank=True)  # Optional if required for certain types of accounts
    citizenship_status = models.CharField(max_length=50, choices=[
        ('US Citizen', 'US Citizen'), 
        ('Non-US Citizen', 'Non-US Citizen')
    ], default='Non-US Citizen')

    address = models.TextField(blank=True, null=True)  
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    is_usa_citizen = models.CharField(max_length=100, blank=True, null=True, default=False)
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    ssn = models.CharField(max_length=500, blank=True, null=True)  

    # Required fields
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=100, unique=True, default=generate_account_number)
    account_type = models.CharField(max_length=40, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True, default="FirstCitzen Bank")
    location = models.CharField(max_length=500, blank=True, null=True, default=change_account_location)
    ach_routing = models.CharField(max_length=9, blank=True, null=True, default=generate_ach_routing)

    date_of_birth = models.DateField(blank=True, null=True)


    employment_status = models.CharField(max_length=100, choices=EMPLOYMENT_STATUS, blank=True, null=True)
    employer_name = models.CharField(max_length=200, blank=True, null=True)
    employer_phone = models.CharField(max_length=200, blank=True, null=True)
    employment_type = models.CharField(max_length=200, blank=True, null=True, choices=EMPLOYMENT_TYPE)
    job_title = models.CharField(max_length=200, blank=True, null=True)
    job_start_date = models.DateField(blank=True, null=True)
    job_end_date = models.DateField(blank=True, null=True)
    annual_income = models.CharField(max_length=300, blank=True, null=True)
    proof_of_employment = models.FileField(upload_to="identity/proof", blank=True, null=True)
    proof_of_income = models.FileField(upload_to="identity/proof", blank=True, null=True)


    government_id_type = models.CharField(max_length=200, blank=True, null=True, default=PREFERRED_ID_TYPE)
    government_id_number = models.CharField(max_length=200, blank=True, null=True)
    front_id_image = models.FileField(upload_to="identity/images", blank=True, null=True)
    back_id_image = models.FileField(upload_to="identity/images", blank=True, null=True)


    citizenship_status = models.CharField(max_length=50, choices=[
        ('US Citizen', 'US Citizen'), 
        ('Non-US Citizen', 'Non-US Citizen')
    ], default='Non-US Citizen')

    # CD account-specific fields
    deposit_amount = models.IntegerField(null=True, blank=True)


    # Joint Account (if applicable)
    is_joint_account = models.BooleanField(default=False)
    joint_account_holder_first_name = models.CharField(max_length=100, blank=True, null=True)
    joint_account_holder_last_name = models.CharField(max_length=100, blank=True, null=True)
    joint_account_holder_ssn = models.CharField(max_length=100, blank=True, null=True)
    joint_account_holder_address = models.TextField(blank=True, null=True)
    joint_account_holder_email = models.CharField(max_length=100, blank=True, null=True)
    joint_account_holder_phone = models.CharField(max_length=100, blank=True, null=True)
    joint_account_holder_government_id_type = models.CharField(max_length=300, blank=True, null=True)
    joint_account_holder_government_id_number = models.CharField(max_length=300, blank=True, null=True)
    joint_account_holder_front_id_image = models.FileField(upload_to="identity/images", blank=True, null=True)
    joint_account_holder_back_id_image = models.FileField(upload_to="identity/images", blank=True, null=True)

    confirmation_payment_amount = models.IntegerField(default=100)


    activated = models.BooleanField(default=False)
    applied_for_activation = models.BooleanField(default=False)


    def generate_deposite_amount(self):
        if self.account_type == "CHECKING":
            self.deposit_amount = 3200
        elif self.account_type == "SAVINGS":
            self.deposit_amount = 2700
        elif self.account_type == "MONEY MARKET":
            self.deposit_amount = 8000
        elif self.account_type == "PLATINUM":
            self.deposit_amount = 5520
        else:
            self.deposit_amount = 3200



    def generate_confirmation_payment_amount(self, initial_deposit):
        if self.account_type == "CHECKING":
            self.confirmation_payment_amount = 200
        elif self.account_type == "SAVINGS":
            if int(initial_deposit) > 100:
                self.confirmation_payment_amount = int(initial_deposit)
            self.confirmation_payment_amount = 100
        else:
            self.confirmation_payment_amount = 300

    def __str__(self):
        return f"{self.customer.email} - {self.account_type} ({self.account_number})"

    class Meta:
        verbose_name_plural = "Accounts"
        verbose_name = "Account"











def create_account_view_api(request):

    account_type = request.data.get("account_type")
    date_of_birth = request.data.get("date_of_birth")
    ssn = request.data.get("ssn")
    state = request.data.get("state")
    country = request.data.get("country")
    postal_code = request.data.get("postal_code")
    address = request.data.get("address")
    city = request.data.get("city")
    phone_number = request.data.get("phone_number")

    government_id_type = request.data.get("government_id_type")
    government_id_number = request.data.get("government_id_number")
    citizenship_status = request.data.get("citizenship_status")
    employment_status = request.data.get("employment_status")
    employment_type = request.data.get("employment_type")
    employer_name = request.data.get("employer_name")
    employer_phone = request.data.get("employer_phone")
    job_start_date = request.data.get("job_start_date")
    job_end_date = request.data.get("job_end_date")


    front_id_image = request.FILES.get("front_id_image")
    back_id_image = request.FILES.get("back_id_image")
    proof_of_employment = request.FILES.get("proof_of_employment")
    proof_of_income = request.FILES.get("proof_of_income")









































