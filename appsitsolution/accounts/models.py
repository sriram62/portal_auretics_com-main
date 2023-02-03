from django.db.models.signals import post_save

from mlm_admin.models import *

# Create your models here.
# phone validater
phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                             message="Phone number must be entered in the format: '9999999999'. Up to 15 digits allowed.")

Status = (
    ("Active", "Active"),
    ("InActive", "InActive"),)

ID_PROOF_TYPE_CHOICES = (
    ('Voter_ID', 'Voter ID'),
    ('Driving_License', 'Driving License'),
    ('Passport', 'Passport'),
    ('PAN', 'PAN'),
    ('Aadhar', 'Aadhar'),
)

ADDRESS_PROOF_TYPE_CHOICES =(
    ('Voter_ID', 'Voter ID'),
    ('Driving_License', 'Driving License'),
    ('Passport', 'Passport'),
    ('Aadhar', 'Aadhar'),
    ('Ration_Card', 'Ration Card'),
    ('Telephone_Bill', 'Telephone Bill'),
    ('Electricity_Bill', 'Electricity  Bill'),
    ('Gas_Connection_Bill', 'Gas Connection Bill'),
    ('Bank_Statement', 'Bank Statement'),
    ('Bank_Passbook', 'Bank Passbook')
    )
Position = (
    ('LEFT','LEFT'),
    ('RIGHT','RIGHT')
)
Gender_choice = (
    ('Other','Other'),
    ('Male','Male'),
    ('Female','Female')
)

class ReferralCode(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    referal_id = models.CharField(max_length=255, default='')
    referral_code =models.CharField(max_length=255, default='', unique=True)
    status = models.BooleanField(default=False)
    # nipur code 10-2-2021 start ---------------------------------------------------------------------------------------------------->
    parent_id = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='parent',null=True,blank=True)
    referal_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='referal_by')
    position = models.CharField(max_length=20,choices=Position,default='LEFT')
    # nipur code 10-2-2021 end ---------------------------------------------------------------------------------------------------->
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


    @staticmethod
    def get_referal_code(referral_code):
        try:
            return ReferralCode.objects.get(referral_code=referral_code)
        except:
            return False

    def __str__(self):
        return self.referral_code

    class Meta:
        unique_together = ('parent_id', 'position')


#User Profile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='assets/profiles/images',
        default='avatar.jpg',
        blank=True
    )
    first_name = models.CharField(max_length=255, default='', )
    last_name = models.CharField(max_length=255, default='', blank=True, null=True)
    email = models.EmailField(default='none@email.com', unique=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, unique=True)
    date_of_birth = models.DateField(null=True, blank=True, default='1997-02-01')
    user_type = models.CharField(max_length=17, blank=True)
    status = models.CharField(max_length=17, blank=True, choices=Status, default='Active')
    shipping_address = models.ForeignKey(Address, related_name='profile_shipping_address', on_delete=models.SET_NULL,blank=True, null=True)
    country = models.CharField(max_length=255, default='', blank=True)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL)
    referral_id = models.CharField(max_length=255, default='', blank=True)
    reference_user_id = models.CharField(max_length=255, default='', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    co_applicant = models.CharField(max_length=255, default='', blank=True, null=True)
    blood_group = models.CharField(max_length=23, default="I don't know")
    blood_rh_factor = models.CharField(max_length=23, default="I don't know")
    normal = models.BooleanField(default=True, null=True, blank=True)
    distributor = models.BooleanField(default=False, null=True, blank=True)
    mlm_admin = models.BooleanField(default=False, null=True, blank=True)
    c_and_f_admin = models.BooleanField(default=False, null=True, blank=True)
    ever_c_and_f_admin = models.BooleanField(default=False, null=True, blank=True)
    super_admin = models.BooleanField(default=False, null=True, blank=True)
    ever_distributor = models.BooleanField(default=False)
    super_bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    gender = models.CharField(max_length=255, default='NOT Disclose', choices=Gender_choice)
    otp_count = models.IntegerField(default=0, null=True, blank=True)
    last_otp_time = models.DateTimeField(null=True, blank=True, default='1997-02-01')
    skip_kyc_date = models.DateTimeField(null=True, blank=True, default='1997-02-01')
    number_of_kyc_attempts = models.IntegerField(default=0, null=True, blank=True)
    preferred_time = models.TimeField(default=time(hour=9))
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
     
    def age(self):
        import datetime
        dob = self.date_of_birth
        tod = datetime.date.today()
        profile_age = (tod.year - dob.year) - int((tod.month, tod.day) < (dob.month, dob.day))
        return profile_age
    
    def get_full_name(self):
        return self.first_name+self.last_name

    def get_related_mc(self):
        qs = Material_center.objects.filter(company_depot="YES", status="Active", delete=False, associated_states=self.state)
        if qs.exists():
            return qs.first()
        return Material_center.objects.filter(frontend=True).first()

    def __str__(self):
        return "{}:{}".format(self.id, self.user)


class User_Check(models.Model):
    user_check = models.OneToOneField(User, on_delete=models.CASCADE)
    check_first_name = models.BooleanField(default=False)
    check_last_name = models.BooleanField(default=False)
    check_email = models.BooleanField(default=False)
    # check_phone_number = models.BooleanField(default=False)
    check_date_of_birth = models.BooleanField(default=False)
    check_house_number = models.BooleanField(default=False)
    check_address_line = models.BooleanField(default=False)
    check_Landmark = models.BooleanField(default=False)
    check_city = models.BooleanField(default=False)
    check_state = models.BooleanField(default=False)
    check_own_state = models.BooleanField(default=False)
    check_street = models.BooleanField(default=False)
    check_pin = models.BooleanField(default=False)
    check_mobile = models.BooleanField(default=False)
    check_alternate_mobile = models.BooleanField(default=False)
    check_pan_number = models.BooleanField(default=False)
    check_pan_file = models.BooleanField(default=False)
    check_id_proof_type = models.BooleanField(default=False)
    check_id_proof_file = models.BooleanField(default=False)
    check_address_proof_type = models.BooleanField(default=False)
    check_address_proof_file = models.BooleanField(default=False)
    check_distributors_name_in_bank_account = models.BooleanField(default=False)
    check_bank_name = models.BooleanField(default=False)
    check_account_number = models.BooleanField(default=False)
    check_ifsc_code = models.BooleanField(default=False)
    check_branch_name = models.BooleanField(default=False)
    check_cheque_photo = models.BooleanField(default=False)
    check_age_confirmation = models.BooleanField(default=False)
    check_co_applicant = models.BooleanField(default=False)
    check_blood_group = models.BooleanField(default=False)
    check_blood_rh_factor = models.BooleanField(default=False)
    check_profile_active = models.BooleanField(default=False)
    check_first_terms_conditions = models.BooleanField(default=False)
    check_second_terms_conditions = models.BooleanField(default=False)
    check_gender = models.BooleanField(default=False)
    check_registration_status = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.user_check.username
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     avatar = models.ImageField(
#         upload_to = 'assets/images',
#         default = 'avatar.jpg',
#         blank=True
#     )
#     first_name = models.CharField(max_length=255, default='')
#     last_name = models.CharField(max_length=255, default='')
#     email = models.EmailField(default='none@email.com')
#     phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
#     user_type = models.CharField( max_length=17, blank=True)
#     status  = models.CharField( max_length=17, blank=True)
#     shipping_address = models.ForeignKey(Address, related_name='profile_shipping_address',on_delete=models.SET_NULL, blank=True, null=True)
#     # address = models.TextField(default='')
#     # city = models.CharField(max_length=255, default='')
#     # state = models.CharField(max_length=255, choices = Status, default = 'A')
#     # country = models.CharField(max_length=255, default='')
#     referral_id = models.CharField(max_length=255, default='')
#     reference_user_id = models.CharField(max_length=255, default='')
#     created_on = models.DateTimeField(auto_now_add=True, null=True)
#
#
#     def __str__(self):
#         return self.user.username


def create_profile(sender, **kwargs):
    if kwargs['created']:
        profile = Profile.objects.create(user=kwargs['instance'], email=kwargs['instance'].email)

post_save.connect(create_profile, sender=User)



class Kyc(models.Model):
    nameFuzzyChoice = (
        ('TRUE','TRUE'),
        ('FALSE','FALSE')
        )
    kyc_user = models.OneToOneField(User, on_delete=models.CASCADE)
    pan_name = models.CharField(max_length=255, default='')
    pan_number= models.CharField(max_length=255, default='')
    pan_file = models.FileField(
        upload_to = 'pan_card/images',
        default = 'avatar.jpg',
        blank=True
    )
    id_proof_type = models.CharField(max_length=255, default='Voter_ID', choices=ID_PROOF_TYPE_CHOICES)
    id_proof_file = models.FileField(
        upload_to = 'id_proof/images',
        default = 'avatar.jpg',
        blank=True
    )
    address_proof_type = models.CharField(max_length=255, default='Voter_ID', choices=ADDRESS_PROOF_TYPE_CHOICES)
    address_proof_file = models.FileField(
        upload_to = 'address_proof/images',
        default = 'avatar.jpg',
        blank=True
    )
    nameFuzzy = models.CharField(max_length=255, default='', choices=nameFuzzyChoice)
    kyc_done = models.BooleanField(default=False)
    manual = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.kyc_user.username


@receiver(pre_save, sender=Kyc)
def save_type_to_kycDone_table(sender, instance, **kwargs):

    print(instance.manual)
    if instance.manual == True and instance.kyc_done == True:
        print("Manually")
        try:
            kyc_done = KycDone.objects.get(kyc_user=instance.kyc_user)
        except:
            kyc_done = KycDone.objects.create(kyc_user=instance.kyc_user)

        kyc_done.kyc_verification_type = "Manually"
        kyc_done.save()
    elif instance.manual == False and instance.kyc_done == True:
        print("signzy")
        try:
            kyc_done = KycDone.objects.get(kyc_user=instance.kyc_user)
        except:
            kyc_done = KycDone.objects.create(kyc_user=instance.kyc_user)

        kyc_done.kyc_verification_type = "Signzy"
        kyc_done.save()
    else:
        try:
            kyc_done = KycDone.objects.get(kyc_user=instance.kyc_user)
        except:
            kyc_done = KycDone.objects.create(kyc_user=instance.kyc_user)

        kyc_done.kyc_verification_type = "None"
        kyc_done.save()




class BankAccountDetails(models.Model):

    nameFuzzyChoice = (
    ('TRUE','TRUE'),
    ('FALSE','FALSE')
    )
    bank_account_user = models.OneToOneField(User, on_delete=models.CASCADE)
    distributors_name_in_bank_account= models.CharField(max_length=255, default='',null=True,blank=True)
    bank_name =models.CharField(max_length=255, default='',null=True,blank=True)
    account_number =models.CharField(max_length=255, default='',null=True,blank=True)
    ifsc_code = models.CharField(max_length=255, default='',null=True,blank=True)
    patron_id = models.CharField(max_length=255, default='',null=True,blank=True)
    nameFuzzy = models.CharField(max_length=255,choices =nameFuzzyChoice,default='',null=True,blank=True)
    branch_name = models.CharField(max_length=255, default='',null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    cheque_photo = models.FileField(
        upload_to = 'bank_cheque/images',
        default = 'avatar.jpg',
        blank=True
    )
    age_confirmation = models.BooleanField(default=False)
    self_declaration = models.BooleanField(default=False)

    def __str__(self):
        return self.bank_account_user.username

class Customer(models.Model):
    firstname = models.CharField(max_length=200, null=True)
    lastname = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.EmailField()
    password = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def register(self):
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email= email)
        except:
            return False

    def __str__(self):
        return self.firstname
class menu_permission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    category_management = models.CharField(max_length=200,null=True,blank=True)
    product_management = models.CharField(max_length=200,null=True,blank=True)
    order_management = models.CharField(max_length=200,null=True,blank=True)
    batch_management = models.CharField(max_length=200,null=True,blank=True)
    mc_management = models.CharField(max_length=200,null=True,blank=True)
    user_management = models.CharField(max_length=200,null=True,blank=True)
    purchase_management = models.CharField(max_length=200,null=True,blank=True)
    crm_management = models.CharField(max_length=200,null=True,blank=True)
    sale_management = models.CharField(max_length=200,null=True,blank=True)
    inventory_management = models.CharField(max_length=200,null=True,blank=True)
    cron_management = models.CharField(max_length=200,null=True,blank=True)
    manual_configure = models.CharField(max_length=200,null=True,blank=True)
    menu_permission = models.BooleanField(default=True)
    manual_verification = models.CharField(max_length=200,null=True,blank=True)
    wallet_configuration = models.CharField(max_length=200,null=True,blank=True)
    mis_report = models.CharField(max_length=200, null=True, blank=True)
    pincode = models.CharField(max_length=200, null=True, blank=True)
    calculations = models.CharField(max_length=200,null=True,blank=True)
    realtime = models.CharField(max_length=200,null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.user.email



 


# # @receiver(pre_save, sender=User)
# @receiver(post_save, sender=User)
# def user_created(sender, instance, **kwargs):
#     if instance._state.adding:
#         print("created")
#         try:
#             kyc_done = KycDone.objects.get(kyc_user=instance)
#         except:
#             kyc_done = KycDone.objects.create(kyc_user=instance)
#         # kyc_done = KycDone.objects.update_or_create(kyc_user=instance, defaults={'kyc_user':instance})
#         print("kyc_done is created")
#         kyc_done.kyc_verification_type = "None"
#         kyc_done.save()


# @receiver(pre_save, sender=User)
@receiver(post_save, sender=User)
def user_created(sender, instance, **kwargs):
    if instance._state.adding:
        # print("created")
        # kyc_done = KycDone.objects.create(kyc_user=instance)
        # print("kyc_done is created")
        # kyc_done.kyc_verification_type = "None"
        # kyc_done.save()
        pass
