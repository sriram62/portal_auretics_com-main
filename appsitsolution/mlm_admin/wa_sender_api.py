import datetime
import logging
import os
import time

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

from mlm_admin.greetings_image_module import GreetingBaseTemplate
from mlm_admin.models import Greeting, WaConfiguration

User = get_user_model()


class GreetingSender:
    def __init__(self, greeting_id, user_list, message=""):
        self.greeting_id = greeting_id
        self.greeting = Greeting.objects.get(pk=greeting_id)
        self.user_list = user_list
        self.message = message
        self.from_number = settings.WA_NUMBER if settings.WA_NUMBER else settings.TWILIO_SANDBOX_NUMBER

    def send_wa_to_list(self):
        for user in self.user_list:
            if self.is_message_triggered(user):
                self.send_greeting_to_user(user)

    def is_message_triggered(self, user):
        current_time = datetime.datetime.now()
        user_pref_time = user.preferred_time
        if not user_pref_time:
            if current_time.time() > datetime.time(hour=9):
                return True
            else:
                return False

    def send_greeting_to_user(self, user):
        image_url = self.get_preview_image(user)
        receiver_number = user.profile.phone_number
        if "+" not in receiver_number:
            # FIXME: static country code
            receiver_number = "+91" + receiver_number
        # client = self.get_client("Twilio")
        client = self.get_client("Wassenger")
        # file_path for wassemger, image_url for Twilio
        print("image_url", image_url)
        result_message = client.send_message(receiver_number, self.message, image_url)
        print(result_message)

    def get_client(self, provider="Twilio"):
        if provider == "Twilio":
            return TwilioPlugin()
        if provider == "Wassenger":
            return WassengerPlugin()

    def get_preview_image(self, user):
        greeting_image = self.greeting.image
        # greeting_name = self.greeting.name
        file_name = self.get_file_name(user)
        temp_file_path = os.path.join(os.getcwd(), "media", "greeting_images", "tmp", file_name)
        GreetingBaseTemplate(user, greeting_image).save_preview_image(temp_file_path)
        return temp_file_path

    def get_file_name(self, user):
        file_name = user.profile.first_name
        file_name += "-" + user.profile.last_name
        file_name += "-" + user.referralcode.referral_code
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        file_name += "-" + str(timestamp)
        return file_name + ".jpg"

    def get_image_bytes(self, user):
        greeting_image = self.greeting.image
        img_bytes = GreetingBaseTemplate(user, greeting_image).get_preview_image_bytes()
        return img_bytes

    def send_wa_to_mock_list(self):
        user_list = self.get_mock_user_list()
        for user in user_list:
            self.send_greeting_to_user(user)

    def get_mock_user_list(self):
        # phone_nums = ['9737643838', '8866786647', '9999112999']
        phone_nums = ['9737643838', '8866786647']
        user_list = []
        for i, user in enumerate(self.user_list[:2]):
            user.profile.phone_number = phone_nums[i]
            user_list.append(user)
        return user_list


class TwilioPlugin:
    def __init__(self):
        from twilio.rest import Client
        self.sid = settings.TWILIO_ACCOUNT_SID
        self.token = settings.TWILIO_AUTH_TOKEN
        self.client = Client(self.sid, self.token)
        self.from_number = settings.TWILIO_SANDBOX_NUMBER

    def send_message(self, receiver_number, message, media_url):
        receiver_number = "whatsapp:" + receiver_number
        result_message = self.client.messages.create(
            from_=self.from_number,
            to=receiver_number,
            body=message,
            media_url=[media_url]
        )
        print(result_message)
        return result_message


class WassengerPlugin:
    def __init__(self):
        try:
            stored_token = WaConfiguration.object.all().reverse()[0].wassenger_token
        except:
            logging.warning("No Wassenger token found. Add Token in configuration to work")
            stored_token = settings.WASSENGER_TOKEN
        self.token = stored_token
        self.files_url = "https://api.wassenger.com/v1/files"
        self.message_url = "https://api.wassenger.com/v1/messages"

    def send_message(self, receiver_number, message, file_path):
        file_id = self.upload_file(file_path)
        if file_id:
            payload = {
                "phone": receiver_number,
                "message": message,
                "media": {"file": file_id}
            }
            headers = {
                "Content-Type": "application/json",
                "Token": self.token
            }

            response = requests.request("POST", self.message_url, json=payload, headers=headers)
            print("message response", response)
            print(response.json())
            return response

    def send_text_message(self, receiver_number, message, image_file_id=None):
        receiver_number = "+91" + receiver_number
        payload = {
            "phone": receiver_number,
            "message": message,
        }

        if image_file_id:
            payload["media"] = {"file": image_file_id}

        headers = {
            "Content-Type": "application/json",
            "Token": self.token
        }
        response = requests.request("POST", self.message_url, json=payload, headers=headers)
        print("message response", response)
        print(response.json())
        return response

    def upload_file(self, file_path):
        print("file_path :", file_path)
        files = {
            'file': open(file_path, 'rb')
        }
        header = {
            "Token": self.token
        }
        response = requests.request("POST", self.files_url, headers=header, files=files)
        print("response: ", response)
        if response.status_code == 409:
            print("file already exists")
            file_id = dict(response.json())["meta"]["file"]
            return file_id
        elif response.status_code >= 400:
            print('Upload failed with invalid status', response.status_code)
            return None
        else:
            response_json = response.json()
            file_id = response_json[0]['id']
            return file_id

    def upload_image_binary(self, image_bytes):
        files = {
            'file': image_bytes
        }
        header = {
            "Token": self.token
        }
        response = requests.request("POST", self.files_url, headers=header, files=files)
        print("response: ", response)
        if response.status_code == 409:
            print("file already exists")
            file_id = dict(response.json())["meta"]["file"]
            return file_id
        elif response.status_code >= 400:
            print('Upload failed with invalid status', response.status_code)
            return None
        else:
            response_json = response.json()
            file_id = response_json[0]['id']
            return file_id
