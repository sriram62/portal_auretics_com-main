from django.core.management import BaseCommand

from notify.models import NoticeTemplate


class Command(BaseCommand):
    help = 'Send notification from template'

    def handle(self, *args, **options):
        NoticeTemplate.send_notification('on_account_created',
                                         email_data={'var1': 'Abhinav',
                                               'var2': 'Hola Amigo'},
                                         sms_data={'var1': '123123',
                                               'var2': 'asdasd'},
                                         email='theabhinavdev@gmail.com',
                                         phone_number='+919090975571',
                                         send_sms=False,
                                         send_email=True)
