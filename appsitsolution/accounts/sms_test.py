# Used to send SMSes with AWS.

from sms import *
import boto3
import requests
import urllib.parse
# from numbers_to_send import numbers_to_send
# from cri_july_21 import numbers_to_send

numbers_to_send = [9999112999,9090900247,7838643736,]

while True:
    print("Enter a input")
    sms_input = input()
    for num in numbers_to_send:
        sendsms(
        sms_input,
        user_mobile_number          = "+91" + str(num),
        # referred_by_mobile_number   = "referred_by_mobile_number",
        # referee_name                = "referee_name",
        # referrer_name               = "referrer_name",
        # registration_number         = "registration_number",
        # password                    = "password",
        # sex                         = "sex",
        # referred_by_id              = "referred_by_id",
        # order_id                    = "order_id",
        # order_dispatched_by         = "order_dispatched_by",
        # order_awb                   = "order_awb",
        # order_status                = "order_status",
        # month                       = "month",
        # commission_amount           = "commission_amount",
        # profile_status              = "profile_status",
        # otp                         = "otp",
        # otp_time                    = "otp_time",
        # password_reset_link         = "password_reset_link",
        # cri_amt                     = "str(num[1])"
        )
