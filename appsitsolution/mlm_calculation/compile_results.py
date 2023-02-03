from .models import *
from django.shortcuts import render,redirect,HttpResponse
from django.db import transaction
from django.contrib import messages
from accounts.models import *
from shop.models import *
import json
import xlwt
from datetime import datetime
from .check_permit import check_permission

def blank_query_to_zero(qs):
    # print(qs)
    if qs:
        for i in qs:
            # print(i)
            return i
    else:
        qs.direct_bonus_earned                  = 0
        qs.team_building_bonus_earned           = 0
        qs.leadership_building_bonus_earned     = 0
        qs.life_style_fund_earned               = 0
        qs.personal_bonus_earned                = 0
        qs.fortune_bonus_earned                 = 0
        qs.sharing_bonus_earned                 = 0
        qs.nurturing_bonus_earned               = 0
        qs.business_master_bonus_earned         = 0
        qs.vacation_fund_earned                 = 0
        qs.automobile_fund_earned               = 0
        qs.shelter_fund_earned                  = 0
        qs.cri_earned                           = 0
        qs.balance                              = 0
        qs.bank_account_user                    = ""
        qs.distributors_name_in_bank_account    = ""
        qs.bank_name                            = ""
        qs.account_number                       = ""
        qs.ifsc_code                            = ""
        qs.branch_name                          = ""
        qs.check_first_name                     = False
        qs.check_last_name                      = False
        qs.check_email                          = False
        qs.check_date_of_birth                  = False
        qs.check_house_number                   = False
        qs.check_address_line                   = False
        qs.check_Landmark                       = False
        qs.check_city                           = False
        qs.check_state                          = False
        qs.check_street                         = False
        qs.check_pin                            = False
        qs.check_mobile                         = False
        qs.check_alternate_mobile               = False
        qs.check_pan_number                     = False
        qs.check_pan_file                       = False
        qs.check_id_proof_type                  = False
        qs.check_id_proof_file                  = False
        qs.check_address_proof_type             = False
        qs.check_address_proof_file             = False
        qs.check_distributors_name_in_bank_account = False
        qs.check_bank_name                      = False
        qs.check_account_number                 = False
        qs.check_ifsc_code                      = False
        qs.check_branch_name                    = False
        qs.check_cheque_photo                   = False
        qs.check_age_confirmation               = False
        qs.check_co_applicant                   = False
        qs.check_blood_group                    = False
        qs.check_blood_rh_factor                = False
        qs.check_profile_active                 = False
        qs.check_first_terms_conditions         = False
        qs.check_second_terms_conditions        = False
        qs.check_gender                         = False
        qs.check_registration_status            = False
        qs.city                                 = ""
        qs.house_number                         = ""
        qs.address_line                         = ""
        qs.Landmark                             = ""
        qs.state                                = ""
        qs.street                               = ""
        return qs
        

def compile_result_fn(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    """
    In this function we are calculating:
    1) The income-wise summary of all the users;
    2) Adding them to the commission wallet;
    3) Preparing the file as per RBI Adapter for upload directly to the Bank's Website
    """
    print("compile_result_fn")
    if request.method == 'POST':
        print("compile_result_fn_inside post")
        month_cal = request.POST.get('month', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()
            if month == 1:
                previous_month = 12
                previous_year = int(year) - 1
            else:
                previous_month = int(month) - 1
                previous_year = year
            # [Flow] Delete Old Data
            results_commission_calculation = commission_calculation_model.objects.filter(date_model__month = month,
                                                                                    date_model__year = year).delete()
            results_commission_wallet = commission_wallet_model.objects.filter(input_date__month = month,
                                                                                    input_date__year = year).delete()
            results_commission_wallet_amount_out_detail = commission_wallet_amount_out_detail_model.objects.filter(input_date__month = month,
                                                                                    input_date__year = year).delete()
            
            # inner_configurations_qs = inner_configurations.objects.last()
                                                                                    
            all_titles  = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year)
            infinity_qs = infinity_model.objects.last()
            super_qs    = super_model.objects.last()
            
            user_loop_no = 0
            for title in all_titles:
                user_first_name     = Profile.objects.get(user=title.user)
                user_last_name      = Profile.objects.get(user=title.user)
                user_mobile_number  = Profile.objects.get(user=title.user)
                user_arn            = ReferralCode.objects.get(user_id=title.user)
                
                user_loop_no += 1
                # [Flow] Check if KYC is done
                if blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_first_name \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_last_name \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_email \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_date_of_birth \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_house_number \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_address_line \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_Landmark \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_city \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_state \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_street \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_pin \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_mobile \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_alternate_mobile \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_pan_number \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_pan_file \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_id_proof_type \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_id_proof_file \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_address_proof_type  \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_address_proof_file  \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_distributors_name_in_bank_account \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_bank_name \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_account_number \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_ifsc_code  \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_branch_name  \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_cheque_photo  \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_age_confirmation  \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_co_applicant  \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_blood_group \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_blood_rh_factor \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_profile_active \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_first_terms_conditions \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_second_terms_conditions \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_gender \
                    and blank_query_to_zero(User_Check.objects.filter(user_check = title.user)).check_registration_status:
                    kyc_status = True
                else:
                    kyc_status = False
                        
                
                # [Flow] Calculating Total Commission of the User
                user                                        = title.user
                user_active                                 = title.user_active
                current_month_qualification                 = title.current_month_qualification
                direct_bonus_current_month                  = blank_query_to_zero(direct_bonus_super_plan_model.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).direct_bonus_earned
                direct_bonus_till_date                      = blank_query_to_zero(direct_bonus_super_plan_model.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).direct_bonus_earned + direct_bonus_current_month
                team_building_bonus_current_month           = blank_query_to_zero(team_building_bonus_super_plan_model.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).team_building_bonus_earned
                team_building_bonus_till_date               = blank_query_to_zero(team_building_bonus_super_plan_model.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).team_building_bonus_earned + team_building_bonus_current_month
                leadership_building_bonus_current_month     = blank_query_to_zero(leadership_building_bonus_super_plan_model.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).leadership_building_bonus_earned
                leadership_building_bonus_till_date         = blank_query_to_zero(leadership_building_bonus_super_plan_model.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).leadership_building_bonus_earned + leadership_building_bonus_current_month
                lifestyle_fund_current_month                = leadership_building_bonus_current_month
                lifestyle_fund_till_date                    = leadership_building_bonus_till_date
                retail_margin_current_month                 = 0
                retail_margin_till_date                     = 0
                personal_bonus_current_month                = blank_query_to_zero(personal_bonus.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).personal_bonus_earned
                personal_bonus_till_date                    = blank_query_to_zero(personal_bonus.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).personal_bonus_earned + personal_bonus_current_month
                fortune_bonus_current_month                 = blank_query_to_zero(fortune_bonus.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).fortune_bonus_earned
                fortune_bonus_till_date                     = blank_query_to_zero(fortune_bonus.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).fortune_bonus_earned + fortune_bonus_current_month
                sharing_bonus_current_month                 = blank_query_to_zero(sharing_bonus.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).sharing_bonus_earned
                sharing_bonus_till_date                     = blank_query_to_zero(sharing_bonus.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).sharing_bonus_earned + sharing_bonus_current_month
                nurturing_bonus_current_month               = blank_query_to_zero(nuturing_bonus.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).nurturing_bonus_earned
                nurturing_bonus_till_date                   = blank_query_to_zero(nuturing_bonus.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).nurturing_bonus_earned + nurturing_bonus_current_month
                business_master_bonus_current_month         = blank_query_to_zero(business_master_bonus.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).business_master_bonus_earned
                business_master_bonus_till_date             = blank_query_to_zero(business_master_bonus.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).business_master_bonus_earned + business_master_bonus_current_month
                vacation_fund_bonus_current_month           = blank_query_to_zero(vacation_fund.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).vacation_fund_earned
                vacation_fund_bonus_till_date               = blank_query_to_zero(vacation_fund.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).vacation_fund_earned + vacation_fund_bonus_current_month
                automobile_fund_bonus_current_month         = blank_query_to_zero(automobile_fund.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).automobile_fund_earned
                automobile_fund_bonus_till_date             = blank_query_to_zero(automobile_fund.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).automobile_fund_earned + automobile_fund_bonus_current_month
                shelter_fund_bonus_current_month            = blank_query_to_zero(shelter_fund.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).shelter_fund_earned
                shelter_fund_bonus_till_date                = blank_query_to_zero(shelter_fund.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).shelter_fund_earned + shelter_fund_bonus_current_month
                consistent_retailers_income_current_month   = blank_query_to_zero(consistent_retailers_income.objects.filter(user = title.user, input_date__month = month,input_date__year = year)).cri_earned
                consistent_retailers_income_till_date       = blank_query_to_zero(consistent_retailers_income.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).cri_earned + consistent_retailers_income_current_month
                elite_incentive_current_month               = 0
                elite_incentive_till_date                   = 0
                meeting_expense_current_month               = 0
                meeting_expense_till_date                   = 0
                admin_charge_current_month                  = 0
                admin_charge_till_date                      = 0
                advertisement_current_month                 = 0
                advertisement_till_date                     = 0
                    
                commission_calculation_model_qs = commission_calculation_model(user                                     = user,
                                                                            user_active                                 = user_active,
                                                                            user_name                                   = str(user_first_name) + str(user_last_name),
                                                                            mobile_number                               = str(user_mobile_number),
                                                                            ARN                                         = str(user_arn),
                                                                            current_month_qualification                 = current_month_qualification,
                                                                            direct_bonus_current_month                  = direct_bonus_current_month,
                                                                            direct_bonus_till_date                      = direct_bonus_till_date,
                                                                            team_building_bonus_current_month           = team_building_bonus_current_month,
                                                                            team_building_bonus_till_date               = team_building_bonus_till_date,
                                                                            leadership_building_bonus_current_month     = leadership_building_bonus_current_month,
                                                                            leadership_building_bonus_till_date         = leadership_building_bonus_till_date,
                                                                            lifestyle_fund_current_month                = lifestyle_fund_current_month,
                                                                            lifestyle_fund_till_date                    = lifestyle_fund_till_date,
                                                                            retail_margin_current_month                 = retail_margin_current_month,
                                                                            retail_margin_till_date                     = retail_margin_till_date,
                                                                            personal_bonus_current_month                = personal_bonus_current_month,
                                                                            personal_bonus_till_date                    = personal_bonus_till_date,
                                                                            fortune_bonus_current_month                 = fortune_bonus_current_month,
                                                                            fortune_bonus_till_date                     = fortune_bonus_till_date,
                                                                            sharing_bonus_current_month                 = sharing_bonus_current_month,
                                                                            sharing_bonus_till_date                     = sharing_bonus_till_date,
                                                                            nurturing_bonus_current_month               = nurturing_bonus_current_month,
                                                                            nurturing_bonus_till_date                   = nurturing_bonus_till_date,
                                                                            business_master_bonus_current_month         = business_master_bonus_current_month,
                                                                            business_master_bonus_till_date             = business_master_bonus_till_date,
                                                                            vacation_fund_bonus_current_month           = vacation_fund_bonus_current_month,
                                                                            vacation_fund_bonus_till_date               = vacation_fund_bonus_till_date,
                                                                            automobile_fund_bonus_current_month         = automobile_fund_bonus_current_month,
                                                                            automobile_fund_bonus_till_date             = automobile_fund_bonus_till_date,
                                                                            shelter_fund_bonus_current_month            = shelter_fund_bonus_current_month,
                                                                            shelter_fund_bonus_till_date                = shelter_fund_bonus_till_date,
                                                                            consistent_retailers_income_current_month   = consistent_retailers_income_current_month,
                                                                            consistent_retailers_income_till_date       = consistent_retailers_income_till_date,
                                                                            elite_incentive_current_month               = elite_incentive_current_month,
                                                                            elite_incentive_till_date                   = elite_incentive_till_date,
                                                                            meeting_expense_current_month               = meeting_expense_current_month,
                                                                            meeting_expense_till_date                   = meeting_expense_till_date,
                                                                            admin_charge_current_month                  = admin_charge_current_month,
                                                                            admin_charge_till_date                      = admin_charge_till_date,
                                                                            advertisement_current_month                 = advertisement_current_month,
                                                                            advertisement_till_date                     = advertisement_till_date, 
                                                                            draft_date                                  = today_date,
                                                                            )
                commission_calculation_model_qs.save()
                
                # [Flow] Calculating Commission Wallet of the User 
                # Total Cash Bonus
                total_commission_amount = direct_bonus_current_month \
                                            + team_building_bonus_current_month \
                                            + leadership_building_bonus_current_month \
                                            + personal_bonus_current_month \
                                            + fortune_bonus_current_month \
                                            + sharing_bonus_current_month \
                                            + nurturing_bonus_current_month \
                                            + business_master_bonus_current_month
                
                # Bonus to become part of Funds
                total_fund_amount       = lifestyle_fund_current_month\
                                            + vacation_fund_bonus_current_month \
                                            + automobile_fund_bonus_current_month \
                                            + shelter_fund_bonus_current_month
                                            
                # Bonus to become part of Consistent Retailer's Income
                total_consistent_retail_income  = consistent_retailers_income_current_month
                
                # Retail Margin (not bonus)
                total_retail_margin     = retail_margin_current_month 
                
                # Applicable TDS rate
                # AG :: If total commission for this financial year (i.e. 1st April to 31st March) > Rs. 5000, then 5% TDS on complete payment
                # When user gets commission for the first time, then TDS will be deducted for previous payment in the Financial Year also.

                # Frontend pages
                # TDS deducted - Username | Referral Code | Commission | TDS on Commission | Total Commission in FY | Total TDS in this FY
                # TDS to be paid, every month
                # TDS paid or not

                # This is wrong method
                # tds = total_commission_amount * inner_configurations_qs.tds_percentage / 100
                tds = 0.0

                amount_in                               = total_commission_amount
                amount_out                              = 0.0
                commission_wallet_model_balance_prev    = blank_query_to_zero(commission_wallet_model.objects.filter(user = title.user, input_date__month = previous_month,input_date__year = previous_year)).balance
                commission_payable                      = float(amount_in) - tds
                commission_wallet_model_balance         = float(commission_wallet_model_balance_prev) + float(commission_payable) - float(amount_out)
                beneficiary_code                        = str(user) + str(user_loop_no)
                transaction_id                          = str(month_cal) + beneficiary_code

                if (float(amount_in) + float(commission_wallet_model_balance_prev)) > 0.0:
                    commission_wallet_model_qs = commission_wallet_model(user               = user,
                                                                        user_name           = str(user_first_name) + str(user_last_name),
                                                                        mobile_number       = str(user_mobile_number),
                                                                        ARN                 = str(user_arn),
                                                                        input_date          = month_cal,
                                                                        user_active         = user_active,
                                                                        kyc_done            = kyc_status,
                                                                        transaction_type    = "Credit",
                                                                        transaction_id      = transaction_id,
                                                                        account_hit         = "Commission Account",
                                                                        heading             = "Commission for the Month of " + str(month) + " - " +str(year),
                                                                        narration           = "",
                                                                        amount_in           = total_commission_amount,
                                                                        amount_out          = 0,
                                                                        tds                 = tds,
                                                                        balance             = commission_wallet_model_balance,
                                                                        draft_date          = today_date
                                                                        )
                    commission_wallet_model_qs.save()

                    # [Flow] Preparing RBI Adapter File (Commission Out Model)
                    transaction_type                        = "N"
                    beneficiary_account_number              = blank_query_to_zero(BankAccountDetails.objects.filter(bank_account_user = title.user)).account_number
                    ifsc                                    = blank_query_to_zero(BankAccountDetails.objects.filter(bank_account_user = title.user)).ifsc_code
                    instrument_amount_without_comma_style   = str(commission_payable)
                    beneficiary_name                        = blank_query_to_zero(BankAccountDetails.objects.filter(bank_account_user = title.user)).distributors_name_in_bank_account
                    drawee_location                         = blank_query_to_zero(Address.objects.filter(user = title.user)).city
                    print_location                          = blank_query_to_zero(Address.objects.filter(user = title.user)).city
                    bene_address_1                          = blank_query_to_zero(Address.objects.filter(user = title.user)).house_number
                    bene_address_2                          = blank_query_to_zero(Address.objects.filter(user = title.user)).address_line
                    bene_address_3                          = blank_query_to_zero(Address.objects.filter(user = title.user)).Landmark
                    bene_address_4                          = blank_query_to_zero(Address.objects.filter(user = title.user)).street
                    bene_address_5                          = blank_query_to_zero(Address.objects.filter(user = title.user)).state
                    instruction_reference_number            = ""
                    customer_reference_number               = str(user)
                    payment_details_1                       = "Commission for the Month of " + str(month) + " - " +str(year)
                    payment_details_2                       = ""
                    payment_details_3                       = ""
                    payment_details_4                       = ""
                    payment_details_5                       = ""
                    payment_details_6                       = ""
                    payment_details_7                       = ""
                    cheque_number                           = str(user_loop_no) + str(month_cal)
                    chq_trn_date                            = today_date
                    micr_number                             = ""
                    bene_bank_name                          = blank_query_to_zero(BankAccountDetails.objects.filter(bank_account_user = title.user)).bank_name
                    bene_bank_branch_name                   = blank_query_to_zero(BankAccountDetails.objects.filter(bank_account_user = title.user)).branch_name
                    beneficiary_email_id                    = title.user

                    commission_wallet_amount_out_detail_model_qs = commission_wallet_amount_out_detail_model(user                                   = user,
                                                                                                            user_name                               = str(user_first_name) + str(user_last_name),
                                                                                                            mobile_number                           = str(user_mobile_number),
                                                                                                            ARN                                     = str(user_arn),
                                                                                                            input_date                              = month_cal,
                                                                                                            kyc_done                                = kyc_status,
                                                                                                            transaction_id                          = transaction_id,
                                                                                                            transaction_type                        = transaction_type,
                                                                                                            beneficiary_code                        = beneficiary_code,
                                                                                                            beneficiary_account_number              = beneficiary_account_number,
                                                                                                            ifsc                                    = ifsc,
                                                                                                            instrument_amount_without_comma_style   = instrument_amount_without_comma_style,
                                                                                                            beneficiary_name                        = beneficiary_name,
                                                                                                            drawee_location                         = drawee_location,
                                                                                                            print_location                          = print_location,
                                                                                                            bene_address_1                          = bene_address_1,
                                                                                                            bene_address_2                          = bene_address_2,
                                                                                                            bene_address_3                          = bene_address_3,
                                                                                                            bene_address_4                          = bene_address_4,
                                                                                                            bene_address_5                          = bene_address_5,
                                                                                                            instruction_reference_number            = instruction_reference_number,
                                                                                                            customer_reference_number               = customer_reference_number,
                                                                                                            payment_details_1                       = payment_details_1,
                                                                                                            payment_details_2                       = payment_details_2,
                                                                                                            payment_details_3                       = payment_details_3,
                                                                                                            payment_details_4                       = payment_details_4,
                                                                                                            payment_details_5                       = payment_details_5,
                                                                                                            payment_details_6                       = payment_details_6,
                                                                                                            payment_details_7                       = payment_details_7,
                                                                                                            cheque_number                           = cheque_number,
                                                                                                            chq_trn_date                            = chq_trn_date,
                                                                                                            micr_number                             = micr_number,
                                                                                                            ifsc_code                               = ifsc,
                                                                                                            bene_bank_name                          = bene_bank_name,
                                                                                                            bene_bank_branch_name                   = bene_bank_branch_name,
                                                                                                            beneficiary_email_id                    = beneficiary_email_id,
                                                                                                            draft_date                              = today_date,
                                                                                                            )

                    commission_wallet_amount_out_detail_model_qs.save()
            return HttpResponse('<h1>Welcome Auretics! If you are at this page it means Compilations are calculated Successfully!!!</h1>')


    try:
        public_data = commission_calculation_model.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.input_date
        public_month = public_data.input_date

    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = commission_calculation_model.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.input_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}
    return render(request,'mlm_calculation/compile_results.html',params)


def commission_calculation_model_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        print(month_cal,'<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = Compiled Results' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Commission Calculation Model')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 
                      'user',
                      'user_name',
                      'mobile_number',
                      'ARN',
                      'date_model',
                      'calculation_stage',
                      'user_enabled',
                      'user_active',
                      'current_month_qualification',
                      'direct_bonus_current_month',
                      'direct_bonus_till_date',
                      'team_building_bonus_current_month',
                      'team_building_bonus_till_date',
                      'leadership_building_bonus_current_month',
                      'leadership_building_bonus_till_date',
                      'lifestyle_fund_current_month',
                      'lifestyle_fund_till_date',
                      'retail_margin_current_month',
                      'retail_margin_till_date',
                      'personal_bonus_current_month',
                      'personal_bonus_till_date',
                      'fortune_bonus_current_month',
                      'fortune_bonus_till_date',
                      'sharing_bonus_current_month',
                      'sharing_bonus_till_date',
                      'nurturing_bonus_current_month',
                      'nurturing_bonus_till_date',
                      'business_master_bonus_current_month',
                      'business_master_bonus_till_date',
                      'vacation_fund_bonus_current_month',
                      'vacation_fund_bonus_till_date',
                      'automobile_fund_bonus_current_month',
                      'automobile_fund_bonus_till_date',
                      'shelter_fund_bonus_current_month',
                      'shelter_fund_bonus_till_date',
                      'consistent_retailers_income_current_month',
                      'consistent_retailers_income_till_date',
                      'elite_incentive_current_month',
                      'elite_incentive_till_date',
                      'meeting_expense_current_month',
                      'meeting_expense_till_date',
                      'admin_charge_current_month',
                      'admin_charge_till_date',
                      'advertisement_current_month',
                      'advertisement_till_date',
                      'draft_date',
                      'public_date',
                      ]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = commission_calculation_model.objects.filter(date_model__month = month,date_model__year = year).values_list(
                'pk',
                'user__username',  
                'user_name',
                'mobile_number',
                'ARN',
                'date_model',
                'calculation_stage',
                'user_enabled',
                'user_active',
                'current_month_qualification',
                'direct_bonus_current_month',
                'direct_bonus_till_date',
                'team_building_bonus_current_month',
                'team_building_bonus_till_date',
                'leadership_building_bonus_current_month',
                'leadership_building_bonus_till_date',
                'lifestyle_fund_current_month',
                'lifestyle_fund_till_date',
                'retail_margin_current_month',
                'retail_margin_till_date',
                'personal_bonus_current_month',
                'personal_bonus_till_date',
                'fortune_bonus_current_month',
                'fortune_bonus_till_date',
                'sharing_bonus_current_month',
                'sharing_bonus_till_date',
                'nurturing_bonus_current_month',
                'nurturing_bonus_till_date',
                'business_master_bonus_current_month',
                'business_master_bonus_till_date',
                'vacation_fund_bonus_current_month',
                'vacation_fund_bonus_till_date',
                'automobile_fund_bonus_current_month',
                'automobile_fund_bonus_till_date',
                'shelter_fund_bonus_current_month',
                'shelter_fund_bonus_till_date',
                'consistent_retailers_income_current_month',
                'consistent_retailers_income_till_date',
                'elite_incentive_current_month',
                'elite_incentive_till_date',
                'meeting_expense_current_month',
                'meeting_expense_till_date',
                'admin_charge_current_month',
                'admin_charge_till_date',
                'advertisement_current_month',
                'advertisement_till_date',
                'draft_date',
                'public_date',
                )
            if len(rows)< 1:
                messages.success(request, 'This month Commission Calculation is not Calculated!')
                return redirect('mlm_calculation_compile_result')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Cri is not Calculated!')
    return redirect('mlm_calculation_compile_result')


def commission_wallet_model_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = Compiled Results' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Commission Wallet Model')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 
                      'user',
                      'user_name',
                      'mobile_number',
                      'ARN',
                      'created_on',
                      'input_date',
                      'user_enabled',
                      'user_active',
                      'kyc_done',
                      'transaction_type',
                      'transaction_id',
                      'account_hit',
                      'heading',
                      'narration',
                      'amount_in',
                      'amount_out',
                      'tds',
                      'balance',
                      'audit_balance',
                      'calculation_stage',
                      'draft_date',
                      'public_date',
                      ]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = commission_wallet_model.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username',  
                'user_name',
                'mobile_number',
                'ARN',
                'created_on',
                'input_date',
                'user_enabled',
                'user_active',
                'kyc_done',
                'transaction_type',
                'transaction_id',
                'account_hit',
                'heading',
                'narration',
                'amount_in',
                'amount_out',
                'tds',
                'balance',
                'audit_balance',
                'calculation_stage',
                'draft_date',
                'public_date',
                )
            if len(rows)< 1:
                messages.success(request, 'This month Commission Wallet is not Calculated!')
                return redirect('mlm_calculation_compile_result')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Cri is not Calculated!')
    return redirect('mlm_calculation_compile_result')



def commission_wallet_amount_out_detail_model_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        print(month_cal,'<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = Compiled Results' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Commission Wallet Amount Out')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 
                      'user',
                      'user_name',
                      'mobile_number',
                      'ARN',
                      'created_on',
                      'input_date',
                      'calculation_stage',
                      'kyc_done',
                      'transaction_id',
                      'transaction_type',
                      'beneficiary_code',
                      'beneficiary_account_number',
                      'ifsc',
                      'instrument_amount_without_comma_style',
                      'beneficiary_name',
                      'drawee_location',
                      'print_location',
                      'bene_address_1',
                      'bene_address_2',
                      'bene_address_3',
                      'bene_address_4',
                      'bene_address_5',
                      'instruction_reference_number',
                      'customer_reference_number',
                      'payment_details_1',
                      'payment_details_2',
                      'payment_details_3',
                      'payment_details_4',
                      'payment_details_5',
                      'payment_details_6',
                      'payment_details_7',
                      'cheque_number',
                      'chq_trn_date',
                      'micr_number',
                      'ifsc_code',
                      'bene_bank_name',
                      'bene_bank_branch_name',
                      'beneficiary_email_id',
                      'draft_date',
                      'public_date',
                      ]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = commission_wallet_amount_out_detail_model.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 
                'user_name',
                'mobile_number',
                'ARN', 
                'created_on',
                'input_date',
                'calculation_stage',
                'kyc_done',
                'transaction_id',
                'transaction_type',
                'beneficiary_code',
                'beneficiary_account_number',
                'ifsc',
                'instrument_amount_without_comma_style',
                'beneficiary_name',
                'drawee_location',
                'print_location',
                'bene_address_1',
                'bene_address_2',
                'bene_address_3',
                'bene_address_4',
                'bene_address_5',
                'instruction_reference_number',
                'customer_reference_number',
                'payment_details_1',
                'payment_details_2',
                'payment_details_3',
                'payment_details_4',
                'payment_details_5',
                'payment_details_6',
                'payment_details_7',
                'cheque_number',
                'chq_trn_date',
                'micr_number',
                'ifsc_code',
                'bene_bank_name',
                'bene_bank_branch_name',
                'beneficiary_email_id',
                'draft_date',
                'public_date',
                )
            if len(rows)< 1:
                messages.success(request, 'This month Commission Wallet is not Calculated!')
                return redirect('mlm_calculation_compile_result')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Cri is not Calculated!')
    return redirect('mlm_calculation_compile_result')
    


def compile_result_publish(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('publish_date', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()
            success = False
            
            value_commission_calculation                = commission_calculation_model.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            value_commission_wallet                     = commission_wallet_model.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            value_ommission_wallet_amount_out_detail    = commission_wallet_amount_out_detail_model.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            
            if value_commission_calculation == True:
                data_qs = commission_calculation_model.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                        calculation_stage = 'Public')
                success = True
            if value_commission_wallet == True:
                data_qs = commission_wallet_model.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                        calculation_stage = 'Public')
                success = True
            if value_ommission_wallet_amount_out_detail == True:
                data_qs = commission_wallet_amount_out_detail_model.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                        calculation_stage = 'Public')
                success = True
            if success == True:
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('mlm_calculation_compile_result')