import urllib.parse

import boto3
import requests
# from django.conf import settings
from django.core.mail import send_mail
from django.db import models
# Create your models here.
from django.template import Template, Context
from django.urls import reverse
from django.utils import timezone
from portal_auretics_com import settings
from datetime import datetime


class NoticeTemplate(models.Model):
    template_name = models.CharField(max_length=100)
    template_event = models.CharField(max_length=50)
    # template_type = models.CharField(max_length=50)
    # template_category = models.CharField(max_length=50)
    # for SMS
    sms_sender_id = models.CharField(max_length=100, blank=True, null=True, choices=[(c,c) for c in ['AURTCS']
    ])
    message_template = models.CharField(max_length=500, blank=True, null=True,
                                        help_text='Use {{var}} to declare a variable. Eg. {{var1}}, {{var2}}, {{var3}}, etc.')
    template_id = models.CharField(max_length=50)
    # header = models.CharField(max_length=20)
    # approval_date = models.DateField()
    # for email
    email_sender_id = models.CharField(max_length=100, blank=True, null=True)
    email_subject = models.CharField(max_length=500, blank=True, null=True)
    email_text = models.TextField(blank=True, null=True, help_text='Use {{var}} to declare a variable. Eg. {{var1}}, {{var2}}, {{var3}}, etc.')

    remarks = models.CharField(max_length=200, blank=True, null=True)

    datetime_created = models.DateTimeField(default=timezone.now)
    datetime_updated = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    # Configurations
    service = "AWS"
    entity_id = "1201161952385409194"
    sender_id = "AURTCS"

    # service = "NimbusIT"
    def get_absolute_url(self):
        return reverse('template_view', args=[self.pk])

    def get_rendered_sms(self, data):
        if not isinstance(data, dict):
            return self.email_text
        data = Context(data)
        template = Template(self.message_template)
        rendered = template.render(context=data)
        return rendered

    def send_sms(self, mobile_number, data):
        client = boto3.client(
            "sns",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.region_name,
        )
        # Send your sms message via AWS:
        if self.service == "AWS":
            resp = client.publish(
                PhoneNumber=str(mobile_number),
                Message=self.get_rendered_sms(data),
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {'DataType': 'String', 'StringValue': self.sms_sender_id},
                    'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'},
                    "AWS.MM.SMS.TemplateId": {'DataType': 'String', 'StringValue': self.template_id},
                    "AWS.MM.SMS.EntityId": {'DataType': 'String', 'StringValue': self.entity_id},
                }
            )
            print(resp)
            return True
        elif self.service == "NimbusIT":
            number = str(mobile_number)
            sms = urllib.parse.quote(self.get_rendered_sms(data), safe='')
            data = "https://nimbusit.co.in/api/swsend.asp?username=" + settings.nimbus_username + "&password=" + settings.nimbus_password + "&sender=AURTCS&sendto=" + number + "&entityID=" + self.entity_id + "&templateID=" + self.template_id + "&message=" + sms
            response = requests.get(data)
            # print("Data is:")
            # print(data)
            # print(response)
            return True

        else:
            print("Please enter valid service name in service variable")
            return False

    def get_email_message(self, data):
        if not isinstance(data, dict):
            return self.email_text
        data = Context(data)
        template = Template(self.email_text)
        rendered = template.render(context=data)
        return rendered

    def send_email(self, email, data):
        subject = self.email_subject
        message = self.get_email_message(data)
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email, ]
        print(send_mail(subject, message, email_from, recipient_list, html_message=message))

    @classmethod
    def send_notification(cls,
                          event,
                          email_data={},
                          sms_data={},
                          send_sms=True,
                          send_email=True,
                          email=None,
                          phone_number=None):
        template = cls.objects.filter(template_event=event).first()
        if template:
            if send_sms and phone_number:
                template.send_sms(phone_number, sms_data)
            if send_email and email:
                template.send_email(email, email_data)

    def __str__(self):
        return self.template_name

    class Meta:
        ordering = ['-datetime_updated']
