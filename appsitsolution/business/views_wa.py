import mimetypes
import os
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from mlm_admin.greetings_image_module import GreetingBaseTemplate
from mlm_admin.models import Greeting


@login_required(login_url='home')
def change_avatar(request):
    if request.method == 'POST':
        user_profile = request.user.profile
        old_avatar = user_profile.avatar
        try:
            avatar = request.FILES.get('avatar_image')
            if avatar:
                user_profile.avatar = avatar
                user_profile.save()
                messages.add_message(request, messages.SUCCESS, "Profile Picture Changed")
            else:
                messages.add_message(request, messages.ERROR, "Something went wrong. Please Try Again")
        except:
            user_profile.avatar = old_avatar
            user_profile.save()
            messages.add_message(request, messages.ERROR, "Something went wrong. Please Try Again")

    return render(request, 'business/add_avatar.html')


@login_required(login_url='home')
def view_greetings(request):
    greetings = Greeting.objects.filter(status='ACTIVE')

    return render(request, 'business/view_greetings.html', context={'greetings': greetings})


@login_required(login_url='home')
def download_greeting(request, greeting_id):
    greeting = Greeting.objects.get(pk=greeting_id)
    file_name = uuid.uuid4().hex + ".jpg"
    tmp_folder = os.path.join(os.getcwd(), "media", "greeting_images", "tmp")
    if not os.path.isdir(tmp_folder):
        os.mkdir(tmp_folder)
    temp_file_path = os.path.join(tmp_folder, file_name)
    # print(temp_file_path)
    # print(os.path.isdir(temp_file_path))
    GreetingBaseTemplate(request.user, greeting.image).save_preview_image(temp_file_path)
    mime_type, _ = mimetypes.guess_type(temp_file_path)
    with open(temp_file_path, 'rb') as fl:
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = f"attachment; filename={file_name}"
        return response
