import datetime
import os
# from django.http import HttpResponse
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from twilio.rest import Client

from mlm_admin.greetings_image_module import GreetingBaseTemplate
from mlm_admin.models import Greeting

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN

client = Client(account_sid, auth_token)
from_number = settings.TWILIO_SANDBOX_NUMBER

User = get_user_model()


def get_preview_image(user, greeting_id):
    greeting = Greeting.objects.get(pk=greeting_id)
    greeting_image = greeting.image
    greeting_name = greeting.name
    file_name = uuid.uuid4().hex + ".jpg"
    temp_file_path = os.path.join(os.getcwd(), "media", "greeting_images", "tmp", file_name)
    # print(temp_file_path)
    # print(os.path.isdir(temp_file_path))
    GreetingBaseTemplate(user, greeting_image).save_preview_image(temp_file_path)
    return temp_file_path, greeting_name


def get_image_bytes(user, greeting_id):
    greeting = Greeting.objects.get(pk=greeting_id)
    greeting_image = greeting.image
    greeting_name = greeting.name
    img_bytes = GreetingBaseTemplate(user, greeting_image).get_preview_image_bytes()
    return img_bytes


def send_wati_message(user, greeting_id):
    image_bytes = get_image_bytes(user, greeting_id)
    receiver = user.profile.phone_number

    TOKEN = settings.WATI_TOKEN
    ENDPOINT = settings.WATI_ENDPOINT
    # PHONE_NUMBER = settings.WATI_PHONE_NUMBER
    import requests
    url = f"https://{ENDPOINT}/api/v1/sendSessionFile/{receiver}"
    # files = [
    #     ('file', (file_path.split(os.sep)[-1], open(file_path, 'rb'), 'image/jpeg'))
    # ]
    files = {
        "image_name": image_bytes
    }
    headers = {
        'Authorization': TOKEN,
    }
    # response = requests.request(
    #     "POST", url, headers=headers, files=files)
    response = requests.request(
        "POST", url, headers=headers)
    print(response.text)


def send_greeting_to_user(user, greeting_id):
    image_path, greeting_name = get_preview_image(user, greeting_id)
    receiver = "whatsapp:+91" + user.profile.phone_number
    content = "Hi!\nIt's a happy day today\nEnjoy!\n-Auretics - A Team "
    result_message = client.messages.create(
        from_=from_number,
        to=receiver,
        body=content,
        media_url=["https://auretics.com/images/mail/onion_oil.jpg"]
    )
    print(result_message.body)


def is_message_triggered(user):
    current_time = datetime.datetime.now()
    user_pref_time = user.preffered_time
    if not user_pref_time:
        if current_time.time() > datetime.time(hour=9):
            return True
        else:
            return False

    if user_pref_time > current_time:
        return True
    else:
        return False


def send_wa_to_list(user_list, greeting_id):
    phone_nums = ['9737643838', '8866786647']
    for phone_number in phone_nums:
        if is_message_triggered(user):
            send_greeting_to_user(user, greeting_id)


def send_wa_to_mock_list(greeting_id):
    user_list = User.objects.all()[:3]
    user_list = get_mock_user_list(user_list)
    for user in user_list:
        send_greeting_to_user(user, greeting_id)


def get_mock_user_list(user_list):
    # phone_nums = ['9737643838', '8866786647', '9999112999']
    phone_nums = ['9737643838', '8866786647']
    for i, user in enumerate(user_list):
        user.profile.phone_number = phone_nums[i]
    return user_list


def upload_file_to_wassenger_(file):
    import requests

    filepath = Greeting.objects.get(pk=greeting_id).image.path
    apikey = settings.WASSENGER_TOKEN

    files = {'file': open(filepath, 'rb')}

    # Upload file
    response = requests.post('https://api.wassenger.com/v1/files', files=files)

    if response.status_code >= 400:
        print('Request failed with invalid status:', response.status_code)
    else:
        json = response.json()
        file_id = json[0]['id']
        print('File uploaded successfully with ID:', file_id)


if __name__ == '__main__':
    class User:
        pass


    phone_nums = ['9737643838', '8866786647']
    user_list = []
    for i in range(2):
        user = User()

        user.profile.phone_number = phone_nums[i]
        user.referralcode.referral_code = "798754545" + str(i)
        user.profile.first_name = "First"
        user.profile.last_name = "Last" + str(i)
        user_list.append(user)

    send_wa_to_list(user_list, 4)
