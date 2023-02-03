from django.urls import path
from .views import *

urlpatterns = [
    path('payu/failure', payu_failure, name="payufailure"),
    path('zaakpay/failure', zaakpay_failure, name="zaakpay_failure"),
    path('razorpay/failure', razorpay_failure, name="razorpay_failure"),

]
