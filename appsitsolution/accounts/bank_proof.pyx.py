import requests
from portal_auretics_com.settings import signzy_username, signzy_password, signzy_spoc, signzy_callback


import json


def Authorization():

    url = "https://signzy.tech/api/v2/patrons/login"
    body = {
    "username":signzy_username,
    "password":signzy_password
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

    auth = Authorization()
    patron_id = auth["userId"]
    print("patronid", patron_id)
    id_ = auth["id"]
    print("id___", id_)

    url = f"https://signzy.tech/api/v2/patrons/61e8730595285167698f40a2/identities"

    image_body = {"type": "individualPan", "callbackUrl": "http://portal.auretics.com", "email": "arjun@auretics.com",
                  "images": [img_path]
                  }

    # payload = "{\"username\":\"<username>\",\"password\":\"<Password-or-apikey>\"}"
    headers = {
        'accept-language': "en-US,en;q=0.8",
        'accept': "*/*",
        'Authorization': id_
    }

    response = requests.request(
        "POST", url, data=None, json=image_body, headers=headers).json()

    # print("autoRecognition", response["autoRecognition"])
    # print("\nverification", response["verification"])
    # print("\nforgeryCheck", response["forgeryCheck"])
    print("Identity>>>>>>>", response)
    return response


def Bank_proof_api(request, ifsc, account_number):
    print(Authorization())
    auth = Authorization()
    id_ = auth["id"]

    patron_id = auth["userId"]

    url = f"https://signzy.tech/api/v2/patrons/{patron_id}/bankaccountverifications"

    body = {
        "task": "bankTransfer",
        "essentials": {
            "beneficiaryAccount": account_number,
            "beneficiaryIFSC": ifsc,
            "nameFuzzy": "true"
        }
    }
    headers = {
        'Authorization': id_,
        'Content-type': 'application/json'
    }
    response = requests.request("POST", url, data=body, headers=headers)

    return response



def Pan_verification(request,img_path,pan):
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
        print("pan_num", pan_num)
        print("pan", pan)

        if pan == pan_num:
            print("equal")
            return {'verified': 'True'}
        else:
            return {'error': 'Image is verified but pan number does not match'}
    except:
        return {'error': 'Pan number does not match'}
