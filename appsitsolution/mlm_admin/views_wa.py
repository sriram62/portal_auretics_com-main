import csv
import datetime
import logging
import os
import re

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from mlm_admin.forms import GreetingForm
from mlm_admin.greetings_image_module import GreetingBaseTemplate
from mlm_admin.models import Greeting, BulkMessages, WaConfiguration
from mlm_admin.views import is_mlm_admin
from mlm_admin.wa_sender_api import GreetingSender, WassengerPlugin

User = get_user_model()

user_active_this_month = User.objects.all()
user_active_last_month = User.objects.all()
user_ever_active = User.objects.all()
user_all_green = User.objects.all()
user_kyc_done = User.objects.all()


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def add_greeting(request: HttpRequest):
    form = GreetingForm()
    if request.method == 'POST':
        form = GreetingForm(request.POST, request.FILES)
        if form.is_valid():
            dataform = form.save(commit=False)
            dataform.save()
            messages.success(request, 'Greeting has been added Successfully')
            return redirect('list_greetings')
        else:
            for validation_errors in form.errors.as_data().values():
                #  form.errors.as_data() returns dict{'image': [ValidationError(["The image is 1000 pixel wide. It's supposed to be 1280px wide x 1280px high"])]}
                for error in validation_errors:
                    messages.add_message(request, messages.ERROR, error.message)
            return redirect('add_greeting')
    params = {
        'greeting_form': form,
        'title': 'Add Greeting'
    }

    return render(request, 'mlm_admin/add_greeting.html', context=params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def edit_greeting(request, greeting_id):
    greeting = Greeting.objects.get(pk=greeting_id)
    if request.method == 'POST':
        form = GreetingForm(request.POST, files=request.FILES, instance=greeting)
        if form.is_valid():
            # print("Update the instance here - > not implemented")
            # print(form.instance.image)
            image_path = greeting.image.path
            # TODO: figure out a safe way to delete old image files (Cron rm on a list?)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except PermissionError as permission_error:
                logging.getLogger().error(f"Cannot delete file at {image_path} due to {permission_error}")
            form.save()

            messages.add_message(request, messages.SUCCESS, "Greeting edited")
            return redirect("list_greetings")
        else:
            for validation_errors in form.errors.as_data().values():
                #  form.errors.as_data() returns dict{'image': [ValidationError(["The image is 1000 pixel wide. It's supposed to be 1280px wide x 1280px high"])]}
                for error in validation_errors:
                    messages.add_message(request, messages.ERROR, error.message)
            return redirect('edit_greeting', greeting_id=greeting_id)
    elif request.method == 'GET':
        form = GreetingForm(instance=greeting)
        params = {
            'greeting_form': form,
            'title': 'Edit Greeting'
        }
        return render(request, 'mlm_admin/add_greeting.html', context=params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def delete_greeting(request, greeting_id):
    greeting = Greeting.objects.get(pk=greeting_id)
    # print(f"Deleting greeting {greeting}")
    greeting.delete()
    messages.add_message(request, messages.SUCCESS, "Greeting Deleted")
    return redirect('list_greetings')
    # return HttpResponse("Deleting commenced but not implemented")


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def list_greetings(request, filter=None):
    greetings = Greeting.objects.all()
    return render(request, 'mlm_admin/list_greetings.html', {'greetings': greetings, 'title': 'Greetings List'})


# image_overlay section
@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def set_schedule(request):
    pass


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def preview_greeting(request, greeting_id, user_id=None):
    if request.method == 'GET':
        if user_id:
            user = User.objects.get(pk=user_id)
            # TODO: Arjun Gupta:: get user object that contains full name, ARN/Referral,
            #  Title/Qualification and profile image/avatar
        else:
            user = request.user
        # user.referral_id = "Dummy ID"
        # user.phone_number = "0000000000"
        background_image_path = Greeting.objects.get(pk=greeting_id).image
        preview_image = GreetingBaseTemplate(user, background_image_path).get_preview_image_bytes()
        data = {
            'preview_image': preview_image,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Unable to show preview image'})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def send_mock_wa_messages(request, greeting_id):
    user_list = user_group_1[:2]
    GreetingSender(
        greeting_id=greeting_id,
        message="Hello!\nGreetings form Auretics!",
        user_list=user_list).send_wa_to_mock_list()
    return HttpResponse("Greetings Sent")


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def send_wa_messages(request, greeting_id, user_group=1):
    USER_TYPES = (
        ('A', 'Active this Month'),
        ('B', 'Active last Month'),
        ('C', 'Ever Active'),
        ('D', 'All Green Users'),
        ('E', 'KYC Done'),
    )
    if user_group == 1:
        user_list = user_active_this_month
    elif user_group == 2:
        user_list = user_active_last_month
    elif user_group == 3:
        user_list = user_ever_active
    elif user_group == 4:
        user_list = user_all_green
    elif user_group == 5:
        user_list = user_kyc_done
    else:
        user_list = user_active_this_month

    GreetingSender(greeting_id, user_list).send_wa_to_list()
    # send_wa_to_mock_list(greeting_id)
    messages.add_message(request, messages.SUCCESS, "Messages sent")
    return HttpResponse("Greetings Sent")


@user_passes_test(is_mlm_admin)
def send_todays_greetings(request):
    user_group = request.POST['user_group']
    current_time = datetime.datetime.now()
    active_greetings = Greeting.objects.filter(
        trigger_date__=current_time.year,
        trigger_date__month=current_time.month,
        trigger_date__day=current_time.day,
        status="ACTIVE"
    )
    for greeting in active_greetings:
        send_wa_messages(request, greeting.id, user_group)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def send_bulk_messages(request):
    """
    Function that sends customized messages to multiple numbers from a CSV.
    Message is customized using tags <<field_name>>.
    Parameters
    ----------
    request

    Returns
    -------

    """
    if request.method == "POST":
        contact_list = request.FILES['csv_file_input']
        try:
            image = request.FILES["bulk_image"]
        except:
            image = None
        message = request.POST.get('message')
        decoded_file = contact_list.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        wassenger_obj = WassengerPlugin()
        if image:
            file_id = wassenger_obj.upload_image_binary(image)
        else:
            file_id = None

        for row in reader:
            new_message = message
            for key in row.keys():
                new_message = re.sub(f'<<{key}>>', str(row[key]), new_message)
            number = row['number']
            print(new_message, number)
            response = wassenger_obj.send_text_message(number, new_message, file_id)
            messages_db = BulkMessages()
            date = datetime.date.today()
            messages_db.message = new_message
            messages_db.receiver_number = number
            messages_db.sent_date = date
            messages_db.status = response
            messages_db.file_id = file_id
            messages_db.save()
    context = {'title': 'Send Bulk Messages'}
    return render(request, 'mlm_admin/send_bulk_messages.html', context)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def whatsapp_configuration(request):
    if request.method == "POST":
        token = request.POST.get('token')
        number = request.POST.get('number')
        wa_config = WaConfiguration()
        wa_config.wassenger_token = token
        wa_config.queue_size = number
        wa_config.save()
        print("token & queue size:", token, number)
    context = {'title': 'Whatsapp Configurations'}
    return render(request, 'mlm_admin/WA_configurations.html', context)
