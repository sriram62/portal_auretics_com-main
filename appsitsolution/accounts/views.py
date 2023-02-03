from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from mlm_admin.forms import CheckForm
from django.contrib.auth import authenticate,login, logout,  update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
# from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm, PasswordChangeForm)
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from shop.forms import AddressForm
from .models import *
from shop.models import *
from shop.models import CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from shop import cart
from mlm_admin.views import is_mlm_admin, Objectify
from mlm_admin.decorator import allowed_users
from accounts.gencode import genReferralCode
from .sms import sendsms
from accounts.sms import *
import boto3
import urllib.parse
import json
import random
import requests
from datetime import datetime, timedelta
import base64
import pyotp

from wallet.models import Wallet
from wallet.views import JuspayPayment
from django.db import transaction

from .bank_proof import Bank_proof_api, Pan_verification
from .common_code import check_registration_form_fn

# AG Shout :: Increase recursion limit to handle user depth till 1,00,00,000 levels.
# Used information provided at https://www.geeksforgeeks.org/python-handling-recursion-limit/
# importing the sys module
import sys

from mlm_admin.sr_api_call import OrderMaintain
from mlm_admin.models import ManualVerification

from django.core.mail import send_mail
import random
from portal_auretics_com import settings

# Common Variables
kyc_pan_fail_message = "KYC Verification is Pending"
kyc_pan_pass_message = "Congrats KYC Verified Partially"


# the setrecursionlimit function is used to modify the default recursion limit set by python.
sys.setrecursionlimit(10**6)
# Create your views here.

EXPIRY_TIME = 60*30 # seconds

 
def user_login(request):
    if request.method == 'POST':
        if 'mobile' in request.POST and 'otp' in request.POST:
            mobile = request.POST.get('mobile')
            mobile_otp = request.POST.get('otp')
            if not mobile_otp:
                messages.warning(request,"OTP is wrong/expired")
                return redirect('home')
                # return HttpResponse('<script>alert(OTP is wrong/expired);</script>')

            try:
                prof = Profile.objects.get(phone_number= mobile)
                email = prof.user.username
            except ObjectDoesNotExist:
                messages.warning(request,"Mobile number is not valid")
                # return HttpResponse('<script>alert(Mobile number is not valid);</script>')
                return redirect('home')

            keygen = generateKey()
            key = base64.b32encode(keygen.returnValue(mobile).encode())  # Generating Key
            OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model

            if OTP.verify(mobile_otp):  # Verifying the OTP
                 
                user = User.objects.get(email=email)
                check = User_Check.objects.get(user_check=user)
                check.check_mobile = True
                check.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                valuenext= request.POST.get('next')
                clientkey = request.POST['g-recaptcha-response']
                serverkey = '6LeVCKgaAAAAADsn51OcTxu6-wZ_THxWCT7b_GoA'
                captchaData = {
                    'secret': serverkey,
                    'response': clientkey
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify',data=captchaData)
                response = json.loads(r.text)
                verify = response['success']
                verify = True

                if verify:

                    if user is not None and valuenext=='':
                        check = User_Check.objects.get(user_check=user)
                        check.check_mobile = True
                        check.user_check
                        check.save()
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        if request.session['cart_id']:
                            cart_id = request.session['cart_id']
                            cart_session_item = CartItem.objects.filter(cart_id = cart_id)
                            # cart_session_item = recalculate_cart(cart_session_item)
                            if len(cart_session_item)>0:
                                cart_user_item = CartItem.objects.filter(user = user).first()
                                # cart_user_item = recalculate_cart(cart_user_item)
                                if cart_user_item != None:
                                     user_database_cart_id = cart_user_item.cart_id
                                cart_user_item_delete = CartItem.objects.filter(user = user).delete()
                                CartItem.objects.filter(cart_id = cart_id).update(user=user)
                                if cart_user_item != None:
                                    CartItem.objects.filter(user = user).update(cart_id=user_database_cart_id)
                                    request.session['cart_id'] = user_database_cart_id
                            else:
                                cart_user_item = CartItem.objects.filter(user = user).first()
                                # cart_user_item = recalculate_cart(cart_user_item)
                                if cart_user_item != None:
                                    request.session['cart_id'] = cart_user_item.cart_id
                        else:
                            cart_id = CartItem.objects.filter(user=request.user).first()
                            # cart_id = recalculate_cart(cart_id)
                            for i in cart_id:
                                request.session['i.cart_id'] = i.cart_id

                        context= {'valuenext': valuenext}             # next value is being kept insidecontext
                        messages.success(
                                request, "Welcome! You've been signed in"   #a success message is bein sent
                                )
                        return redirect('home')
                    elif user is not None and valuenext !='':
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        if request.session['cart_id']:
                            cart_id = request.session['cart_id']
                            cart_session_item = CartItem.objects.filter(cart_id = cart_id)
                            # cart_session_item = recalculate_cart(cart_session_item)
                            if len(cart_session_item)>0:
                                cart_user_item = CartItem.objects.filter(user = user).first()
                                # cart_user_item = recalculate_cart(cart_user_item)
                                if cart_user_item != None:
                                     user_database_cart_id = cart_user_item.cart_id
                                cart_user_item_delete = CartItem.objects.filter(user = user).delete()
                                CartItem.objects.filter(cart_id = cart_id).update(user=user)

                                if cart_user_item != None:
                                    CartItem.objects.filter(user = user).update(cart_id = user_database_cart_id)
                                    request.session['cart_id'] = user_database_cart_id
                            else:
                                cart_user_item = CartItem.objects.filter(user = user).first()
                                if cart_user_item != None:
                                    request.session['cart_id'] = cart_user_item.cart_id

                        else:
                            cart_id = CartItem.objects.filter(user=request.user).first()
                            # cart_id = recalculate_cart(cart_id)
                            for i in cart_id:
                                request.session['i.cart_id'] = i.cart_id

                        messages.success(request, "You have successfully logged in")
                        valuenext =valuenext.strip('/')
                        context= {'valuenext': valuenext}
                        return redirect('checkout')
                    else:
                        messages.warning(request,"Wrong Credentials")
                        return redirect('home')

            messages.warning(request,"OTP is wrong/expired")
            return redirect('home')

        else:
            email = request.POST.get('username')
            # getting username from the user
            # emails will be upper cased to ensure that ARN numbers are picked in all cases.
            email = str(email).upper()
            try:
                referal = ReferralCode.objects.get(referral_code = email)                 #getting email and putting into referal variable
                email = referal.user_id.username                                          #store the username of the selected id of referal inside email.
            except:
                pass
            try:
                prof = Profile.objects.get(phone_number = email)                          #getting email of the user and saving it under "prof"
                email = prof.user.username                                                #gettng username from profile-->user and saving under email
            except:
                pass
            email = email.lower()                                                         #email should be in lower case
            password =request.POST.get('password')                                        #getting password and saving under password variable
             #to show that user is authenticated or genuine , system requests for username and password
            user = authenticate(request, username= email, password=password)
            valuenext= request.POST.get('next')
            # here we are writing code for recaptchar
            clientkey = request.POST['g-recaptcha-response']
            #A POST Request is being sent to request for a specified URL.
            #Serverkey is being generated
            #Here, Data is being captured by putting serverkey inside "secret"
             #and clientkey inside "response"
            serverkey = '6LeVCKgaAAAAADsn51OcTxu6-wZ_THxWCT7b_GoA'
            captchaData = {
                'secret': serverkey,
                'response': clientkey
            }

              #POST request is being sent for a specific URL that is saved inside "r" variable ,
              #response is being loaded by json and verified, after that a verified print statement
              #is being printed.

            r = requests.post('https://www.google.com/recaptcha/api/siteverify',data=captchaData)
            response = json.loads(r.text)
            verify = response['success']
            if verify:
            # here we are writing code for recaptchar
                if user is not None and valuenext=='':
                    login(request, user)
                    try:
                        if request.session['cart_id']:
                            cart_id = request.session['cart_id']
                            cart_session_item = CartItem.objects.filter(cart_id = cart_id)
                            # cart_session_item = recalculate_cart(cart_session_item)
            # <--!-------------------------------------------nipur code start 9-02-2021--------------------------------------------------------!-->
                          # length of cart session is being estimated and likewise the logic to establish cart user items.

                            if len(cart_session_item)>0:
                                cart_user_item = CartItem.objects.filter(user = user).first()
                                # cart_user_item = recalculate_cart(cart_user_item)
                                if cart_user_item != None:
                                     user_database_cart_id = cart_user_item.cart_id
                                cart_user_item_delete = CartItem.objects.filter(user = user).delete()
                                CartItem.objects.filter(cart_id = cart_id).update(user=user)
                                if cart_user_item != None:
                                    CartItem.objects.filter(user = user).update(cart_id = user_database_cart_id)
                                    request.session['cart_id'] = user_database_cart_id
                            else:
                                cart_user_item = CartItem.objects.filter(user = user).first()
                                # cart_user_item = recalculate_cart(cart_user_item)
                                if cart_user_item != None:
                                    request.session['cart_id'] = cart_user_item.cart_id
                        else:
                            cart_id = CartItem.objects.filter(user=request.user).first()
                            # cart_id = recalculate_cart(cart_id)
                            for i in cart_id:
                                request.session['i.cart_id'] = i.cart_id
                    except:
                        cart_id = CartItem.objects.filter(user=request.user).first()
                        # cart_id = recalculate_cart(cart_id)
                        for i in cart_id:
                            request.session['i.cart_id'] = i.cart_id


                    context= {'valuenext': valuenext}             # next value is being kept insidecontext
                    messages.success(
                            request, "Welcome! You've been signed in"   #a success message is bein sent
                            )
                    # return render(request, 'base.html', context)
                    return redirect(request.META.get('HTTP_REFERER'))
                    # return JsonResponse({'a': True})
                elif user is not None and valuenext !='':
                    login(request, user)
                    if request.session['cart_id']:
                        cart_id = request.session['cart_id']
                        cart_session_item = CartItem.objects.filter(cart_id = cart_id)
                        # cart_session_item = recalculate_cart(cart_session_item)
                        if len(cart_session_item)>0:
                            cart_user_item = CartItem.objects.filter(user = user).first()
                            # cart_user_item = recalculate_cart(cart_user_item)
                            if cart_user_item != None:
                                 user_database_cart_id = cart_user_item.cart_id
                            cart_user_item_delete = CartItem.objects.filter(user=user).delete()
                            CartItem.objects.filter(cart_id=cart_id).update(user=user)

                            if cart_user_item != None:
                                CartItem.objects.filter(user = user).update(cart_id=user_database_cart_id)
                                request.session['cart_id'] = user_database_cart_id
                            # < ------------------------------------------ this is my new code 20 feb -------------------------------->
                            cart_user_item = CartItem.objects.filter(user = user).delete()
                            CartItem.objects.filter(cart_id = cart_id).update(user=user)
                        else:
                            cart_user_item = CartItem.objects.filter(user = user).first()
                            # cart_user_item = recalculate_cart(cart_user_item)
                            if cart_user_item != None:
                                request.session['cart_id'] = cart_user_item.cart_id
                    else:
                        cart_id = CartItem.objects.filter(user=request.user).first()
                        # cart_user_item = recalculate_cart(cart_user_item)
                        for i in cart_id:
                            request.session['i.cart_id'] = i.cart_id

                    # nipur code end
                    messages.success(request, "You have successfully logged in")
                    valuenext =valuenext.strip('/')
                    context= {'valuenext': valuenext}
                    return redirect('checkout')
                    # return redirect(valuenext)
                else:
                    messages.warning(request,"Wrong Credentials")
                    # return render(request,'base.html',{})
                    # nipur code start
                    return redirect('home')
            else:
                return HttpResponse('<script>alert(here the recaptcha  is not valid);</script>')

    else:
        # return render(request, 'base.html', {})
        # nipur code start
        return redirect('home')


def mobile_verification_otp(request):
    try:
        if User_Check.objects.get(user_check=request.user).check_mobile:
            return redirect('profile_pan_verification')
    except:
        pass
    mobile_number = []
    try:
        mobile_number = request.user.profile.phone_number
    except:
        pass
    return render(request, 'reg_otp.html', {'mobile_number':mobile_number})


def new_reg_user_login(request):
    # AG :: Redirect to edit profile if mobile number is already verified
    try:
        if User_Check.objects.get(user_check=request.user).check_mobile:
            return redirect('profile_pan_verification')
    except:
        pass

    phone = []
    try:
        # phone = request.POST.get('mobile')
        phone = request.user.profile.phone_number
    except:
        pass

    if request.method == 'POST':
        if 'mobile' in request.POST and 'otp' in request.POST:
            mobile = phone
            mobile_otp = request.POST.get('otp')
            if not mobile_otp:
                messages.warning(request,"OTP is wrong/expired")
                # return redirect('home')
                return render(request, 'reg_otp.html', {'mobile_number': phone})
                # return HttpResponse('<script>alert(OTP is wrong/expired);</script>')

            try:
                prof = Profile.objects.get(phone_number= mobile)
                email = prof.user.username
            except ObjectDoesNotExist:
                messages.warning(request,"Mobile number is not valid")
                # return HttpResponse('<script>alert(Mobile number is not valid);</script>')
                # return redirect('home')
                return render(request, 'reg_otp.html', {'mobile_number': phone})

            keygen = generateKey()
            key = base64.b32encode(keygen.returnValue(mobile).encode())  # Generating Key
            OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model

            if OTP.verify(mobile_otp):  # Verifying the OTP
                 
                user = User.objects.get(email=email)
                check = User_Check.objects.get(user_check=user)
                check.check_mobile = True
                check.save()

                valuenext = request.POST.get('next')
                if user is not None and valuenext=='':
                    check = User_Check.objects.get(user_check=user)
                    check.check_mobile = True
                    check.user_check
                    check.save()
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                    context= {'valuenext': valuenext}             # next value is being kept insidecontext
                    # return redirect('home')
                    return render(request, 'reg_otp.html', {'mobile_number': phone})
                elif user is not None and valuenext !='':
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                    messages.success(request, "You have successfully logged in")
                    valuenext =valuenext.strip('/')
                    context= {'valuenext': valuenext}
                    return redirect('checkout')
                else:
                    return render(request, 'reg_otp.html', {'mobile_number': phone})
            return render(request, 'reg_otp.html', {'mobile_number': phone})
    else:
        return render(request, 'reg_otp.html', {'mobile_number': phone})



# This class returns the string needed to generate the key
class generateKey:
    @staticmethod
    def returnValue(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"

@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        try:
            mobile = request.POST['mobile']
            try:
                prof = Profile.objects.filter(phone_number= str(mobile)).first()
                keygen = generateKey()
                time_elapsed = datetime.now().astimezone() - prof.last_otp_time
                
                if time_elapsed > timedelta(1):
                    prof.otp_count = 1
                    prof.last_otp_time = datetime.now()
                else:
                    if prof.otp_count >= 3:
                        response = JsonResponse({"message": "OTP Limit is exceeded for today"})
                        response.status_code = 400
                        return response
                    else:     
                        prof.otp_count = prof.otp_count + 1
               
                key = base64.b32encode(keygen.returnValue(mobile).encode())  # Key is generated
                OTP = pyotp.TOTP(key, interval= EXPIRY_TIME)  # TOTP Model for OTP is created
                sendsms("msg_otp", user_mobile_number = "+91" + str(mobile), otp = OTP.now(), otp_time = "30")
                prof.save()
                return JsonResponse({'mobile': "OTP Has been send"}, status=200)                                               #getting username from profile-->user and saving under email
            except ObjectDoesNotExist:
                response = JsonResponse({"message": "Mobile Number - " + str(mobile) + " is not registered with any advisor.\nPlease check and type again."})
                response.status_code = 400
                return response
        except:
            response = JsonResponse({"message": "Mobile Number - " + str(mobile) + " is not registered with any advisor.\nKindly re-check and type again."})
            response.status_code = 400
            return response



#
# def new_sign_up(request):
#     if request.method == 'GET':
#         profile_form = ProfileForm()
#         create_form = CreateUserForm()
#         kyc = KycForm()
#         bank_form = BankAccountDetailsForm()
#
#     else:
#
#         form = ProfileForm(request.POST) # Bind Form data
#
#         if form.is_valid():
#             pass
#             #content = form.cleaned_data['content']
#             #created_at = form.cleaned_data['created_at']
#             #post = m.Post.objects.create(content=content,created_at=created_at)
#             #return HttpResponseRedirect(reverse('reg',kwargs={'post_id': post.id}))
#     context = {'form': kyc, 'bank_form': bank_form , 'profile_form':profile_form, 'create_form' : create_form}
#     return render(request, 'registration1.html',context)
#

def bank_check_fn(request):
    '''
    This function will mark User's Bank Account Details as Verified when this function is called.
    '''
    try:
        bank_check_qs = User_Check.objects.get(user_check=request.user)
        bank_check_qs.check_distributors_name_in_bank_account = True
        bank_check_qs.check_bank_name = True
        bank_check_qs.check_account_number = True
        bank_check_qs.check_ifsc_code = True
        bank_check_qs.check_branch_name = True
        bank_check_qs.check_cheque_photo = True
        bank_check_qs.save()
        return True
    except:
        pass
    return False

def pan_check_fn(request):
    '''
    This function will mark User's Bank Account Details as Verified when this function is called.
    '''
    try:
        pan_check_qs = User_Check.objects.get(user_check=request.user)
        pan_check_qs.check_pan_number = True
        pan_check_qs.check_pan_file = True
        pan_check_qs.save()
        return True
    except:
        pass
    return False

'''========================
# Sign Up Function - This is signup function , if a user is signing up , necessary details need to be posted.
===========================
'''
def new_sign_up(request):
    user = User
    context = {}
    kyc = KycForm()
    bank_form = BankAccountDetailsForm()
    if request.method =='POST':
        postData= request.POST
        firstName = postData.get('firstname')
        lastName = postData.get('lastname')
        email = postData.get('email')
        check_box_value = postData.get('email_check_box',None)
        phone = postData.get('phone')
        # if phone number exists:
        try:
            Profile.objects.get(phone_number=phone)
            messages.error(request, "Mobile Number Already Exist")
            return redirect('register')
        except:
            pass
        # if we found invalid phone number
        try:
            phone = str(int(phone))
        except:
            phone = random.randrange(1111111111, 9999999999)
            phone = "0" + str(phone)
        if check_box_value == 'no':
            phone = postData.get('phone')
            # if we found no/blank phone number
            if phone == '':
                phone = random.randrange(1111111111, 9999999999)
            email = phone + '@mywebstay.com'
        email = email.lower()
        # if email number exists:
        try:
            User.objects.get(email=email)
            messages.error(request, "Email Already Exist")
            return redirect('register')
        except:
            pass
        # Checking email id pattern
        try:
            email_status = False
            if "@" in email:
                if "." in email:
                    if " " not in email:
                        email_status = True
            if not email_status:
                email = phone + '@mywebstay.com'
        except:
            pass
        password = postData.get('password')
        confirmpassword = postData.get('confirmPassword')
        referral_code = postData.get('referral_code')
        PAN = postData.get('pan_number')
        rc = ReferralCode.get_referal_code(referral_code)
        if True:
            if not firstName or not email or not phone  or not password or not referral_code:
                messages.error(request, "Form is Empty ")
            else:
                if rc:
                    try:
                        referral_mobile_number = Profile.objects.get(user = rc.user_id).phone_number
                    except:
                        referral_mobile_number = "0"

                    if password == confirmpassword:
                        user = user(username = email, email=email)
                        user.set_password(password)
                        user.save()
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        if user.save:
                            profile = Profile.objects.get(user= request.user)
                            profile.first_name = postData.get('firstname')
                            profile.last_name =postData.get('lastname')
                            profile.date_of_birth=postData.get('birthday')
                            profile.co_applicant=postData.get('co_applicant')
                            profile.blood_group=postData.get('blood_group')
                            profile.blood_rh_factor=postData.get('blood_rh_factor')
                            profile.phone_number=postData.get('phone')
                            profile.gender=postData.get('gender')
                            profile.save()
                            user_check = User_Check(user_check = request.user)
                            user_check.save()

    # This code tells basically the generation of referral code with the help of userid, profile id and status.
                            userID = profile.id
                            UplineCode = rc.referral_code
                            PAN = PAN
                            try:
                                lastname = profile.last_name
                            except:
                                lastname = "6"
                            final = genReferralCode(userID,UplineCode,PAN,lastname)
                            position = postData.get('position')
                            rfc = ReferralCode(user_id=request.user,
                                referal_id = profile.id, referral_code=final,referal_by = rc.user_id,status=False,position = position)
                            position = rfc.position
                            if not ReferralCode.objects.filter(parent_id = rc.user_id,position = position).exists() :
                                rfc.parent_id = rc.user_id
                            else:
                                result = puting_parent_id(rc,rfc,position)
                            rfc.save()
                            code = get_object_or_404(ReferralCode, user_id=request.user)
                            profile.reference_user_id = code.id
                            profile.save()
                        else:
                            messages.error(request, "You are not registerd")
                        if profile.save:
                            addres_query = Address(user= request.user,
                                                    house_number=postData.get('house'),
                                                    address_line= postData.get('address2'),
                                                    Landmark= postData.get('landmark'),
                                                    city= postData.get('city'),
                                                    state_id = postData.get('state'),
                                                    street= postData.get('street'),
                                                    # country= postData.get(),
                                                    pin= postData.get('pincode'),
                                                    mobile= postData.get('phone'),
                                                    alternate_mobile= postData.get('altphone'),
                                                    default=True
                                                    )
                            addres_query.save()
                            profile.shipping_address = addres_query
                            profile.save()
                            try:
                                if addres_query.save:
                                    kyc = KycForm(request.POST, request.FILES)
                                    if kyc.is_valid():
                                        if request.POST["manual_verify"] == "Yes":
                                            kyc_ = kyc.save(commit=False)
                                            kyc_.kyc_user= request.user
                                            try:
                                                manual = ManualVerification.objects.create(kyc_user=request.user, pan_number=kyc_.pan_number, pan_file=kyc_.pan_file, id_proof_type=kyc_.id_proof_type,id_proof_file=kyc_.id_proof_file,address_proof_type=kyc_.address_proof_type,address_proof_file=kyc_.address_proof_file)
                                                manual.save()
                                                kyc_.save()
                                            except:
                                                manual = ManualVerification.objects.get(kyc_user=request.user)
                                                manual.pan_number = kyc_.pan_number
                                                manual.pan_file = kyc_.pan_file
                                                manual.id_proof_type = kyc_.id_proof_type
                                                manual.id_proof_file = kyc_.id_proof_file
                                                manual.address_proof_type = kyc_.address_proof_type
                                                manual.address_proof_file = kyc_.address_proof_file
                                                manual.save()
                                                kyc_.save()
                                        else:
                                            post = kyc.save(commit=False)
                                            post.kyc_user= request.user
                                            pan_number = post.pan_number
                                            try:
                                                # img_path = post.pan_file.path
                                                img_path = post.pan_file.url
                                                print(img_path)
                                            except:
                                                img_path = None

                                            pan_name = post.pan_name
                                            response_kyc = Pan_verification(request,img_path,pan_number)
                                            if response_kyc == 400:
                                                messages.error(request,"Images not present in Identity, Update now")
                                                return redirect("edit_profile")
                                            try:
                                                error = response_kyc["error"]
                                                post.kyc_done = False
                                                post.save()
                                                messages.error(request,error)
                                                return redirect("edit_profile")
                                            except:
                                                if response_kyc["verified"] == "True":
                                                    post.kyc_done = True
                                                    post.save()
                                                    pan_check_fn(request)
                                                    messages.success(request, kyc_pan_pass_message)
                                                else:
                                                    post.kyc_done = False
                                                    post.save()
                                                    messages.error(request,"Sorry KYC Verification Failed")
                                    else:
                                        pass
                                    if post.save:
                                        bank_form = BankAccountDetailsForm(request.POST, request.FILES)
                                        if bank_form.is_valid():
                                            post_bank = bank_form.save(commit=False)
                                            post_bank.bank_account_user = request.user
                                            post_bank.save()
                                            post_bank_ifcs = bank_form.cleaned_data['ifsc_code']
                                            post_bank_account_number = bank_form.cleaned_data['account_number']
                                            post_bank_name_in_bank = bank_form.cleaned_data['distributors_name_in_bank_account']
                                            
                                             
                                            # Bank_proof_api(post_bank_ifcs,post_bank_account_number,post_bank_user_name,post_bank_user_number)
                                            res =  Bank_proof_api(request,post_bank_ifcs,post_bank_account_number,post_bank_name_in_bank )
                                            try:
                                                result = res["result"]
                                                if result["active"] == 'yes':
                                                    post_bank.account_number = post_bank_account_number
                                                    post_bank.ifsc_code = post_bank_ifcs

                                                    post_bank.save()
                                                    bank_check_fn(request)
                                                    messages.success(
                                                        request, "Bank Account is verified."
                                                        )
                                                else:
                                                    messages.error(
                                                        request, "Bank credentials are not correct"
                                                        )
                                                    return redirect("register")
                                            except:
                                                 
                                                msg = "ERROR! Bank Account is not verified"
                                                messages.error(
                                                    request, f"{msg}"
                                                    )
                                                return redirect("register")
                                            #This code is to send an email and sms.
                                            from mlm_admin.views import sendemail
                                            result = sendemail(profile,final)
                                            phone = postData.get('phone')
                                            # result = sendsms(phone,final)
                                            result = sendsms("msg_welcome", user_mobile_number = "+91" + str(phone), ARN = final, password = password)
                                           
                                            result_sponsor = sendsms("msg_welcome_sponsor", user_mobile_number = "+91" + str(referral_mobile_number), ARN = final, referee_name = (str(firstName) + " " + str(lastName)))
# <-----------------------------------------------------------End email send message --------------------------------------------------------------------------------------------->
                                            # return render(request,'reg_otp.html',{'mobile_number':phone})
                                            # return redirect('home')
                                            return HttpResponseRedirect(reverse('mobile_verification',kwargs={'mobile_number':phone}))

                                    else:
                                        messages.success(
                                            request,"You are signed In."
                                        )
                                        from mlm_admin.views import sendemail
                                        result = sendemail(profile,final)
                                        phone = postData.get('phone')
                                        # result = sendsms(phone,final)
                                        result = sendsms("msg_welcome", user_mobile_number = "+91" + str(phone), ARN = final, password = password)
                                        # if result == True:
                                        #     check = User_Check.objects.get(user_check = request.user)
                                        #     check.check_phone_number = True
                                        #     check.save()
                                        result_sponsor = sendsms("msg_welcome_sponsor", user_mobile_number = "+91" + str(referral_mobile_number), ARN = final, referee_name = (str(firstName) + " " + str(lastName)))
# <-----------------------------------------------------------End email send message --------------------------------------------------------------------------------------------->

                                        # return render(request,'reg_otp.html',{'mobile_number':phone})
                                        # return redirect('home') 
                                        return HttpResponseRedirect(reverse('mobile_verification',kwargs={'mobile_number':phone}))

                            except:
                                messages.success(
                                    request,"You are signed In."
                                )
                                from mlm_admin.views import sendemail
                                try:
                                    result = sendemail(profile,final)
                                    phone = postData.get('phone')
                                    # result = sendsms(phone,final)
                                    result = sendsms("msg_welcome", user_mobile_number = "+91" + str(phone), ARN = final, password = password)
                                     
                                    result_sponsor = sendsms("msg_welcome_sponsor", user_mobile_number = "+91" + str(referral_mobile_number), ARN = final, referee_name = (str(firstName) + " " + str(lastName)))
                                except:
                                    pass
# <-----------------------------------------------------------End email send message --------------------------------------------------------------------------------------------->

                                # return render(request,'reg_otp.html',{'mobile_number':phone})
                                # return redirect('home')
                                user_check_check_mobile = False
                                user_check_check_pan = False
                                try:
                                    user_check_check_mobile = User_Check.objects.get(user_check=request.user).check_mobile
                                    user_check_check_pan = User_Check.objects.get(user_check=request.user).check_pan_number
                                except:
                                    pass

                                if not user_check_check_mobile:
                                    return redirect('mobile_verification')
                                if not user_check_check_pan:
                                    return redirect('profile_pan_verification')
                                # return HttpResponseRedirect(reverse('mobile_verification',kwargs={'mobile_number':phone}))
                                # return redirect('mobile_verification')

                    else:
                        messages.error(request, "password not match ")
                else:
                    messages.error(request, "Wrong ReferralCode ")


    state = AdminState.objects.filter()
    if 'refid' in request.GET:
        refid = request.GET.get('refid', None)
        position = None
        if refid:
            refid_position = ReferralCode.objects.filter(referral_code=refid)
            if refid_position:
                refid_position = refid_position[0].position
                if refid_position == "LEFT":
                    position = "RIGHT"
                if refid_position == "RIGHT":
                    position = "LEFT"
        if 'position' in request.GET:
            position = request.GET.get('position', None)
        context={'form':kyc,'bank_form':bank_form,'title':'Auretics Distributor Registration Form','refid':refid,'position':position,'state':state}
    else:
        context={'form':kyc, 'bank_form':bank_form,'title':'Auretics Distributor Registration Form','state':state}
    # return render(request, 'registration1.html', context)
    return render(request, 'registration.html', context)


# return render(request, 'registration1.html', {
#         'form': form,
#     })


def profile_pan(request):
    try:
        check_user_qs = User_Check.objects.get(user_check=request.user)
        if check_user_qs.check_pan_number:
            return redirect('profile_bank_verification')
    except:
        pass

    kyc = KycForm()
    profile = Profile.objects.get(user=request.user)

    try:
        kyc_qs = Kyc.objects.get(kyc_user=request.user)
    except:
        kyc_qs = Objectify()
        kyc_qs.pan_number = ''
        kyc_qs.pan_file = ''
        kyc_qs.id_proof_type = ''
        kyc_qs.id_proof_file = ''
        kyc_qs.address_proof_type = ''
        kyc_qs.address_proof_file = ''
    
    if request.method == "POST":
        kyc_pan_number = request.POST.get('pan_number', '')
        kyc_pan_file = request.FILES.get('pan_file', '')
        kyc_id_proof_type = request.POST.get('id_proof_type', '')
        kyc_id_proof_file = request.FILES.get('id_proof_file', '')
        kyc_address_proof_type = request.POST.get('address_proof_type', '')
        kyc_address_proof_file = request.FILES.get('address_proof_file', '')

        if check_user_qs.check_pan_number:
            kyc_pan_number = kyc_qs.pan_number
        if check_user_qs.check_pan_file:
            kyc_pan_file = kyc_qs.pan_file
        if check_user_qs.check_id_proof_type:
            kyc_id_proof_type = kyc_qs.id_proof_type
        if check_user_qs.check_id_proof_file:
            kyc_id_proof_file = kyc_qs.id_proof_file
        if check_user_qs.check_address_proof_type:
            kyc_address_proof_type = kyc_qs.address_proof_type
        if check_user_qs.check_address_proof_file:
            kyc_address_proof_file = kyc_qs.address_proof_file

        kyc_form = Kyc.objects.filter(kyc_user=request.user).update(pan_number=kyc_pan_number, id_proof_type=kyc_id_proof_type,
                                                            address_proof_type=kyc_address_proof_type)

        kyc = KycForm(request.POST, request.FILES)
        if kyc.is_valid():
            manual_verify_var = request.POST.get('manual_verify', False)
            if manual_verify_var:
                post = kyc.save(commit=False)
                try:
                    post.kyc_user= request.user
                    post.save()
                except:
                    pass

                try:
                    manual = ManualVerification.objects.create(kyc_user=request.user,
                                                               pan_number=post.pan_number,
                                                               pan_file=post.pan_file,
                                                               id_proof_type=post.id_proof_type,
                                                               id_proof_file=post.id_proof_file,
                                                               address_proof_type=post.address_proof_type,
                                                               address_proof_file=post.address_proof_file)
                    manual.save()

                except:
                    manual = ManualVerification.objects.get(kyc_user=request.user)
                    manual.pan_number = post.pan_number
                    manual.pan_file = post.pan_file
                    manual.id_proof_type = post.id_proof_type
                    manual.id_proof_file = post.id_proof_file
                    manual.address_proof_type = post.address_proof_type
                    manual.address_proof_file = post.address_proof_file
                    manual.save()

            else:
                post = kyc.save(commit=False)
                # post = kyc.objects.get(commit=False)
                post.kyc_user= request.user
                pan_number = post.pan_number
                try:
                    # img_path = post.pan_file.path
                    img_path = post.pan_file.url
                    print(img_path)
                except:
                    img_path = None

                pan_name = post.pan_name

                response_kyc = Pan_verification(request,img_path,pan_number)
                if response_kyc == 400:
                    messages.error(request,"Images not present in Identity, Update now")
                    return redirect("edit_profile")
                try:
                    error = response_kyc["error"]
                    post.kyc_done = False
                    try:
                        post.save()
                    except:
                        pass
                    messages.error(request,error)
                    # return redirect("edit_profile")
                except:
                    if response_kyc["verified"] == "True":
                        post.kyc_done = True
                        post.save()
                        pan_check_fn(request)
                        messages.success(request, "Congrats KYC verified")
                print (post)
            if post.save:
                return redirect('profile_bank_verification')
            else:
                messages.error(request,"Pan information did not save")
        else:
            messages.error(request,"Information is not valid") 
    kyc = KycForm()
    context = {'form':kyc,
               'kyc_qs':kyc_qs,}
    return render(request,'prof_pan.html', context)



def profile_bank(request):
    try:
        check_user_qs = User_Check.objects.get(user_check=request.user)
        if check_user_qs.check_account_number:
            return redirect('edit_profile')
    except:
        pass

    bank_form = BankAccountDetailsForm()

    try:
        bank_qs = BankAccountDetails.objects.get(bank_account_user=request.user)
        cheque_photo = bank_qs.cheque_photo
    except:
        bank_qs = Objectify()
        bank_qs.bank_name = ''
        bank_qs.account_number = ''
        bank_qs.ifsc_code = ''
        bank_qs.branch_name = ''
        bank_qs.cheque_photo = ''
        cheque_photo = False

    if request.method == "POST":
        bank_distributors_name_in_bank_account = request.POST.get('distributors_name_in_bank_account', '')
        bank_bank_name = request.POST.get('bank_name', '')
        bank_account_number = request.POST.get('account_number', '')
        bank_ifsc_code = request.POST.get('ifsc_code', '')
        bank_branch_name = request.POST.get('branch_name', '')
        bank_cheque_photo = request.FILES.get('cheque_photo', '')

        if check_user_qs.check_bank_name:
            bank_bank_name = bank_qs.bank_name
        if check_user_qs.check_account_number:
            bank_account_number = bank_qs.account_number
        if check_user_qs.check_ifsc_code:
            bank_ifsc_code = bank_qs.ifsc_code
        if check_user_qs.check_branch_name:
            bank_branch_name = bank_qs.branch_name
        if check_user_qs.check_cheque_photo:
            bank_cheque_photo = bank_qs.cheque_photo

        if bank_qs:
            # bank_form = BankAccountDetails.objects.filter(bank_account_user = user).update(distributors_name_in_bank_account = kyc_d)
            # bank_form.save()
            bank_form = BankAccountDetailsForm(instance=bank_qs, data=request.POST, files=(request.FILES or None), )
            if bank_form.is_valid():
                post_bank = bank_form.save(commit=False)
                post_bank.bank_account_user = request.user
                
                post_bank_ifcs = bank_form.cleaned_data['ifsc_code']
                post_bank_account_number = bank_form.cleaned_data['account_number']
                post_bank_name_in_bank = bank_form.cleaned_data['distributors_name_in_bank_account']
                                             
                # Bank_proof_api(post_bank_ifcs,post_bank_account_number,post_bank_user_name,post_bank_user_number)
                res =  Bank_proof_api(request,post_bank_ifcs,post_bank_account_number,post_bank_name_in_bank )
                try:
                    result = res["result"]
                    if result["active"] == 'yes':
                        post_bank.account_number = post_bank_account_number
                        post_bank.ifsc_code = post_bank_ifcs
                        post_bank.save()
                        bank_check_fn(request)
                        messages.success(
                            request, "Bank Account is verified."
                            )

                    else:
                        messages.error(
                            request, "Bank credentials are not correct"
                            )
                        return redirect("profile_bank_verificationk")
                except:

                    msg = "ERROR! Bank Account is not verified"
                    messages.error(
                        request, f"{msg}"
                        )
                
            else:
                return HttpResponse('<h1>' + str(bank_form.errors) + '</h1>')
            form = BankAccountDetails.objects.filter(bank_account_user = request.user).update(distributors_name_in_bank_account = post_bank.distributors_name_in_bank_account,
                            bank_name = post_bank.bank_name,account_number = post_bank.account_number,ifsc_code = post_bank.ifsc_code,branch_name = post_bank.branch_name
                            )

        else:
            bank_form = BankAccountDetailsForm_for_user(data=request.POST, files=(request.FILES or None), )
            if bank_form.is_valid():
                databankform = bank_form.save(commit=False)
                databankform.bank_account_user = request.user
                databankform.save()
            else:
                print(bank_form.errors)
                return HttpResponse('<h1>' + bank_form.errors + '</h1>')

            #This code is to send an email and sms.
                 # <-----------------------------------------------------------End email send message --------------------------------------------------------------------------------------------->
            # return render(request,'reg_otp.html',{'mobile_number':phone})
            # return redirect('home')
            profile = Profile.objects.get(user=request.user)
            phone = profile.phone_number 
            return redirect('mobile_verification')
        return redirect('mobile_verification')
    context = {'bank_form':bank_form,
               'bank_qs':bank_qs,}
    return render(request,'prof_bank.html',context)

# ajax request
def validate_data(request):
    email = request.GET.get('email', None)
    firstname = request.GET.get('firstname', None)
    email = email.lower()
    data = {
        'is_taken': User.objects.filter(email__iexact=email).exists(),
        'name_is_taken': User.objects.filter(username__iexact=firstname).exists()
    }
    return JsonResponse(data)



# This is for user creation with the required fields as under first name, last name and so on ..
def sign_up(request):
    form = UserCreationForm()
    if request.method == 'GET':
        return render(request, 'base.html')
    else:
    # if request.method == 'POST':
        user = User
        postData= request.POST
        firstName = postData.get('firstname')
        lastName = postData.get('lastname')
        email = postData.get('email')
        phone = postData.get('phone')
        referral_code = postData.get('referral_code')
        password = postData.get('password')
        confirmpassword = postData.get('confirmpassword')

# wallets are owned by users.
        wallet = Wallet.objects.create(user=request.user)
        form = UserCreationForm(data=request.POST)

        rc = ReferralCode.get_referal_code(referral_code)
        if rc:
            if password==confirmpassword:
                # print ('working')
                user = user(username = firstName, email=email)
                user.set_password(password)
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                profile = Profile.objects.get(user = request.user)
                rfc = ReferralCode(user_id=request.user,
                        referal_id = profile.id, referral_code="12346")
                rfc.save()
                code = get_object_or_404(ReferralCode, user_id=request.user)
                profile.reference_user_id = code.id
                profile.save()
                check_data = User_Check(user_check = user)
                check_data.save()
                messages.success(
                    request, "You're now a user! You've been signed in, too."
                    )
                return HttpResponseRedirect(reverse('home'))
            else:
                messages.error(request, "password not match ")
        else:
            messages.error(request, "Wrong ReferralCode ")
    return render(request, 'base.html', {'form':form, 'hello':'Hello'})


def logoutUser(request):
    try:
        data = request.session['cart_id']
    except:
        data = []
    logout(request)
    cart_items =CartItem.objects.filter(cart_id = data)
    # del request.session['cart_id']
    cart.get_all_cart_items(request)
    cart_id = request.session['cart_id']
    for i in cart_items:
        item = CartItem(cart_id = cart_id,
                        price = i.price,
                        discount_price=i.discount_price,
                        business_value = i.business_value,
                        point_value = i.point_value,
                        quantity = i.quantity,
                        in_stock = i.in_stock,
                        product = i.product,)
        item.save()
    return redirect('home')# return HttpResponseRedirect(reverse('home'))

@login_required
def profile(request):
    """Display User Profile"""
    user = request.user
    profile = request.user.profile
    referal_code = get_object_or_404(ReferralCode, user_id = user)
    if settings.WALLET == "ON":
        wallet = Wallet.objects.get_or_create(user=request.user)
        parms_with_wallet = {
        'profile': profile,'referalForm':referal_code,
        'title':'Profile', 'wallet':wallet
        }
        return render(request, 'profile.html',parms_with_wallet)

    parms_without_wallet = {
        'profile': profile,'referalForm':referal_code,
        'title':'Profile'
        }

    return render(request, 'profile.html',parms_without_wallet)


from mlm_admin.forms import *
@login_required
def edit_profile(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    check_user_qs = get_object_or_404(User_Check, user_check=user)

    # if request.method == "POST":
    #     kyc = KycForm(request.POST, request.FILES)
    #     if kyc.is_valid():
    #         manual_verify_var = request.POST.get('manual_verify', False)
    #         if manual_verify_var:
    #             kyc_ = kyc.save(commit=False)
    #             try:
    #                 kyc_.kyc_user= request.user
    #                 kyc_.save()
    #             except:
    #                 pass

    #             try:
    #                 manual = ManualVerification.objects.create(kyc_user=request.user,
    #                                                            pan_number=kyc_.pan_number,
    #                                                            pan_file=kyc_.pan_file,
    #                                                            id_proof_type=kyc_.id_proof_type,
    #                                                            id_proof_file=kyc_.id_proof_file,
    #                                                            address_proof_type=kyc_.address_proof_type,
    #                                                            address_proof_file=kyc_.address_proof_file)
    #                 manual.save()

    #             except:
    #                 manual = ManualVerification.objects.get(kyc_user=request.user)
    #                 manual.pan_number = kyc_.pan_number
    #                 manual.pan_file = kyc_.pan_file
    #                 manual.id_proof_type = kyc_.id_proof_type
    #                 manual.id_proof_file = kyc_.id_proof_file
    #                 manual.address_proof_type = kyc_.address_proof_type
    #                 manual.address_proof_file = kyc_.address_proof_file
    #                 manual.save()

    #         else:
    #             post = kyc.save(commit=False)
    #             # post = kyc.objects.get(commit=False)
    #             post.kyc_user= request.user
    #             pan_number = post.pan_number
    #             try:
    #                 # img_path = post.pan_file.path
    #                 img_path = post.pan_file.url
    #                 print(img_path)
    #             except:
    #                 img_path = None

    #             pan_name = post.pan_name

    #             response_kyc = Pan_verification(request,img_path,pan_number)
    #             if response_kyc == 400:
    #                 messages.error(request,"Images not present in Identity, Update now")
    #                 return redirect("edit_profile")
    #             try:
    #                 error = response_kyc["error"]
    #                 post.kyc_done = False
    #                 try:
    #                     post.save()
    #                 except:
    #                     pass
    #                 messages.error(request,error)
    #                 # return redirect("edit_profile")
    #             except:
    #                 if response_kyc["verified"] == "True":
    #                     post.kyc_done = True
    #                     post.save()
    #                     pan_check_fn(request)
    #                     messages.success(request, "Congrats KYC verified")
    #             print (post)


    #     try:
    #         bank_qs=get_object_or_404(BankAccountDetails, bank_account_user = user)
    #         # cheque_photo = bank_qs.cheque_photo
             
    #     except:
    #         bank_qs = False
    #         cheque_photo = False
    #         # bank_form = BankAccountDetailsForm_for_user()
    #     if bank_qs:
    #         # bank_form = BankAccountDetails.objects.filter(bank_account_user = user).update(distributors_name_in_bank_account = kyc_d)
    #         # bank_form.save()
    #         bank_form = BankAccountDetailsForm(instance=bank_qs, data=request.POST, files=(request.FILES or None), )
    #         if bank_form.is_valid():
    #             post_bank = bank_form.save(commit=False)
    #             post_bank.bank_account_user = request.user
                
    #             post_bank_ifcs = bank_form.cleaned_data['ifsc_code']
    #             post_bank_account_number = bank_form.cleaned_data['account_number']
    #             post_bank_name_in_bank = bank_form.cleaned_data['distributors_name_in_bank_account']
                                            
                                             
    #             # Bank_proof_api(post_bank_ifcs,post_bank_account_number,post_bank_user_name,post_bank_user_number)
    #             res =  Bank_proof_api(request,post_bank_ifcs,post_bank_account_number,post_bank_name_in_bank )
    #             try:
    #                 result = res["result"]
    #                 if result["active"] == 'yes':
    #                     post_bank.account_number = post_bank_account_number
    #                     post_bank.ifsc_code = post_bank_ifcs

                         
    #                     post_bank.save()
    #                     bank_check_fn(request)
    #                     messages.success(
    #                         request, "Bank Account is verified."
    #                         )

    #                 else:
    #                     messages.error(
    #                         request, "Bank credentials are not correct"
    #                         )
    #                     return redirect("register")
    #             except:

    #                 msg = "ERROR! Bank Account is not verified"
    #                 messages.error(
    #                     request, f"{msg}"
    #                     )
                
    #         else:
    #             return HttpResponse('<h1>' + str(bank_form.errors) + '</h1>')
    #         form = BankAccountDetails.objects.filter(bank_account_user = user).update(distributors_name_in_bank_account = post_bank.distributors_name_in_bank_account,
    #                         bank_name = post_bank.bank_name,account_number = post_bank.account_number,ifsc_code = post_bank.ifsc_code,branch_name = post_bank.branch_name
    #                         )

    #     else:
    #         bank_form = BankAccountDetailsForm_for_user(data=request.POST, files=(request.FILES or None), )
    #         if bank_form.is_valid():
    #             databankform = bank_form.save(commit=False)
    #             databankform.bank_account_user = user
    #             databankform.save()
    #         else:
    #             print(bank_form.errors)
    #             return HttpResponse('<h1>' + bank_form.errors + '</h1>')

    # print("try")
    # try:
    #     kyc_qs = get_object_or_404(Kyc, kyc_user = user)
    #     pan_file = kyc_qs.pan_file
    #     id_proof_file = kyc_qs.id_proof_file
    #     address_proof_file = kyc_qs.address_proof_file
    #     if request.method == "POST":
    #         kyc = KycForm(request.POST, request.FILES)
    #         if kyc.is_valid():
    #             if request.POST["manual_verify"] == "Yes":
    #                 kyc_ = kyc.save(commit=False)
    #                 try:
    #                     kyc_.kyc_user= request.user
    #                     kyc_.save()
    #                 except:
    #                     pass

    #                 try:
    #                     manual = ManualVerification.objects.create(kyc_user=request.user,
    #                                                                pan_number=kyc_.pan_number,
    #                                                                pan_file=kyc_.pan_file,
    #                                                                id_proof_type=kyc_.id_proof_type,
    #                                                                id_proof_file=kyc_.id_proof_file,
    #                                                                address_proof_type=kyc_.address_proof_type,
    #                                                                address_proof_file=kyc_.address_proof_file)
    #                     manual.save()
    #                     kyc_.save()
    #                 except:
    #                     manual = ManualVerification.objects.get(kyc_user=request.user)
    #                     manual.pan_number = kyc_.pan_number
    #                     manual.pan_file = kyc_.pan_file
    #                     manual.id_proof_type = kyc_.id_proof_type
    #                     manual.id_proof_file = kyc_.id_proof_file
    #                     manual.address_proof_type = kyc_.address_proof_type
    #                     manual.address_proof_file = kyc_.address_proof_file
    #                     manual.save()
    #                     kyc_.save()
    #             else:
    #                 post = kyc.save(commit=False)
    #                 post.kyc_user= request.user
    #                 pan_number = post.pan_number
    #                 try:
    #                     # img_path = post.pan_file.path
    #                     img_path = post.pan_file.url
    #                     print(img_path)
    #                 except:
    #                     img_path = None

    #                 pan_name = post.pan_name

    #                 response_kyc = Pan_verification(request,img_path,pan_number)
    #                 if response_kyc == 400:
    #                     messages.error(request,"Images not present in Identity, Update now")
    #                     return redirect("edit_profile")
    #                 try:
    #                     error = response_kyc["error"]
    #                     post.kyc_done = False
    #                     post.save()
    #                     messages.error(request,error)
    #                     # return redirect("edit_profile")
    #                 except:
    #                     if response_kyc["verified"] == "True":
    #                         post.kyc_done = True
    #                         post.save()
    #                         pan_check_fn(request)
    #                         messages.success(request, "Congrats KYC verified")
    #                     else:
    #                         post.kyc_done = False
    #                         post.save()
    #                         messages.error(request,kyc_pan_fail_message)
    #                 # print (post)
    #     kyc_qs = Objectify()
    #     kyc_qs.object_is = False
    #     pan_file = False
    #     id_proof_file = False
    #     address_proof_file = False
    #     form = KycForm()
    # except:
    #     pass

    # # try:
    #     # bank_qs=get_object_or_404(BankAccountDetails, bank_account_user = user)
    # bank_qs = BankAccountDetails.objects.update_or_create(bank_account_user=user, defaults={'bank_account_user':user})[0]
    # # except:
    # #     bank_qs = False
    # try:
    #     cheque_photo = bank_qs.cheque_photo
    # except:
    #     cheque_photo = False
    # try:
    #     bank_form = BankAccountDetailsForm_for_user(instance=bank_qs)
    # except:
    #     bank_form = BankAccountDetailsForm_for_user()

    # address_qs = get_object_or_404(Address, user=user, address_type='B')
    # try:
    #     kyc_qs = Kyc.objects.get(kyc_user = user)
    # except:
    #     kyc_qs = Objectify()
    #     kyc_qs.object_is = False
    #     kyc_qs.pan_file = False
    #     kyc_qs.id_proof_file = False
    #     kyc_qs.address_proof_file = False
    #     kyc_qs.pan_number = False
    #     kyc_qs.pan_file = False
    #     kyc_qs.id_proof_type = False
    #     kyc_qs.id_proof_file = False
    #     kyc_qs.address_proof_type = False
    #     kyc_qs.address_proof_file = False

    # try:
    #     form = KycForm(instance=kyc_qs)
    # except:
    #     form = KycForm()

    # pan_file = kyc_qs.pan_file
    # id_proof_file = kyc_qs.id_proof_file
    # address_proof_file = kyc_qs.address_proof_file

    # <-----------------------------------------------------------------for changing data in reqistration field ----------------------------------->   if request.method == 'POST':
    
    address_qs = get_object_or_404(Address, user=user, address_type='B')
    
    if request.method == 'POST':
        profile_firstname = request.POST.get('firstname',None)
        profile_lastname = request.POST.get('lastname',None)
        profile_birthday = request.POST.get('birthday',None)
        profile_co_applicant = request.POST.get('co_applicant',None)
        profile_blood_group = request.POST.get('blood_group',None)
        profile_blood_rh_factor = request.POST.get('blood_rh_factor',None)
        profile_gender = request.POST.get('gender',None)
        shipping_house = request.POST.get('house',None)
        shipping_street = request.POST.get('street',None)
        shipping_address2 = request.POST.get('address2',None)
        shipping_landmark = request.POST.get('landmark',None)
        shipping_city = request.POST.get('city',None)
        shipping_state = request.POST.get('state',None)
        shipping_pincode = request.POST.get('pincode',None)
        shipping_phone = request.POST.get('phone',None)
        shipping_altphone = request.POST.get('altphone',None)
        
        if check_user_qs.check_first_name:
            profile_firstname = profile.first_name
        if check_user_qs.check_last_name:
            profile_lastname = profile.last_name
        if check_user_qs.check_email:
            profile_email = profile.email
        if check_user_qs.check_co_applicant:
            profile_co_applicant = profile.co_applicant
        if check_user_qs.check_blood_group:
            profile_blood_group = profile.blood_group
        if check_user_qs.check_blood_rh_factor:
            profile_blood_rh_factor = profile.blood_rh_factor
        if check_user_qs.check_gender:
            profile_gender = profile.gender
        if check_user_qs.check_date_of_birth:
            profile_birthday = profile.date_of_birth
        if check_user_qs.check_house_number:
            shipping_house = address_qs.house_number
        if check_user_qs.check_address_line:
            shipping_address2 = address_qs.address_line
        if check_user_qs.check_Landmark:
            shipping_landmark = address_qs.Landmark
        if check_user_qs.check_city:
            shipping_city = address_qs.city
        if check_user_qs.check_state:
            shipping_state = address_qs.state_id
        if check_user_qs.check_street:
            shipping_street = address_qs.street
        if check_user_qs.check_pin:
            shipping_pincode = address_qs.pin
        if check_user_qs.check_mobile:
            shipping_phone = address_qs.mobile
        if check_user_qs.check_alternate_mobile:
            shipping_altphone = address_qs.alternate_mobile
         
       
        profile_update = Profile.objects.filter(pk=profile.pk).update(first_name=profile_firstname,
                                                                      last_name=profile_lastname,
                                                                      date_of_birth=profile_birthday,
                                                                      co_applicant=profile_co_applicant,
                                                                      blood_group=profile_blood_group,
                                                                      blood_rh_factor=profile_blood_rh_factor,
                                                                      gender=profile_gender,
                                                                      )
        address_update = Address.objects.filter(pk=profile.shipping_address.pk).update(house_number=shipping_house,
                                                                                       address_line=shipping_address2,
                                                                                       Landmark=shipping_landmark,
                                                                                       city=shipping_city,
                                                                                       street=shipping_street,
                                                                                       pin=shipping_pincode,
                                                                                       alternate_mobile=shipping_altphone,
                                                                                       state_id=shipping_state,
                                                                                       )
         
        profile = Profile.objects.get(pk=profile.pk)
        user = profile.user

        # if kyc_qs.object_is:
         
                 
         
        messages.success(request, "Updated the Profile Successfully!")
        return redirect('mobile_verification')

        # return redirect('referral_list')
    # <-----------------------------------------------------------------for changing data in reqistration field ----------------------------------->

    try:
        bank_qs=get_object_or_404(BankAccountDetails, bank_account_user = user)
        cheque_photo = bank_qs.cheque_photo
        bank_form = BankAccountDetailsForm_for_user(instance=bank_qs)
    except:
        bank_qs = False
        cheque_photo = False
        bank_form = BankAccountDetailsForm_for_user()
    check_form = CheckForm(instance=check_user_qs)
        # data = User_Check(user_check = user,check_first_name = check)
        # data.save()
    referal_code=get_object_or_404(ReferralCode, user_id=user)
    # address_qs = get_object_or_404(Address,user = user,address_type='B')
    state = AdminState.objects.filter()
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    if profile.first_name == None:
        profile.first_name = ''
    if profile.last_name == None:
        profile.last_name = ''
    name = profile.first_name.title() + '  ' + profile.last_name.title()
    registration_form = check_registration_form_fn(check_user_qs)
    if registration_form == 'Registration  is Complete':
        messages.success(request, "Your details have been verified by us, in case you wish to change any detail please contact Auretics Support at 1800 889 0360 or mail at support@auretics.com")
        return redirect('home')
    context ={
        'profile': profile,
        'referal_code': referal_code,
        'address': address_qs,
        'bank_form': bank_form,
        'check_form': check_form,
        'check_user_qs': check_user_qs,
        'registration_form': registration_form,
        'cheque_photo': cheque_photo,
        'title': name,
        'state': state,
    }
    return render(request,'edit_profile.html',context)






@login_required
def track_order(request,myid):
    order = Order.objects.get(pk=myid)
    sr_shipment_id = order.sr_shipment_id
    om = OrderMaintain()
    om.set_token()

    om.get_channel_id()

    response = om.track_order(order)
    params = {}
    try:
        tracking_data = response["tracking_data"]
        track_url = response["tracking_data"]["track_url"]
        shipment_track = response["tracking_data"]["shipment_track"]
        try:
            shipment_data = shipping_track[0]
        except:
            shipment_data = []
        params = {'order':order,'tracking_data':tracking_data, 'track_url':track_url,'shipment_track':shipment_data}
        return render(request,'track_order.html',params)
    except:
        error = response["tracking_data"]["error"]
        messages.error(request,f"Shiprocket Error '{error}' ")
        params = {'order':order}
    return render(request,'track_order.html', params)



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form,'title':'Change Password',
    })



def Wallet_view(request):
    if settings.WALLET == "ON":
        with transaction.atomic():
            wallet = Wallet.objects.get(user=request.user)
            parms = {'wallet':wallet}
        return render(request,'wallet.html',parms)
    return redirect('home')
def recharge(request):

    if request.method == "POST":
        amount = float(int(request.POST["recharge"]))
        c_id = request.user.id
        c_email = request.user.email
        c_phone = request.user.profile.phone_number

        # with transaction.atomic():
        #     wallet = Wallet.objects.get(user=request.user)
        #     wallet.deposit(amount)
        JuspayPayment(request,amount,c_id, c_email, c_phone)
    return HttpResponseRedirect(reverse('wallet'))




def withdraw(request):
    if request.method == "POST":
        amount = float(request.POST["withdraw"])


        with transaction.atomic():
            wallet = Wallet.objects.get(user=request.user)
            wallet.withdraw(amount)
    return HttpResponseRedirect(reverse('profile'))

def validate_ref(request):
    referall_code = request.GET.get('referall_code', None)

    try:
        queryset = ReferralCode.objects.get(referral_code=referall_code)
        ref_list = queryset.user_id.username
        code= 200
    except ObjectDoesNotExist:
        ref_list=''
        code= 404
    #

    data = {
        'refer_by':ref_list,
        'code':code
    }
    return JsonResponse(data)


@csrf_exempt
def user_login2(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password =request.POST.get('password')
        user = authenticate(request, username= email, password=password)
        if user is not None :
            pass
        return JsonResponse(status=200,)
# here we are add a recapture in forget password
from django.contrib.auth.views import PasswordResetView


def test(request):
    data = ReferralCode.objects.filter(position = 'LEFT')
    data = data.latest('pk')
    return HttpResponse(data)

# referal_by having the data for that user which referalcode is used.
# referal_user this is the user which we are creating now.
def puting_parent_id(referal_by,referal_user,position):
    value = ReferralCode.objects.filter(parent_id = referal_by.user_id,position = position).exists()
    if value == False:
        referal_user.parent_id = referal_by.user_id
        return True
    else:
        data1 = ReferralCode.objects.filter(parent_id = referal_by.user_id,position = position).first()
        result = puting_parent_id(data1,referal_user,position)
        return result




def new_sign_up_auto(request):
    user = User
    context={}
    kyc = KycForm()
    bank_form = BankAccountDetailsForm()
    if request.method =='POST':
        postData= request.POST
        firstName = postData.get('firstname')
        lastName = postData.get('lastname')
        email = postData.get('email')
        email = email.lower()
        phone = postData.get('phone')
        password = postData.get('password')
        confirmpassword = postData.get('confirmPassword')

        referral_code = postData.get('referral_code')
        PAN = postData.get('pan_number')
# <--------------------------------------------------------------here we are adding coloumn for blood group and RH factor -------------------->
#         blood_group = postData.get('blood_group')
#         blood_rh_factor = postData.get('blood_rh_factor')
# <--------------------------------------------------------------here we are adding coloumn for blood group and RH factor -------------------->

        rc = ReferralCode.get_referal_code(referral_code)

        # here we are writing code for recaptchar
        clientkey = request.POST['g-recaptcha-response']
        serverkey = '6LeVCKgaAAAAADsn51OcTxu6-wZ_THxWCT7b_GoA'
        captchaData = {
            'secret': serverkey,
            'response': clientkey
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify',data=captchaData)
        response = json.loads(r.text)
        verify = response['success']
        if verify:
        # here we are writing code for recaptchar end here.
            if not firstName or not email or not phone  or not password or not referral_code:
                messages.error(request, "Form is Empty ")
            else:
                if rc:
                    if password == confirmpassword:
                        user = user(username = email, email=email)
                        user.set_password(password)
                        user.save()
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        if user.save:
                            profile = Profile.objects.get(user= request.user)
                            profile.first_name = postData.get('firstname')
                            profile.last_name =postData.get('lastname')
                            profile.date_of_birth=postData.get('birthday')
                            profile.co_applicant=postData.get('co_applicant')
                            profile.blood_group=postData.get('blood_group')
                            profile.blood_rh_factor=postData.get('blood_rh_factor')
                            profile.phone_number=postData.get('phone')
                            profile.save()
                            user_check = User_Check(user_check = request.user)
                            user_check.save()

    # <------------------------------------------------------------------------------21 feb referal code ----------------------------------------------------------->
                            userID = profile.id
                            UplineCode = rc.referral_code
                            PAN = PAN
                            final = genReferralCode(userID,UplineCode,PAN)
                            position = postData.get('position')
                            rfc = ReferralCode(user_id=request.user,
                                referal_id = profile.id, referral_code=final,referal_by = rc.user_id,status=False,position = position)

# <-----------------------------------------------------code for parent ------------------------------------------------------------------------------------------------->
                            position = rfc.position
                            if not ReferralCode.objects.filter(parent_id = rc.user_id,position = position).exists() :
                                rfc.parent_id = rc.user_id
                            else:
                                result = puting_parent_id(rc,rfc,position)
                                # data = ReferralCode.objects.filter(position = position,referal_by =  rc.user_id)
                                # data = data.latest('pk')
                                # rfc.parent_id = data.user_id
                            rfc.save()
# <-----------------------------------------------------code for end parent ------------------------------------------------------------------------------------------------->

                            code = get_object_or_404(ReferralCode, user_id=request.user)
                            profile.reference_user_id = code.id
                            profile.save()
                        else:
                            messages.error(request, "You are not registerd")
                        if profile.save:
                            addres_query = Address(user= request.user,
                                                    house_number=postData.get('house'),
                                                    address_line= postData.get('address2'),
                                                    Landmark= postData.get('landmark'),
                                                    city= postData.get('city'),
                                                    state_id = postData.get('state'),
                                                    street= postData.get('street'),
                                                    # country= postData.get(),
                                                    pin= postData.get('pincode'),
                                                    mobile= postData.get('phone'),
                                                    alternate_mobile= postData.get('altphone'),
                                                    default=True
                                                    )
                            addres_query.save()
                            profile.shipping_address = addres_query
                            profile.save()
                            try:
                                if addres_query.save:
                                    kyc = KycForm(request.POST, request.FILES)
                                    if kyc.is_valid():
                                        if request.POST["manual_verify"] == "Yes":
                                            kyc_ = kyc.save(commit=False)
                                            kyc_.kyc_user= request.user
                                            try:
                                                manual = ManualVerification.objects.create(kyc_user=request.user, pan_number=kyc_.pan_number, pan_file=kyc_.pan_file, id_proof_type=kyc_.id_proof_type,id_proof_file=kyc_.id_proof_file,address_proof_type=kyc_.address_proof_type,address_proof_file=kyc_.address_proof_file)
                                                manual.save()
                                                kyc_.save()
                                            except:
                                                manual = ManualVerification.objects.get(kyc_user=request.user)
                                                manual.pan_number = kyc_.pan_number
                                                manual.pan_file = kyc_.pan_file
                                                manual.id_proof_type = kyc_.id_proof_type
                                                manual.id_proof_file = kyc_.id_proof_file
                                                manual.address_proof_type = kyc_.address_proof_type
                                                manual.address_proof_file = kyc_.address_proof_file
                                                manual.save()
                                                kyc_.save()
                                        else:
                                            post = kyc.save(commit=False)
                                            post.kyc_user= request.user
                                            pan_number = post.pan_number
                                            try:
                                                img_path = post.pan_file.url
                                                print("path", img_path)
                                            except:
                                                img_path = None

                                            pan_name = post.pan_name

                                            response_kyc = Pan_verification(request,img_path,pan_number)
                                            if response_kyc == 400:
                                                messages.error(request,"Images not present in Identity, Update now")
                                                return redirect("edit_profile")
                                            if response_kyc["error"]:
                                                post.kyc_done = False
                                                post.save()

                                                messages.error(request,kyc_pan_fail_message)
                                                return redirect("register")

                                            result = response_kyc["result"]
                                            if result["verified"] == True:
                                                post.kyc_done = False
                                                post.save()
                                                pan_check_fn(request)
                                                messages.success = kyc_pan_pass_message
                                            else:
                                                messages.error = kyc_pan_fail_message
                                            print (post)
                                    else:
                                        # messages.error(request, "You KYC is not registerd")
                                        pass

                                    if post.save:
                                        bank_form = BankAccountDetailsForm(request.POST, request.FILES)
                                        if bank_form.is_valid():
                                            post_bank = bank_form.save(commit=False)
                                            post_bank.bank_account_user = request.user
                                            post_bank.save()
                                            post_bank = bank_form.cleaned_data['ifsc_code']

                                            messages.success(
                                                request, "You're now a user! You've been signed in, too."
                                                )
# <-----------------------------------------------------------Start email send message --------------------------------------------------------------------------------------------->
                                            from mlm_admin.views import sendemail
                                            result = sendemail(profile,final)
                                            phone = postData.get('phone')

                                            # result = sendsms(phone,final)
                                            result = sendsms("msg_welcome", user_mobile_number = "+91" + str(phone), ARN = final, password = password)
                                           
                                            result_sponsor = sendsms("msg_welcome_sponsor", user_mobile_number = "+91" + str(referral_mobile_number), ARN = final, referee_name = (str(firstName) + " " + str(lastName)))
# <-----------------------------------------------------------End email send message --------------------------------------------------------------------------------------------->
                                            return redirect('home')
                                    else:
                                        messages.success(
                                            request,"You are Signed In."
                                        )
# <-----------------------------------------------------------Start email send message --------------------------------------------------------------------------------------------->
                                        from mlm_admin.views import sendemail
                                        result = sendemail(profile,final)
                                        phone = postData.get('phone')
                                        # result = sendsms(phone,final)
                                        result = sendsms("msg_welcome", user_mobile_number = "+91" + str(phone), ARN = final, password = password)
                                       
                                        result_sponsor = sendsms("msg_welcome_sponsor", user_mobile_number = "+91" + str(referral_mobile_number), ARN = final, referee_name = (str(firstName) + " " + str(lastName)))
# <-----------------------------------------------------------End email send message --------------------------------------------------------------------------------------------->

                                        return redirect('home')
                            except:
                                messages.success(
                                    request,"You are Signed In."
                                )
# <-----------------------------------------------------------Start email send message --------------------------------------------------------------------------------------------->
                                from mlm_admin.views import sendemail
                                result = sendemail(profile,final)
                                phone = postData.get('phone')
                                # result = sendsms(phone,final)
                                result = sendsms("msg_welcome", user_mobile_number = "+91" + str(phone), ARN = final, password = password)
                               
                                result_sponsor = sendsms("msg_welcome_sponsor", user_mobile_number = "+91" + str(referral_mobile_number), ARN = final, referee_name = (str(firstName) + " " + str(lastName)))
# <-----------------------------------------------------------End email send message --------------------------------------------------------------------------------------------->
                                return redirect('home')
                    else:
                        messages.error(request, "password not match ")
                else:
                    messages.error(request, "Wrong ReferralCode ")


    state = AdminState.objects.filter()
    refid = request.GET.get('refid', False)
    fname = request.GET.get('fn', False)
    lname = request.GET.get('ln', False)
    email = request.GET.get('em', False)
    password = request.GET.get('pass', False)
    dob = request.GET.get('bd', False)
    dbirth = dob.split('/')
    dob = ''
    dob += dbirth[2]
    dob += '-'
    dob += dbirth[1]
    dob += '-'
    dob += dbirth[0]
    blood_group = request.GET.get('bg', False)
    rh_factor = request.GET.get('rh', False)
    position = request.GET.get('position', False)
    home_number = request.GET.get('ahn', False)
    street = request.GET.get('ast', False)
    address_line2 = request.GET.get('al2', False)
    land_mark = request.GET.get('alm', False)
    city = request.GET.get('city', False)
    state_adm = request.GET.get('state', False)
    pin = request.GET.get('pin', False)
    mobile = request.GET.get('mob', False)
    context={'form':kyc, 'bank_form':bank_form,'title':'Registration','refid':refid,'state':state,'fname':fname,'lname':lname,'email':email,'password':password,
             'dob':dob,'blood_group':blood_group,'rh_factor':rh_factor,'position':position,'home_number':home_number,'street':street,'address_line2':address_line2,
             'land_mark':land_mark,'city':city,'state_adm':state_adm,'pin':pin,'mobile':mobile}
    # return render(request, 'registration1.html', context)
    return render(request, 'registration_auto.html', context)


import random
#
def otp_send(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        try: 
            referal = ReferralCode.objects.get(referral_code = email)
            email = referal.user_id.username
        except:
            pass
        try:
            prof = Profile.objects.get(phone_number = email)
            email = prof.user.username
        except:
            pass
        email = email.lower()
        user = User.objects.get(email = email)
        number = user.profile.phone_number
        email = user.email
        otp = random.randrange(111111, 999999)
        result = login_otp_send(number,otp)
        result = login_otp_mail(email,otp)
        if result:
            request.session['otp'] = otp

            login(request, user)
#sends one time OTP Password
    return render(request,'otp_login.html')
def login_otp_send(number,otp):
    number = number
    otp = otp
    sms = 'Welcome to Auretics.Your One time password is - '+ str(otp) +' .For any query,please feel free to contact Auretics Support at 9090900247.'
    data = "http://nimbusit.co.in/api/swsend.asp?username=t1671910&password=psfl1015&sender=PSFLDL&sendto="+ number +"&entityID=1701158053522863199&templateID=1707161788188889057&message="+ sms
    response = requests.get(data)
    return True

def login_otp_mail(email,otp):
    smail = send_mail('OTP Varification',
                      'Welcome to Auretics. Your one time password is ' + str(otp),
                      settings.EMAIL_HOST_USER, [email])

    return True


from django.contrib.auth.forms import AdminPasswordChangeForm,PasswordChangeForm
@login_required(login_url='/mlm_admin/login')
@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management',['2']])
def admin_password_change(request,myid):
    user = User.objects.get(pk = myid)
    form = AdminPasswordChangeForm(user = user)
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user = user,data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                    request, ""
                             "Password has been reset successfully!"
                    )
            return redirect('referral_list')
    return render(request,'registration/password_reset_form.html',{'form':form})

@login_required(login_url='/mlm_admin/login')
def user_password_change(request):
    form = PasswordChangeForm(user = request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(user = request.user,data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request,form.user)
            messages.success(
                    request, ""
                             "Password has been reset successfully!"
                    )
            return redirect('home')
    return render(request,'registration/password_reset_form.html',{'form':form})
def check_box(request):
    if request.method == 'POST':
        check_box_value = request.POST.get('check_box',None)
    return render(request,'check_box.html')

