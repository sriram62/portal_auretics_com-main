from django.db import models
from accounts.models import *
from shop.models import *
from datetime import datetime

from django.utils.timezone import now
# Create your models here.
circle = (
    ("Lead Circle", "Lead Circle"),
    ("Influence Circle", "Influence Circle"),
    ("None", "None"),
)
choice = (
    ("YES", "Yes"),
    ("NO", "No"), )
infinity_choice = (
    ("YES", "Yes"),
    ("NO", "No"), )
differential_bonus = (
    ("YES", "Yes"),
    ("NO", "No"), )
stage = (
    ("Public", "Public"),
    ("Draft", "Draft"), )
circle_concider = (
    ("Influence", "Influence"),
    ("Lead", "Lead"), )
qualification = (
    ('Black Diamond Director', 'Black Diamond Director'),
    ('Diamond Director', 'Diamond Director'),
    ('Emerald Director', 'Emerald Director'),
    ('Crown Director', 'Crown Director'),
    ('Jade Director', 'Jade Director'),
    ('Sapphire Director', 'Sapphire Director'),
    ('Titanium Director', 'Titanium Director'),
    ('Platinum Director', 'Platinum Director'),
    ('Gold Director', 'Gold Director'),
    ('Silver Director', 'Silver Director'),
    ('Bronze Director', 'Bronze Director'),
    ('Associate Director', 'Associate Director'),
    ('Non Qualified Director', 'Non Qualified Director'),
    ('Manager', 'Manager'),
    ('Associate Manager', 'Associate Manager'),
    ('Advisor', 'Advisor'),
    ('Associate Advisor', 'Associate Advisor'),
    ('Blue Advisor', 'Blue Advisor'),
)


class weekly_distributor(models.Model):
    distributor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    distributor_reff = models.ForeignKey(
        ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)
    pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    dp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class monthly_distributor(models.Model):
    distributor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    distributor_reff = models.ForeignKey(
        ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)
    pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    dp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class weekly_material(models.Model):
    distributor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    distributor_reff = models.ForeignKey(
        ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)
    pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    dp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class monthly_material(models.Model):
    distributor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    distributor_reff = models.ForeignKey(
        ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)
    pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    dp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class configurations(models.Model):
    minimum_monthly_purchase_to_become_active = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_advisor_accumulated_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_advisor_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    advisor_accumulated_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    advisor_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_manager_accumulated_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_manager_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    manager_accumulated_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    manager_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_director_accumulated_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_director_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bronze_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bronze_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bronze_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    silver_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    silver_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    silver_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    gold_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    gold_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    gold_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    platinum_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    platinum_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    platinum_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    titanium_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    titanium_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    titanium_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sapphire_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sapphire_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sapphire_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    emerald_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    emerald_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    emerald_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    jade_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    jade_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    jade_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    crown_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    crown_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    crown_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    diamond_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    diamond_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    diamond_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    black_diamond_director_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    black_diamond_director_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    black_diamond_director_legs = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    perform_roll_up = models.CharField(choices=choice, max_length=20)
    perform_dynamic_compression_actives = models.CharField(
        choices=choice, max_length=20)
    perform_dynamic_compression_directors = models.CharField(
        choices=choice, max_length=20)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class company_calculation_model(models.Model):
    date_model = models.DateField(default=now)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    company_gpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    company_gbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    company_accumulated_gpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    company_accumulated_gbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    super_plan_gpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    super_plan_accumulated_gpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    super_plan_gbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    super_plan_accumulated_gbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    infinity_plan_gpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    infinity_plan_accumulated_gpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    infinity_plan_gbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    infinity_plan_accumulated_gbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class title_qualification_calculation_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    date_model = models.DateField(default=now)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    pgpv_pgbv_calculation_done = models.BooleanField(default=False)
    no_of_director_legs = models.IntegerField(default=0)
    is_there_a_qualified_director_in_the_group = models.BooleanField(
        default=False)
    pgpv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accumulated_pgpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    ppv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accumulated_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    pgbv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accumulated_pgbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    pbv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accumulated_pbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    gpv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accumulated_gpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    gbv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accumulated_gbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    tbv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accumulated_tbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    tpv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accumulated_tpv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    is_user_green = models.BooleanField(default=False)
    current_month_qualification = models.CharField(
        choices=qualification, max_length=200, default='Blue Advisor')
    highest_qualification_ever = models.CharField(
        choices=qualification, max_length=200, default='Blue Advisor')
    super_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    super_pbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    infinity_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    infinity_pbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    calculation = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class commission_calculation_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(
        choices=stage, max_length=3000, null=True, blank=True, default="")
    mobile_number = models.CharField(
        choices=stage, max_length=3000, null=True, blank=True, default="")
    ARN = models.CharField(choices=stage, max_length=3000,
                           null=True, blank=True, default="")
    date_model = models.DateField(default=now)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    current_month_qualification = models.CharField(
        choices=qualification, max_length=200, default='Blue Advisor')
    direct_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    direct_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    team_building_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    team_building_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    leadership_building_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    leadership_building_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    lifestyle_fund_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    lifestyle_fund_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    retail_margin_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    retail_margin_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    personal_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    personal_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    fortune_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    fortune_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sharing_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sharing_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    nurturing_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    nurturing_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    business_master_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    business_master_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    vacation_fund_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    vacation_fund_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    automobile_fund_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    automobile_fund_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    shelter_fund_bonus_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    shelter_fund_bonus_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    consistent_retailers_income_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    consistent_retailers_income_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    elite_incentive_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    elite_incentive_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    meeting_expense_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    meeting_expense_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    admin_charge_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    admin_charge_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    advertisement_current_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    advertisement_till_date = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class commission_wallet_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(
        choices=stage, max_length=3000, null=True, blank=True, default="")
    mobile_number = models.CharField(
        choices=stage, max_length=3000, null=True, blank=True, default="")
    ARN = models.CharField(choices=stage, max_length=3000,
                           null=True, blank=True, default="")
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    kyc_done = models.BooleanField(default=False)
    transaction_type = models.CharField(max_length=1000, null=True, blank=True)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    account_hit = models.CharField(max_length=200, null=True, blank=True)
    heading = models.CharField(max_length=200, null=True, blank=True)
    narration = models.CharField(max_length=200, null=True, blank=True)
    amount_in = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    amount_out = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    tds = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    balance = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    audit_balance = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    tds_job_done = models.BooleanField(default=False)


class commission_wallet_amount_out_detail_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(
        choices=stage, max_length=3000, null=True, blank=True, default="")
    mobile_number = models.CharField(
        choices=stage, max_length=3000, null=True, blank=True, default="")
    ARN = models.CharField(choices=stage, max_length=3000,
                           null=True, blank=True, default="")
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    kyc_done = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    transaction_type = models.CharField(max_length=1000, null=True, blank=True)
    beneficiary_code = models.CharField(max_length=200, blank=True, null=True)
    beneficiary_account_number = models.CharField(
        max_length=200, blank=True, null=True)
    ifsc = models.CharField(max_length=200, blank=True, null=True)
    instrument_amount_without_comma_style = models.CharField(
        max_length=200, blank=True, null=True)
    beneficiary_name = models.CharField(max_length=200, blank=True, null=True)
    drawee_location = models.CharField(max_length=200, blank=True, null=True)
    print_location = models.CharField(max_length=200, blank=True, null=True)
    bene_address_1 = models.CharField(max_length=200, blank=True, null=True)
    bene_address_2 = models.CharField(max_length=200, blank=True, null=True)
    bene_address_3 = models.CharField(max_length=200, blank=True, null=True)
    bene_address_4 = models.CharField(max_length=200, blank=True, null=True)
    bene_address_5 = models.CharField(max_length=200, blank=True, null=True)
    instruction_reference_number = models.CharField(
        max_length=200, blank=True, null=True)
    customer_reference_number = models.CharField(
        max_length=200, blank=True, null=True)
    payment_details_1 = models.CharField(max_length=200, blank=True, null=True)
    payment_details_2 = models.CharField(max_length=200, blank=True, null=True)
    payment_details_3 = models.CharField(max_length=200, blank=True, null=True)
    payment_details_4 = models.CharField(max_length=200, blank=True, null=True)
    payment_details_5 = models.CharField(max_length=200, blank=True, null=True)
    payment_details_6 = models.CharField(max_length=200, blank=True, null=True)
    payment_details_7 = models.CharField(max_length=200, blank=True, null=True)
    cheque_number = models.CharField(max_length=200, blank=True, null=True)
    chq_trn_date = models.DateField(auto_now_add=True)
    micr_number = models.CharField(max_length=200, blank=True, null=True)
    ifsc_code = models.CharField(max_length=200, blank=True, null=True)
    bene_bank_name = models.CharField(max_length=200, blank=True, null=True)
    bene_bank_branch_name = models.CharField(
        max_length=200, blank=True, null=True)
    beneficiary_email_id = models.CharField(
        max_length=200, blank=True, null=True)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class super_plan_model(models.Model):
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    week = models.CharField(max_length=200, null=True, blank=True)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    company_super_bv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_direct_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_direct_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_direct_bonus_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sum_of_all_team_building_bonus_points = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    team_building_bonus_index = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_team_building_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_team_building_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_team_building_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_leadership_building_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_leadership_building_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_leadership_building_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_lifestyle_fund_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_lifestyle_fund_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_lifestyle_fund_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class direct_bonus_super_plan_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    week = models.CharField(max_length=200, null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    no_of_user_referred = models.IntegerField(default=0)
    no_of_new_user_referred = models.IntegerField(default=0)
    direct_bonus_for_any_sponsor_exceeded_capping = models.BooleanField(
        default=False)
    direct_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    direct_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    direct_bonus_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    direct_bonus_user_wise_details = models.TextField(
        default='{}', null=True, blank=True)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class team_building_bonus_super_plan_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    week = models.CharField(max_length=200, null=True, blank=True)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    cm_left_pv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    cm_right_pv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    cm_left_bv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    cm_right_bv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    cm_no_of_new_advisor_in_left_position_referred = models.IntegerField(
        default=0)
    cm_no_of_new_advisor_in_right_position_referred = models.IntegerField(
        default=0)
    bf_no_of_new_advisor_pv_in_left_position_referred = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='bf_new_left_pv_referred')
    bf_no_of_new_advisor_pv_in_right_position_referred = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='bf_new_right_pv_referred')
    cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='cm_new_left_pv_ref_cf')
    cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='cm_new_right_pv_ref_cf')
    total_no_of_new_advisor_in_left_position = models.IntegerField(default=0)
    total_no_of_new_advisor_in_right_position = models.IntegerField(default=0)
    total_no_of_new_advisor_pv_in_left_position = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_no_of_new_advisor_pv_in_right_position = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    max_no_of_new_advisor_to_be_considered_in_left_position = models.IntegerField(
        default=0)
    max_no_of_new_advisor_to_be_considered_in_right_position = models.IntegerField(
        default=0)
    team_building_bonus_points = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    team_building_bonus_capping = models.BooleanField(default=False)
    team_building_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    team_building_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    team_building_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=200, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class leadership_building_bonus_super_plan_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    week = models.CharField(max_length=200, null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    all_first_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_all_first_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    all_second_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_all_second_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    all_third_immediate_active_advisor_username = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    all_third_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_all_third_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    all_fourth_immediate_active_advisor_username = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    all_fourth_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_all_fourth_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    all_fifth_immediate_active_advisor_username = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    all_fifth_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_all_fifth_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    leadership_building_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    leadership_building_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    leadership_building_bonus_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class leadership_building_bonus_tree_super_plan_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    week = models.CharField(max_length=200, null=True, blank=True)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    first_immediate_active_advisor_username = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_first_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    second_immediate_active_advisor_username = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    second_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_second_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    third_immediate_active_advisor_username = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    third_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_third_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    fourth_immediate_active_advisor_username = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    fourth_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_fourth_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    fifth_immediate_active_advisor_username = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    fifth_immediate_active_advisor_Tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bonus_from_fifth_immediate_active_advisor = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    first_immediate_active_advisor_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class life_style_fund_super_plan_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    week = models.CharField(max_length=200, null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    leadership_building_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    life_style_fund_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    life_style_fund_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    life_style_fund_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    life_style_fund_opening = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    life_style_fund_closing = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class infinity_plan_model(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    input_date = models.DateField(null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    infinity_bv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_retail_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_personal_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_personal_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_personal_bonus_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    fb_no_number_of_users = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    fb_total_number_of_users_selected = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_fortune_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_fortune_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_fortune_bonus_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sb_percent_for_pool = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sb_sum_of_all_sharing_bonus_points = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sb_sharing_bonus_index_calculated = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sb_sharing_bonus_index_given_by_admin = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_sharing_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_sharing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_sharing_bonus_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_nurturing_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_nurturing_bonus_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bmb_percent_for_pool = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bmb_sum_of_all_sharing_bonus_points = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bmb_sharing_bonus_index_calculated = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    bmb_sharing_bonus_index_given_by_admin = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_business_master_bonus_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_business_master_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_business_master_bonus_balance_payable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_consistent_retailer_income_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_consistent_retailer_income_consumable = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_consistent_retailer_income_consumed = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    total_consistent_retailer_income_lapsed = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class retail_margin(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    week = models.CharField(max_length=200, null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    retail_margin = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class personal_bonus(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    advisor_level = models.CharField(max_length=200, null=True, blank=True)
    previous_accumulated_pgbv = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    current_month_pgbv = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    personal_bonus_level = models.CharField(
        choices=qualification, max_length=200, default='Blue Advisor')
    my_personal_bonus = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    personal_bonus_from_my_personal_group = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    personal_bonus_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    personal_bonus_paid = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    personal_bonus_balance_payable = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    audit_personal_bonus_self_perc = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00, null=True, blank=True)
    audit_down_personal_bonus_diff = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00, null=True, blank=True)
    audit_down_personal_bonus_diff_list = models.TextField(
        default='', null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class fortune_bonus(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    wheather_Selected = models.BooleanField(default=False)
    personal_bonus = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    fortune_bonus_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    fortune_bonus_paid = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    fortune_bonus_balance_payable = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class sharing_bonus(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    is_user_qualified_director = models.BooleanField(default=False)
    pgbv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00)
    sharing_bonus_point = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    sharing_bonus_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    sharing_bonus_paid = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    sharing_bonus_balance_payable = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    draft_date = models.DateField(default=now)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class nuturing_bonus(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    is_user_qualified_director = models.BooleanField(default=False)
    qualified_director_level = models.CharField(
        choices=qualification, max_length=200, default='Blue Advisor')
    circle_to_consider = models.CharField(
        choices=circle_concider, max_length=50)
    percentage = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    nurturing_bonus_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    nurturing_bonus_paid = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    nurturing_bonus_balance_payable = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_1st_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_2nd_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_3rd_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_4th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_5th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_6th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_7th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_8th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_9th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_personal_bonus_of_10th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class nuturing_bonus_tree(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    username_of_1st_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_1st_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_2nd_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_2nd_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_3rd_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_3rd_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_4th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_4th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_5th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_5th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_6th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_6th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_7th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_7th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_8th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_8th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_9th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_9th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    username_of_10th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    personal_bonus_of_10th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class business_master_bonus(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    is_user_qualified_director = models.BooleanField(default=False)
    qualified_director_level = models.CharField(
        max_length=200, choices=qualification, default='Blue Advisor')
    circle_to_consider = models.CharField(
        max_length=200, choices=circle_concider)
    percentage = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    business_master_bonus_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    business_master_bonus_paid = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    business_master_bonus_balance_payable = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_1st_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_2nd_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_3rd_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_4th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_5th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_6th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_7th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_8th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_9th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points_from_10th_generation_down = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    total_bmb_points = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class business_master_bonus_tree(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    username_of_qualified_diretor_at_1st_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_1st_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_1st')
    username_of_qualified_diretor_at_2nd_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_2nd_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_2nd')
    username_of_qualified_diretor_at_3rd_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_3rd_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_3rd')
    username_of_qualified_diretor_at_4th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_4th_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_4th')
    username_of_qualified_diretor_at_5th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_5th_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_5th')
    username_of_qualified_diretor_at_6th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_6th_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_6th')
    username_of_qualified_diretor_at_7th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_7th_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_7th')
    username_of_qualified_diretor_at_8th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_8th_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_8th')
    username_of_qualified_diretor_at_9th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_9th_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_9th')
    username_of_qualified_diretor_at_10th_generation_down = models.CharField(
        max_length=200, null=True, blank=True)
    points_to_be_given_for_qualified_diretor_at_10th_generation_down = models.CharField(
        max_length=200, null=True, blank=True, db_column='points_dq_10th')
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class vacation_fund(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    is_user_qualified_director = models.BooleanField(default=True)
    qualified_director_level = models.CharField(
        max_length=200, choices=qualification, default='Blue Advisor')
    is_user_qualified_vacation_fund = models.BooleanField(default=False)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    closing_vacation_fund = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    sum_of_all_bonus_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    vacation_fund_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    vacation_fund_earned_heading = models.CharField(
        max_length=200, null=True, blank=True)
    vacation_fund_earned_remarks = models.CharField(
        max_length=200, null=True, blank=True)
    opening_vacation_fund = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    vacation_fund_used = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    vacation_fund_used_heading = models.CharField(
        max_length=200, null=True, blank=True)
    vacation_fund_used_remarks = models.CharField(
        max_length=200, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class automobile_fund(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    is_user_qualified_director = models.BooleanField(default=False)
    qualified_director_level = models.CharField(
        max_length=200, choices=qualification, default='Blue Advisor')
    is_user_qualified_automobile_fund = models.BooleanField(default=False)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    closing_automobile_fund = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    sum_of_all_bonus_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    automobile_fund_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    automobile_fund_earned_heading = models.CharField(
        max_length=200, null=True, blank=True)
    automobile_fund_earned_remarks = models.CharField(
        max_length=200, null=True, blank=True)
    opening_automobile_fund = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    automobile_fund_used = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    automobile_fund_used_heading = models.CharField(
        max_length=200, null=True, blank=True)
    automobile_fund_used_remarks = models.CharField(
        max_length=200, null=True, blank=True)
    closing_automobile_fund_used = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class shelter_fund(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    is_user_qualified_director = models.BooleanField(default=False)
    qualified_director_level = models.CharField(
        max_length=200, choices=qualification, default='Blue Advisor')
    is_user_qualified_shelter_fund = models.BooleanField(default=False)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    closing_shelter_fund = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    sum_of_all_bonus_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    shelter_fund_earned = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    shelter_fund_earned_heading = models.CharField(
        max_length=200, null=True, blank=True)
    shelter_fund_earned_remarks = models.CharField(
        max_length=200, null=True, blank=True)
    opening_shelter_fund = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    shelter_fund_used = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    shelter_fund_used_heading = models.CharField(
        max_length=200, null=True, blank=True)
    shelter_fund_used_remarks = models.CharField(
        max_length=200, null=True, blank=True)
    closing_shelter_fund_used = models.DecimalField(
        max_digits=200, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class consistent_retailers_income(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    is_user_qualified_consistent_retailers_income = models.BooleanField(
        default=False)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    last_month_pbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    this_month_pbv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    cri_consumed = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    cri_earned = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    order_no_in_which_pbv_was_consumed = models.CharField(
        max_length=200, null=True, blank=True)
    cri_balance = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class super_model(models.Model):
    purchase_pv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    direct_bonus_bv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    direct_bonus_capping = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    team_building_bonus_capping = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    team_building_bonus_minimum_ppv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    level_1st_downline = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    level_2nd_downline = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    level_3rd_downline = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    level_4th_downline = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    level_5th_downline = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    life_style_fund_tbb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    created_on = models.DateField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class infinity_model(models.Model):
    show_to_advisor = models.CharField(choices=infinity_choice, max_length=30)
    associate_advisor_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    advisor_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_manager_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    manager_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    associate_director_above_percent = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    calculate_differential_bonus = models.CharField(
        choices=differential_bonus, max_length=30)
    advisor_pv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    director_pv = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    how_many_advisor_select = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    how_much_pv_give = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    how_many_point_per_self_pgbv_allocate = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    sb_bonus_pool = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    black_diamond_direct_circle = models.CharField(
        choices=circle, max_length=30)
    black_diamond_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='bd_perc_pb_downline_nb_paid')
    diamond_direct_circle = models.CharField(choices=circle, max_length=30)
    diamond_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='d_perc_pb_downline_nb_paid')
    crown_direct_circle = models.CharField(choices=circle, max_length=30)
    crown_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='c_perc_pb_downline_nb_paid')
    jade_direct_circle = models.CharField(choices=circle, max_length=30)
    jade_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='j_perc_pb_downline_nb_paid')
    emerald_direct_circle = models.CharField(choices=circle, max_length=30)
    emerald_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='e_perc_pb_downline_nb_paid')
    sapphire_direct_circle = models.CharField(choices=circle, max_length=30)
    sapphire_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='sap_perc_pb_downline_nb_paid')
    titanium_direct_circle = models.CharField(choices=circle, max_length=30)
    titanium_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='t_perc_pb_downline_nb_paid')
    platinum_direct_circle = models.CharField(choices=circle, max_length=30)
    platinum_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='p_perc_pb_downline_nb_paid')
    gold_direct_circle = models.CharField(choices=circle, max_length=30)
    gold_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='g_perc_pb_downline_nb_paid')
    silver_direct_circle = models.CharField(choices=circle, max_length=30)
    silver_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='sil_perc_pb_downline_nb_paid')
    bronze_direct_circle = models.CharField(choices=circle, max_length=30)
    bronze_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='b_perc_pb_downline_nb_paid')
    associate_direct_circle = models.CharField(choices=circle, max_length=30)
    associate_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00, db_column='a_perc_pb_downline_nb_paid')
    black_diamond_direct_self = models.IntegerField(default=0)
    black_diamond_direct_1 = models.IntegerField(default=0)
    black_diamond_direct_2 = models.IntegerField(default=0)
    black_diamond_direct_3 = models.IntegerField(default=0)
    black_diamond_direct_4 = models.IntegerField(default=0)
    black_diamond_direct_5 = models.IntegerField(default=0)
    black_diamond_direct_6 = models.IntegerField(default=0)
    black_diamond_direct_7 = models.IntegerField(default=0)
    black_diamond_direct_8 = models.IntegerField(default=0)
    black_diamond_direct_9 = models.IntegerField(default=0)
    black_diamond_direct_10 = models.IntegerField(default=0)
    diamond_direct_self = models.IntegerField(default=0)
    diamond_direct_1 = models.IntegerField(default=0)
    diamond_direct_2 = models.IntegerField(default=0)
    diamond_direct_3 = models.IntegerField(default=0)
    diamond_direct_4 = models.IntegerField(default=0)
    diamond_direct_5 = models.IntegerField(default=0)
    diamond_direct_6 = models.IntegerField(default=0)
    diamond_direct_7 = models.IntegerField(default=0)
    diamond_direct_8 = models.IntegerField(default=0)
    diamond_direct_9 = models.IntegerField(default=0)
    diamond_direct_10 = models.IntegerField(default=0)
    crown_direct_self = models.IntegerField(default=0)
    crown_direct_1 = models.IntegerField(default=0)
    crown_direct_2 = models.IntegerField(default=0)
    crown_direct_3 = models.IntegerField(default=0)
    crown_direct_4 = models.IntegerField(default=0)
    crown_direct_5 = models.IntegerField(default=0)
    crown_direct_6 = models.IntegerField(default=0)
    crown_direct_7 = models.IntegerField(default=0)
    crown_direct_8 = models.IntegerField(default=0)
    crown_direct_9 = models.IntegerField(default=0)
    crown_direct_10 = models.IntegerField(default=0)
    jade_direct_self = models.IntegerField(default=0)
    jade_direct_1 = models.IntegerField(default=0)
    jade_direct_2 = models.IntegerField(default=0)
    jade_direct_3 = models.IntegerField(default=0)
    jade_direct_4 = models.IntegerField(default=0)
    jade_direct_5 = models.IntegerField(default=0)
    jade_direct_6 = models.IntegerField(default=0)
    jade_direct_7 = models.IntegerField(default=0)
    jade_direct_8 = models.IntegerField(default=0)
    jade_direct_9 = models.IntegerField(default=0)
    jade_direct_10 = models.IntegerField(default=0)
    emerald_direct_self = models.IntegerField(default=0)
    emerald_direct_1 = models.IntegerField(default=0)
    emerald_direct_2 = models.IntegerField(default=0)
    emerald_direct_3 = models.IntegerField(default=0)
    emerald_direct_4 = models.IntegerField(default=0)
    emerald_direct_5 = models.IntegerField(default=0)
    emerald_direct_6 = models.IntegerField(default=0)
    emerald_direct_7 = models.IntegerField(default=0)
    emerald_direct_8 = models.IntegerField(default=0)
    emerald_direct_9 = models.IntegerField(default=0)
    emerald_direct_10 = models.IntegerField(default=0)
    sapphire_direct_self = models.IntegerField(default=0)
    sapphire_direct_1 = models.IntegerField(default=0)
    sapphire_direct_2 = models.IntegerField(default=0)
    sapphire_direct_3 = models.IntegerField(default=0)
    sapphire_direct_4 = models.IntegerField(default=0)
    sapphire_direct_5 = models.IntegerField(default=0)
    sapphire_direct_6 = models.IntegerField(default=0)
    sapphire_direct_7 = models.IntegerField(default=0)
    sapphire_direct_8 = models.IntegerField(default=0)
    sapphire_direct_9 = models.IntegerField(default=0)
    sapphire_direct_10 = models.IntegerField(default=0)
    titanium_direct_self = models.IntegerField(default=0)
    titanium_direct_1 = models.IntegerField(default=0)
    titanium_direct_2 = models.IntegerField(default=0)
    titanium_direct_3 = models.IntegerField(default=0)
    titanium_direct_4 = models.IntegerField(default=0)
    titanium_direct_5 = models.IntegerField(default=0)
    titanium_direct_6 = models.IntegerField(default=0)
    titanium_direct_7 = models.IntegerField(default=0)
    titanium_direct_8 = models.IntegerField(default=0)
    titanium_direct_9 = models.IntegerField(default=0)
    titanium_direct_10 = models.IntegerField(default=0)
    platinum_direct_self = models.IntegerField(default=0)
    platinum_direct_1 = models.IntegerField(default=0)
    platinum_direct_2 = models.IntegerField(default=0)
    platinum_direct_3 = models.IntegerField(default=0)
    platinum_direct_4 = models.IntegerField(default=0)
    platinum_direct_5 = models.IntegerField(default=0)
    platinum_direct_6 = models.IntegerField(default=0)
    platinum_direct_7 = models.IntegerField(default=0)
    platinum_direct_8 = models.IntegerField(default=0)
    platinum_direct_9 = models.IntegerField(default=0)
    platinum_direct_10 = models.IntegerField(default=0)
    gold_direct_self = models.IntegerField(default=0)
    gold_direct_1 = models.IntegerField(default=0)
    gold_direct_2 = models.IntegerField(default=0)
    gold_direct_3 = models.IntegerField(default=0)
    gold_direct_4 = models.IntegerField(default=0)
    gold_direct_5 = models.IntegerField(default=0)
    gold_direct_6 = models.IntegerField(default=0)
    gold_direct_7 = models.IntegerField(default=0)
    gold_direct_8 = models.IntegerField(default=0)
    gold_direct_9 = models.IntegerField(default=0)
    gold_direct_10 = models.IntegerField(default=0)
    silver_direct_self = models.IntegerField(default=0)
    silver_direct_1 = models.IntegerField(default=0)
    silver_direct_2 = models.IntegerField(default=0)
    silver_direct_3 = models.IntegerField(default=0)
    silver_direct_4 = models.IntegerField(default=0)
    silver_direct_5 = models.IntegerField(default=0)
    silver_direct_6 = models.IntegerField(default=0)
    silver_direct_7 = models.IntegerField(default=0)
    silver_direct_8 = models.IntegerField(default=0)
    silver_direct_9 = models.IntegerField(default=0)
    silver_direct_10 = models.IntegerField(default=0)
    bronze_direct_self = models.IntegerField(default=0)
    bronze_direct_1 = models.IntegerField(default=0)
    bronze_direct_2 = models.IntegerField(default=0)
    bronze_direct_3 = models.IntegerField(default=0)
    bronze_direct_4 = models.IntegerField(default=0)
    bronze_direct_5 = models.IntegerField(default=0)
    bronze_direct_6 = models.IntegerField(default=0)
    bronze_direct_7 = models.IntegerField(default=0)
    bronze_direct_8 = models.IntegerField(default=0)
    bronze_direct_9 = models.IntegerField(default=0)
    bronze_direct_10 = models.IntegerField(default=0)
    associate_direct_self = models.IntegerField(default=0)
    associate_direct_1 = models.IntegerField(default=0)
    associate_direct_2 = models.IntegerField(default=0)
    associate_direct_3 = models.IntegerField(default=0)
    associate_direct_4 = models.IntegerField(default=0)
    associate_direct_5 = models.IntegerField(default=0)
    associate_direct_6 = models.IntegerField(default=0)
    associate_direct_7 = models.IntegerField(default=0)
    associate_direct_8 = models.IntegerField(default=0)
    associate_direct_9 = models.IntegerField(default=0)
    associate_direct_10 = models.IntegerField(default=0)
    vacation_fund_qualified_direct_level = models.CharField(
        choices=qualification, max_length=100, default='Blue Advisor')
    vacation_fund_percentage_pb_sb_nb_bmb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    vehicle_fund_qualified_direct_level = models.CharField(
        choices=qualification, max_length=100, default='Blue Advisor')
    vehicle_fund_percentage_pb_sb_nb_bmb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    shelter_fund_qualified_direct_level = models.CharField(
        choices=qualification, max_length=100, default='Blue Advisor')
    shelter_fund_percentage_pb_sb_nb_bmb = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    consistent_retailers_enabled_income = models.CharField(
        choices=choice, max_length=30)
    minimum_purchase_in_earning_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    minimum_purchase_in_redeeming_month = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    cap_on_maximum_purchase = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    percentage_loyalty_given = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    @classmethod
    def get_obj(cls):
        return cls.objects.all().first()

class dynamic_compression_director(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(choices=stage, max_length=30)
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    is_user_director = models.BooleanField(default=False)
    referral = models.ForeignKey(
        User, related_name='comp_director_user', on_delete=models.SET_NULL, null=True, blank=True)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class dynamic_compression_active(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    referral = models.ForeignKey(
        User, related_name='comp_active_user', on_delete=models.SET_NULL, null=True, blank=True)
    referral_code = models.CharField(max_length=255, default='')
    # ppv = models.DecimalField(
    #     max_digits=20, decimal_places=2, default=0.00)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class dynamic_compression_tbb(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    input_date = models.DateField(null=True, blank=True)
    calculation_stage = models.CharField(
        choices=stage, max_length=30, default='Draft')
    user_enabled = models.BooleanField(default=False)
    user_active = models.BooleanField(default=False)
    referral = models.ForeignKey(
        User, related_name='comp_tbb_user', on_delete=models.SET_NULL, null=True, blank=True)
    referral_code = models.CharField(max_length=255, default='')
    # users_in_depth_level_1 = models.TextField(null=True, blank=True)
    # users_in_depth_level_2 = models.TextField(null=True, blank=True)
    # users_in_depth_level_3 = models.TextField(null=True, blank=True)
    # users_in_depth_level_4 = models.TextField(null=True, blank=True)
    # users_in_depth_level_5 = models.TextField(null=True, blank=True)
    # no_of_users_in_depth_level_1 = models.IntegerField(default=0)
    # no_of_users_in_depth_level_2 = models.IntegerField(default=0)
    # no_of_users_in_depth_level_3 = models.IntegerField(default=0)
    # no_of_users_in_depth_level_4 = models.IntegerField(default=0)
    # no_of_users_in_depth_level_5 = models.IntegerField(default=0)
    # tbb_user_above_1_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_2_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_3_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_4_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_5_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_6_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_7_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_8_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_9_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # tbb_user_above_10_level = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    draft_date = models.DateField(null=True, blank=True)
    public_date = models.DateField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class inner_configurations(models.Model):
    tds_percentage = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    tds_min_amount = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    pv_multiplier = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
