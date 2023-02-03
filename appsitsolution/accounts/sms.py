# Used to send SMSes with AWS.

import boto3
import requests
import urllib.parse
from portal_auretics_com import settings
# from numbers_to_send import numbers_to_send
# from cri_july_21 import numbers_to_send

# Configurations
service = "AWS"
# service = "NimbusIT"

# Add mobile numbers here.
# numbers_to_send = [9999112999,9090900247,7838643736,9719101082,]
# numbers_to_send = [[9999112999,100],[9090900247,200],[7838643736,300],[9719101082,1245],]

# Create an SNS client
client = boto3.client(
    "sns",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key = settings.aws_secret_access_key,
    region_name = settings.region_name,
)

sender_id = "AURTCS"
entity_id = "1201161952385409194"



# Global SMS Variables:
support_number = "9090900247"


# Messages are list with Message String and TemplateIds in the format: [msg,templateid]

# Send these two message after registration. One to the person who has signed up and other to his upline.
msg_welcome = ["""Jai Hind and Welcome to Auretics!
Your registration number is {} and password is {}
For any query, please call 9090900247.""",
"1207162409404347254"]

msg_welcome2 = ["""Congratulations and Welcome to Auretics. Your registration number is {}. For any query, please feel free to contact Auretics Support at {}.""",
"1207162010663237641"]

msg_welcome_sponsor = ["""Jai Hind{}!
{} has joined under you with registration number {}.
For any query, please call Auretics Support at 9090900247.""",
"1207162409411106654"]



# Mesages related to Orders.
msg_order_placed = ["""Jai Hind{}!
Your order ID {} has been placed and will be dispatched soon.
For any query, please call Auretics Support at 9090900247.""",
"1207162409415636335"]

msg_order_dispatched = ["""Jai Hind{}!
Your order has been dispatched via {} with AWB number {}.
For any query, please call Auretics Support at 9090900247.""",
"1207162409420534479"]

msg_order_status_change = ["""Jai Hind{}!
Your order ID {} has been {}.
For any query, please call Auretics Support at 9090900247.""",
"1207162409427774879"]



# Payment related
payment_link = ["""Jai Hind{}!
Greetings from Auretics.
Please pay at https://pay.auretics.com to place your order.
For support call {}""",
"1207162745464935311"]

payment_link2 = ["""Jai Hind {}!
Please pay at https://pay.auretics.com to place your order.
For support call {}""",
"1207162736633478000"]



# When user earns an income, typically on  week of the next month.
msg_income_earned = ["""Jai Hind{}!
Your income summary for {} is ready. Please goto https://portal.auretics.com/ and login to Business Dashboard for complete information.""",
"1207162409431780954"]

# When commission is transferred.
msg_commission_transferred = ["""Jai Hind{}!
We have transferred your commission of Rs. {} for the month of {}.
For any query, please call Auretics Support at 9090900247.""",
"1207162409437642293"]

# When user gets loyalty purchase voucher
msg_loyalty_purchase = ["""Jai Hind!
Greetings from Auretics.
You have received loyalty purchase voucher worth Rs.{}.
Please place your order online or to our DP and call 9090900247 to receive loyalty products.
For support call 9090900247.""",
"1207162745494155435"]



# User KYC & Profile related
msg_kyc_done = ["""Jai Hind{}!
We have checked all your details. Your profile {} is now {}.
For any changes in future, call Auretics Support at 9090900247.""",
"1207162442889265934"]

msg_kyc_done2 = ["""Jai Hind {}!
We have verified all your details. Your profile is now {}.
For any changes in future, call Auretics Support at {}.""",
"1207162442352551734"]

msg_kyc_pending = ["""Jai Hind{}!
We were unable to check your details your profile {}. Please login at http://auretics.com/ and Update Profile with missing details.""",
"1207162442894455161"]

msg_kyc_pending2 = ["""Jai Hind {}!
We were unable to verify your details. Please login at http://auretics.com/ and Update Profile with missing details.
For support call {}.""",
"1207162442357572035"]

msg_kyc_reminder = ["""Jai Hind!
Please complete your profile at https://portal.auretics.com/accounts/profile/edit/.
For support call 9090900247""",
"1207162736674077534"]

msg_kyc_reminder2 = ["""Jai Hind{}!
Greetings from Auretics.
Please complete your profile at https://portal.auretics.com/accounts/profile/edit/.
For support call {}""",
"1207162745519994274"]

msg_kyc_reminder3 = ["""Jai Hind {}!
Greetings from Auretics Limited
Your Auretics profile is pending, please login and complete your profile from the URL https://portal.auretics.com/accounts/profile/edit/""",
"1207162580736452708"]

msg_kyc_reminder4 = ["""Jai Hind{}!
Greetings from Auretics.
Please complete your profile at {}/{}.
For support call {}""",
"1207162745516176196"]

msg_update_profile = ["""Jai Hind!
Greetings from Auretics.
Please login and complete your Auretics profile from the URL https://portal.auretics.com/accounts/profile/edit/""",
"0"]

ceo_video_msg = ["""Jai Hind{}!
Greetings from Auretics.
Welcome to the Auretics Family, your registration is now complete.
Please visit {}/{} to view our CEO’s message.""",
"1207162745512118248"]

ceo_video_msg2 = ["""Jai Hind {}!
Welcome to the Auretics Family, your registration is now complete.
Please visit {}/{} to view our CEO’s message.""",
"1207162736666859600"]


# Login OTP
msg_otp = ["""Jai Hind{}!
OTP for login to your Auretics Portal is {}.
This OTP is valid for {} minutes.
Please donot share this OTP.
For support call 9090900247""",
"1207162427077639745"]



# To reset password
msg_forgot_password = ["""Use this link to reset your Auretics password: {}""",
"1207162427083763011"]





# General Notifications
mandatory_orientation = ["""Jai Hind {}!
Greetings from Auretics.
You are required to attend mandatory orientation training.
Please visit https://youtu.be/XjsOP18odc4.""",
"1207162736652825610"]

mandatory_orientation2 = ["""Jai Hind{}!
Greetings from Auretics.
You are required to attend mandatory orientation training.
Please visit {}.""",
"1207162745507883354"]

msg_offer_kargil = ["""Jai Hind!
Auretics Offer till 1st August!
On purchase of any product, you will get:
1 - Vitalyte Biscuit
1 – Vitalyte Liquid
1 – TeaAmmrit
1 – Pink Care Hand Sanitizer – 200ml
Worth Rs. 627
Absolutely Free!!!
Place your orders now at:
https://portal.auretics.com""",
"1207162736709566569"]

product_offer = ["""Jai Hind!
Greetings from Auretics.
Auretics {}!
On purchase of any product, you will get:
1 - {}
1 - {}
1 - {}
1 - {}
Worth {}
{}!!!
{} valid till {}
Place your orders now at:
{}""",
"1207162745531222422"]

product_offer2 = ["""Jai Hind!
Auretics {}!
On purchase of any product, you will get:
{}
{}
{}
{}
Worth {}
{}!!!
Place your orders now at:
{}""",
"1207162736713615076"]

mandatory_orientation = ["""Jai Hind{}!
Greetings from Auretics.
A new video is available for you at {}""",
"1207162745498716339"]

mandatory_orientation2 = ["""Jai Hind{}!
Greetings from Auretics.
You are required to attend mandatory orientation training.
Please visit {}/{}.""",
"1207162745504910777"]

mandatory_orientation3 = ["""Jai Hind {}!
Greetings from Auretics.
You are required to attend mandatory orientation training.
Please visit {}.""",
"1207162736661693297"]

product_knowledge = ["""Jai Hind{}!
Greetings from Auretics.
Product knowledge for {} is now available at {}.""",
"1207162745486466015"]

product_knowledge2 = ["""Jai Hind{}!
Greetings from Auretics.
Product knowledge for {} is now available at {}/{}.""",
"1207162745477594129"]

new_product_available = ["""Jai Hind{}!
Greetings from Auretics.
Your {} product {} is now available at {}/{}.""",
"1207162745527251153"]

new_msg = ["""Jai Hind{}!
Greetings from Auretics.
A new message is available for you at {}""",
"1207162745523608006"]

new_msg_with_name = ["""Jai Hind {}!
{} sent you a new message at Auretics Portal.
{}
For support call {}""",
"1207162736618533436"]

wishlist_item = ["""Jai Hind{}!
Greetings from Auretics.
Your wishlisted item {} is now available.
Please goto {}/{} to place your order.
For support call {}""",
"1207162745535467162"]

msg_prod_know = ['''Jai Hind!
Greetings from Auretics.
Product knowledge for TPAS is now available at https://youtu.be/e28dOZcPbyI.''','1207162745486466015']

new_video = ['''"Jai Hind!
Greetings from Auretics.
A new video is available for you at https://youtu.be/sU2OtxKsoMY"''','1207162745498716339']

navratra = ['''Jai Hind!
Greetings from Auretics.
Navratra Offer is Live.
Get double consistency.
Valid from 7th October to 16th October 2021.
Visit https://auretics.com.''','1207163351340313091']



def sendsms(message_type,*arg,**kwargs):

    try:
        user_mobile_number = str(kwargs["user_mobile_number"])
    except:
        user_mobile_number = ""
    try:
        referred_by_mobile_number = str(kwargs["referred_by_mobile_number"])
    except:
        referred_by_mobile_number = ""
    try:
        referee_name = str(kwargs["referee_name"])
    except:
        referee_name = ""
    try:
        referrer_name = str(kwargs["referrer_name"])
    except:
        referrer_name = ""
    try:
        registration_number = str(kwargs["registration_number"])
    except:
        registration_number = ""
    try:
        ARN = str(kwargs["ARN"])
    except:
        ARN = ""
    try:
        password = str(kwargs["password"])
    except:
        password = ""
        
    try:
        sex = ""
        sex = str(kwargs["sex"])

        if sex == "Male":
            sex_salutation = " Sir"
        elif sex == "Female":
            sex_salutation = " Ma'am"
        else:
            sex_salutation = ""
    except:
        sex_salutation = ""

    try:
        referred_by_id = str(kwargs["referred_by_id"])
    except:
        referred_by_id = ""
    try:
        order_id = str(kwargs["order_id"])
    except:
        order_id = ""
    try:
        order_dispatched_by = str(kwargs["order_dispatched_by"])
    except:
        order_dispatched_by = ""
    try:
        order_awb = str(kwargs["order_awb"])
    except:
        order_awb = ""
    try:
        order_status = str(kwargs["order_status"])
    except:
        order_status = ""
    try:
        month = str(kwargs["month"])
    except:
        month = ""
    try:
        commission_amount = str(kwargs["commission_amount"])
    except:
        commission_amount = ""
    try:
        profile_status = str(kwargs["profile_status"])
    except:
        profile_status = ""
    try:
        otp = str(kwargs["otp"])
    except:
        otp = ""
    try:
        otp_time = str(kwargs["otp_time"])
    except:
        otp_time = ""
    try:
        password_reset_link = str(kwargs["password_reset_link"])
    except:
        password_reset_link = ""
    try:
        cri_amt = str(kwargs["cri_amt"])
    except:
        cri_amt = ""

    message_format = ""
    message_template_id = ""
    message_template_id = ""
    send_message = True

    # if 0 == 0:
    try:
    
        if message_type == "msg_welcome":
            message_format = msg_welcome[0].format(ARN, password)
            message_template_id = msg_welcome[1]
            # # print(message_format)

        elif message_type == "msg_welcome2":
            message_format = msg_welcome2[0].format(ARN,support_number)
            message_template_id = msg_welcome2[1]
            # print(message_format)
            
        elif message_type == "msg_welcome_sponsor":
            message_format = msg_welcome_sponsor[0].format(sex_salutation,referee_name,ARN)
            message_template_id = msg_welcome_sponsor[1]
            # print(message_format)

        elif message_type == "msg_order_placed":
            message_format = msg_order_placed[0].format(sex_salutation,order_id)
            message_template_id = msg_order_placed[1]
            # print(message_format)

        elif message_type == "msg_order_dispatched":
            message_format = msg_order_dispatched[0].format(sex_salutation,order_dispatched_by, order_awb)
            message_template_id = msg_order_dispatched[1]
            # print(message_format)

        elif message_type == "msg_order_status_change":
            message_format = msg_order_status_change[0].format(sex_salutation,order_id, order_status)
            message_template_id = msg_order_status_change[1]
            # print(message_format)

        elif message_type == "msg_income_earned":
            message_format = msg_income_earned[0].format(sex_salutation,month)
            message_template_id = msg_income_earned[1]
            # print(message_format)

        elif message_type == "msg_commission_transferred":
            message_format = msg_commission_transferred[0].format(sex_salutation,commission_amount,month)
            message_template_id = msg_commission_transferred[1]
            # print(message_format)

        elif message_type == "msg_kyc_done":
            message_format = msg_kyc_done[0].format(sex_salutation,profile_status)
            message_template_id = msg_kyc_done[1]
            # print(message_format)

        elif message_type == "msg_kyc_pending":
            message_format = msg_kyc_pending[0].format(sex_salutation)
            message_template_id = msg_kyc_pending[1]
            # print(message_format)

        elif message_type == "msg_otp":
            message_format = msg_otp[0].format(sex_salutation,otp,otp_time)
            message_template_id = msg_otp[1]
            # print(message_format)

        elif message_type == "msg_forgot_password":
            message_format = msg_forgot_password[0].format(password_reset_link)
            message_template_id = msg_forgot_password[1]
            # print(message_format)

        elif message_type == "msg_update_profile":
            message_format = msg_update_profile[0]
            message_template_id = msg_update_profile[1]
            # print(message_format)

        elif message_type == "msg_offer_kargil":
            message_format = msg_offer_kargil[0]
            message_template_id = msg_offer_kargil[1]
            # print(message_format)

        elif message_type == "mandatory_orientation":
            message_format = mandatory_orientation[0]
            message_template_id = mandatory_orientation[1]
            # print(message_format)

        elif message_type == "msg_kyc_reminder":
            message_format = msg_kyc_reminder[0]
            message_template_id = msg_kyc_reminder[1]
            # print(message_format)

        elif message_type == "msg_loyalty_purchase":
            message_format = msg_loyalty_purchase[0].format(cri_amt)
            message_template_id = msg_loyalty_purchase[1]
            # print(message_format)

        elif message_type == 'msg_prod_know':
            message_format = msg_prod_know[0]
            message_template_id = msg_prod_know[1]
            print(message_format)

        elif message_type == 'new_video':
            message_format = new_video[0]
            message_template_id = new_video[1]
            print(message_format)

        elif message_type == 'navratra':
            message_format = navratra[0]
            message_template_id = navratra[1]
            print(message_format)

        else:
            print("Please enter valid Message Type")
            send_message = False


    except:
        print("""An error occurred while preparing the message as per the required format.
        This typically happens when all required arguments are not passed.""")


    if send_message == True:
        publish_msg(user_mobile_number,message_format,message_template_id)
        # return True

def publish_msg(user_mobile_number,message_format,message_template_id):
    # Send your sms message via AWS:
    if service == "AWS":
        client.publish(
            PhoneNumber= str(user_mobile_number),
            Message= message_format,
            MessageAttributes= {
            'AWS.SNS.SMS.SenderID': {'DataType': 'String', 'StringValue': sender_id},
            'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'},
            "AWS.MM.SMS.TemplateId" : {'DataType': 'String', 'StringValue': message_template_id},
            "AWS.MM.SMS.EntityId" : {'DataType': 'String', 'StringValue': entity_id},
            }
        )
        # return True
        return False

    elif service == "NimbusIT":
        number = str(user_mobile_number)
        sms = urllib.parse.quote(message_format, safe='')
        data = "https://nimbusit.co.in/api/swsend.asp?username=" + settings.nimbus_username + "&password=" + settings.nimbus_password + "&sender=AURTCS&sendto=" + number + "&entityID=" + entity_id + "&templateID=" + message_template_id + "&message=" + sms
        response = requests.get(data)
        # print("Data is:")
        # print(data)
        # print(response)
        # return True
        return False

    else:
        print("Please enter valid service name in service variable")
        return False
# no_of_sms_sent = 0

# for number_to_send in numbers_to_send:
#     sendsms(
#     "msg_update_profile",
#     user_mobile_number="+91"+str(number_to_send),
#     referred_by_mobile_number="referred_by_mobile_number",
#     referee_name="referee_name",
#     referrer_name="referrer_name",
#     registration_number="registration_number",
#     password="password",
#     sex="sex",
#     referred_by_id="referred_by_id",
#     order_id="order_id",
#     order_dispatched_by="order_dispatched_by",
#     order_awb="order_awb",
#     order_status="order_status",
#     month="month",
#     commission_amount="commission_amount",
#     profile_status="profile_status",
#     otp="otp",
#     otp_time="otp_time",
#     password_reset_link="password_reset_link",
#     )
#     no_of_sms_sent += 1

# print("Number of SMS Sent are: " + str(no_of_sms_sent))
# 
# while True:
#     print("Enter a input")
#     sms_input = input()
#     for num in numbers_to_send:
#         sendsms(
#         sms_input,
#         user_mobile_number          = "+91" + str(num),
#         referred_by_mobile_number   = "referred_by_mobile_number",
#         referee_name                = "referee_name",
#         referrer_name               = "referrer_name",
#         registration_number         = "registration_number",
#         password                    = "password",
#         sex                         = "sex",
#         referred_by_id              = "referred_by_id",
#         order_id                    = "order_id",
#         order_dispatched_by         = "order_dispatched_by",
#         order_awb                   = "order_awb",
#         order_status                = "order_status",
#         month                       = "month",
#         commission_amount           = "commission_amount",
#         profile_status              = "profile_status",
#         otp                         = "otp",
#         otp_time                    = "otp_time",
#         password_reset_link         = "password_reset_link",
#         cri_amt                     = "str(num[1])"
#         )
