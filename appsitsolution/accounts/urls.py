
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    # path('register/', views.registerPage, name="register"),sign_up
    # path('register/', views.sign_up, name="register"),validate_ref
   # path('validate_ref/', views.validate_ref, name="validate_ref"),
    #path('register1/', views.register1, name="register1"),
    path('register/', views.new_sign_up, name="register"),
    path('register_auto/', views.new_sign_up_auto, name="register_auto"),
    path('ajax/validate_form/', views.validate_data, name='validate_form'),
    path('login', views.user_login, name="login"),
    path('send_otp', views.send_otp, name="send_otp"),
    path('logout/', views.logoutUser, name="logout"),
    path('profile/', views.profile, name='profile'),
    path('wallet/', views.Wallet_view, name='wallet'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change_password/', views.change_password, name='change_password'),
    path('profile/recharge', views.recharge, name='recharge'),
    path('profile/withdraw/', views.withdraw, name='withdraw'),
    path('userlogin',views.user_login2, name="userlogin"),
    path('sms',views.sendsms, name="sms"),
    path('check_box',views.check_box, name="check_box"),

    # Password reset views

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name= 'registration/password_reset_form.html'), name="password_reset" ),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name= 'registration/password_reset_done.html'), name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name= 'registration/password_reset_confirm.html'), name="password_reset_confirm"),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name= 'registration/password_reset_complete.html'), name="password_reset_complete"),
    # path('reset/<uidb64>/<token>',
    #      auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
    #      name='password_reset_confirm'),
    # path('password_reset_complete',
    #      auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
    #      name='password_reset_complete'),
    path('test',views.test,name='test'),
    path('otp_login/',views.otp_send,name='otp_login'),
    path('change_passcode/<int:myid>',views.admin_password_change,name='change_passcode'),
    path('userchange_passcode/',views.user_password_change,name='user_change_passcode'),

    path('track_order/<int:myid>',views.track_order,name="track_order"),
    path('new-reg-user-login/',views.new_reg_user_login,name="new_reg_user_login"),
    # path('mobile-verification/<str:mobile_number>',views.mobile_verification_otp,name="mobile_verification"),
    path('mobile-verification/',views.mobile_verification_otp,name="mobile_verification"),
    path('PAN-verification/',views.profile_pan,name="profile_pan_verification"),
    path('bank-verification/',views.profile_bank,name="profile_bank_verification"),

    


]
