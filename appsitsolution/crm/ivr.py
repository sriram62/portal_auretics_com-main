from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.http import HttpResponseNotFound
from accounts.views import new_sign_up
from accounts.models import Profile, ReferralCode
import datetime
import logging
from .models import ivr_user_created, ivr_logs, ivr_check_logs

# Create your views here.
# Create a logger for this file
logger = logging.getLogger('django')

def check_user_exist(request):
    CallSid = request.GET.get('CallSid', '')
    if not CallSid:
        return HttpResponseNotFound("CallSid not found")

    mynumber = request.GET.get('CallFrom', '')
    ivr_check_logs_qs = ivr_check_logs(get_req=str(request.GET),
                                       callsid=CallSid,
                                       mynumber_bc=mynumber)
    ivr_check_logs_qs.save()

    ivr_logs_qs = ivr_logs.objects.filter(callsid = CallSid)[0]
    user_already_exist_error = ivr_logs_qs.user_already_exist_error
    if user_already_exist_error:
        return HttpResponseNotFound("User already exist")
    else:
        return HttpResponse('<h1>DoesNotExist</h1>')

def check_upline_exist(request):
    CallSid = request.GET.get('CallSid', '')
    if not CallSid:
        return HttpResponseNotFound("CallSid not found")

    mynumber = request.GET.get('CallFrom', '')
    ivr_check_logs_qs = ivr_check_logs(get_req=str(request.GET),
                                       callsid=CallSid,
                                       mynumber_bc=mynumber)
    ivr_check_logs_qs.save()

    ivr_logs_qs = ivr_logs.objects.filter(callsid=CallSid)[0]
    sponsor_does_not_exist_error = ivr_logs_qs.sponsor_does_not_exist_error
    if sponsor_does_not_exist_error:
        return HttpResponseNotFound("sponsor_does_not_exist_error")
    else:
        return HttpResponse('<h1>Exist</h1>')

def check_user_success(request):
    CallSid = request.GET.get('CallSid', '')
    if not CallSid:
        return HttpResponseNotFound("CallSid not found")

    mynumber = request.GET.get('CallFrom', '')
    ivr_check_logs_qs = ivr_check_logs(get_req=str(request.GET),
                                       callsid=CallSid,
                                       mynumber_bc=mynumber)
    ivr_check_logs_qs.save()

    ivr_logs_qs = ivr_logs.objects.filter(callsid = CallSid)[0]
    user_created_successfully = ivr_logs_qs.user_created_successfully
    if not user_created_successfully:
        return HttpResponseNotFound("Unsuccessful")
    else:
        return HttpResponse('<h1>Successful</h1>')

def ivr_register(request, mynumber=None, myupline=None):
    ivr_logs_qs = ivr_logs(get_req=str(request.GET))
    ivr_logs_qs.save()

    ivr_logs_qs = ivr_logs.objects.filter(pk=ivr_logs_qs.pk)

    mynumber = request.GET.get('CallFrom', '')
    myupline = request.GET.get('digits', '')
    CurrentTime = request.GET.get('CurrentTime', '')
    CallSid = request.GET.get('CallSid', '')

    ivr_logs_qs.update(mynumber_bc=mynumber,
                       myupline_bc=myupline,
                       CurrentTime_bc=CurrentTime,
                       callsid = CallSid)

    mynumber = mynumber[1:][0:10]
    myupline = myupline[1:][0:10]
    CurrentTime = CurrentTime[0:10]

    ivr_logs_qs.update(mynumber_ac=mynumber,
                       myupline_ac=myupline,
                       CurrentTime_ac=CurrentTime)

    # AG :: Validating the call
    # AG :: With date
    date_now = str(datetime.datetime.now())[0:10]
    # CurrentTime = str(datetime.datetime.strptime(CurrentTime, '%Y-%m-%d').date())
    if date_now != CurrentTime:
        ivr_logs_qs.update(date_mismatch_error=True)
        return HttpResponseNotFound("date mismatch")

    # AG :: are numbers are passed or not
    if not mynumber:
        ivr_logs_qs.update(mynumber_mismatch_error=True)
        return HttpResponseNotFound("mynumber mismatch")
    if not myupline:
        ivr_logs_qs.update(myupline_mismatch_error=True)
        return HttpResponseNotFound("myupline mismatch")

    response = []
    mynumber = str(mynumber)
    myupline = str(myupline)

    mynumber_exist = Profile.objects.filter(phone_number=mynumber)
    if mynumber_exist:
        ivr_logs_qs.update(user_already_exist_error=True)
        return HttpResponseNotFound("User already exist")

    myupline_exist = Profile.objects.filter(phone_number=myupline)
    if not myupline_exist:
        ivr_logs_qs.update(sponsor_does_not_exist_error=True)
        return HttpResponseNotFound("Sponsor does not exist")

    if len(str(myupline)) == 10:
        try:
            refid = Profile.objects.get(phone_number=myupline).user
            if refid:
                refid_position = ReferralCode.objects.get(user_id=refid).position
                refid_referral_code = ReferralCode.objects.get(user_id=refid).referral_code
                if refid_position == "LEFT":
                    position = "RIGHT"
                if refid_position == "RIGHT":
                    position = "LEFT"
        except:
            pass
        details = {
            'firstname' : "ivr" + str(mynumber),
            'lastName' : "ivr" + str(mynumber),
            'email' : "ivr" + str(mynumber) + "@mywebstay.com",
            'check_box_value' : 'on',
            'phone' : mynumber,
            'password' : str(mynumber),
            'confirmPassword' : str(mynumber),
            'referral_code' : refid_referral_code,
            'PAN' : "UserAddedViaIVR",
            'birthday' : '1900-01-01',
            'co_applicant' : "",
            'blood_group' : 'I don\'t know',
            'blood_rh_factor' : 'I don\'t know',
            'gender' : 'Other',
            'house' : 'IVRhouse',
            'address2' : 'IVRaddress2',
            'landmark' : 'IVRlandmark',
            'city' : 'IVRcity',
            'state' : '10',
            'street' : 'IVRstreet',
            'pincode' : '100000',
            'altphone' : '',
            'refid' : refid_referral_code,
            'position' : position,
        }
        updated_request = request
        updated_request.method = 'POST'
        updated_request.POST = details
        # updated_request.update({'method':'POST',
        #                         'POST':{'get':{details}}})
        # updated_request.POST.get = details
        response = new_sign_up(updated_request)
    if response:
        mynumber_exist = Profile.objects.filter(phone_number=mynumber)
        if mynumber_exist:
            ivr_user_created(user=mynumber_exist.user, created=True)
            ivr_logs_qs.update(user_created_successfully=True)
        else:
            ivr_logs_qs.update(user_not_created_error=True)
        return response
        # return HttpResponse('<h1>Profile Creation is Successful</h1>')
    else:
        ivr_logs_qs.update(user_not_created_error=True)
        return HttpResponse('<h1>Invalid Upline Number</h1>')