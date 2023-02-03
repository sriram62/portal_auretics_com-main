


def check_registration_form_fn(check_user_qs):
    if check_user_qs.check_first_name == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_last_name == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_email == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_date_of_birth == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_house_number == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_address_line == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_Landmark == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_city == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_state == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_street == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_pin == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_mobile == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_alternate_mobile == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_pan_number == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_pan_file == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_id_proof_type == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_id_proof_file == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_address_proof_type == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_address_proof_file == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_distributors_name_in_bank_account == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_bank_name == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_account_number == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_ifsc_code == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_branch_name == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_cheque_photo == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_age_confirmation == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_co_applicant == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_blood_group == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_blood_rh_factor == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_profile_active == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_first_terms_conditions == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_second_terms_conditions == False:
        registration_form = 'Registration  is pending verification'
    elif check_user_qs.check_gender == False:
        registration_form = 'Registration  is pending verification'
    else:
        registration_form = 'Registration  is Complete'
    return registration_form