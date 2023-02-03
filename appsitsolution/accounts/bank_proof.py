# from portal_auretics_com.settings import signzy_username, signzy_password, signzy_spoc, signzy_callback
import requests
from portal_auretics_com.settings import signzy_username, signzy_password, signzy_spoc, signzy_callback
from .models import *


import json

 
def Authorization():

    url = "https://signzy.tech/api/v2/patrons/login"
    body = {
        "username": signzy_username,
        "password": signzy_password
    }
    # payload = "{\"username\":\"<username>\",\"password\":\"<Password-or-apikey>\"}"
    headers = {
        'accept-language': "en-US,en;q=0.8",
        'accept': "*/*"
    }

    response = requests.request("POST", url, data=body, headers=headers).json()
    print("auth>>>>>>>", response)
    return response


def Identity(request, img_path):
    try:
        user_verification_status = User_Check.objects.get(user_check=request.user)
        if not user_verification_status.check_pan_number:
            auth = Authorization()
            patron_id = auth["userId"]
            id_ = auth["id"]
            url = f"https://signzy.tech/api/v2/patrons/{patron_id}/identities"
            image_body = {"type": "individualPan", "callbackUrl": "https://portal.auretics.com/", "email": "arjun@auretics.com",
                          "images": [f"https://portal.auretics.com{img_path}"]
            # image_body = {"type": "individualPan", "callbackUrl": "http://portal.auretics.com", "email": "arjun@auretics.com",
            #               "images": [str(img_path)]
                          }
            # image_body = {"type": "individualPan", "callbackUrl": "https://portal.auretics.com/", "email": "arjun@auretics.com",
            #               "images": [f"http://testpal.arj.uno/media/pan_card/images/PAN_CARD_FRONT.jpg"]}
            # payload = "{\"username\":\"<username>\",\"password\":\"<Password-or-apikey>\"}"
            headers = {
                'accept-language': "en-US,en;q=0.8",
                'accept': "*/*",
                'Authorization': id_
            }

            response = requests.request(
                "POST", url, data=None, json=image_body, headers=headers).json()
            print("Identity>>>>>>>", response)
            return response
        else:
            return True
    except:
        return False


def Bank_proof_api(request, ifsc, account_number, name_in_bank):
    try:
        user_verification_status = User_Check.objects.get(user_check=request.user)
        if not user_verification_status.check_account_number:
            auth = Authorization()
            id_ = auth["id"]

            patron_id = auth["userId"]

            url = f"https://signzy.tech/api/v2/patrons/{patron_id}/bankaccountverifications"

            body = {
                "task": "bankTransfer",
                "essentials": {
                    "beneficiaryAccount": account_number,
                    "beneficiaryIFSC": ifsc,
                    "beneficiaryName": name_in_bank,
                    "nameFuzzy": "true"
                }
            }
            headers = {
                'Authorization': id_,
                'Content-type': 'application/json'
            }
            response = requests.request("POST", url, data=None,json=body, headers=headers).json()
            print("Real bank details >>>>>>>>>>",response)
            return response
        else:
            response = {'task': 'bankTransfer',
                     'essentials': {'beneficiaryAccount': '', 'beneficiaryIFSC': '',
                                    'beneficiaryName': '', 'nameFuzzy': 'true'}, 'id': '',
                     'patronId': '',
                     'result': {'active': 'yes', 'nameMatch': 'yes', 'mobileMatch': 'not available',
                                'signzyReferenceId': '',
                                'auditTrail': {'nature': 'BANK RRN', 'value': '',
                                               'timestamp': ''},
                                'bankTransfer': {'response': 'Transaction Successful', 'bankRRN': '',
                                                 'beneName': '', 'beneMMID': '', 'beneMobile': '',
                                                 'beneIFSC': ''}}}
            return response
    except:
        return False

# PAN Extraction API
def Pan_verification(request, img_path, pan):
    try:
        user_verification_status = User_Check.objects.get(user_check=request.user)
        if not user_verification_status.check_pan_number:
            url = "https://signzy.tech/api/v2/snoops"
            res = Identity(request, img_path)
            try:
                IdentityID = res["id"]
                accessToken = res["accessToken"]
            except:
                return res
            bodyFetch = {"service": "Identity", "itemId": IdentityID, "task": "autoRecognition", "accessToken": accessToken, "essentials": {}
                         }
            headers = {
                'accept-language': "en-US,en;q=0.8",
                'accept': "*/*"
            }

            responseFetch = requests.request(
                "POST", url, data=None, json=bodyFetch, headers=headers).json()
            print("ressssss>>>>>", responseFetch)

            pan_num = responseFetch["response"]["result"]['number']
            try:
                if responseFetch.status_code == 400:
                    return 400
            except:
                pass

            try:
                pan_num = responseFetch["response"]["result"]['number']
                if pan == pan_num:
                    return {'verified': 'True'}
                else:
                    pan_error = "PAN image uploaded is different from PAN number entered. PAN entered is " + pan + " and PAN uploaded is " + pan_num
                    return {'error': pan_error }
            except:
                return {'error': 'Pan number does not match'}
        else:
            response = {'service': 'Identity', 'itemId': '', 'task': 'autoRecognition', 'essentials': {},
                         'accessToken': '', 'id': '',
                         'response': {'files': [''],
                                      'type': 'individualPan',
                                      'instance': {'id': '', 'callbackUrl': 'https://portal.auretics.com/'},
                                      'id': 67,
                                      'result': {'dob': '', 'name': '', 'fatherName': '',
                                                 'number': '', 'panType': 'Adult',
                                                 'summary': {'number': '', 'name': '', 'dob': '',
                                                             'address': '',
                                                             'splitAddress': {'district': [], 'state': [[]], 'city': [],
                                                                              'pincode': '', 'country': [], 'addressLine': ''},
                                                             'gender': '', 'guardianName': '', 'issueDate': '',
                                                             'expiryDate': ''}}}}
            return response
    except:
        return False