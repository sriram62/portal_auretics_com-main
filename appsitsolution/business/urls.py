from django.urls import path

from . import views, order_summary, views_wa

urlpatterns = [
    path('business', views.business, name="mlm_admin_user_dashboard_1"),
    path('organisation_structure', views.organisation_structure, name="mlm_admin_user_dashboard_11"),
    path('generational_structure', views.generational_structure, name="mlm_admin_user_dashboard_12"),
    path('generational_structure/<int:myid>/<str:referal>', views.more_generational_structure,
         name="mlm_admin_general_stracture"),
    path('organisation_structure/<int:myid>/<str:referal>', views.more_binary, name='mlm_calculation_binary'),
    path('business_summary', views.business_summary, name='mlm_admin_user_dashboard_2'),
    path('income_statement', views.income_statement, name='mlm_admin_user_dashboard_3'),
    path('income_statement/<int:pid>/', views.income_statement_add, name='mlm_admin_user_dashboard_3_add'),
    # TODO
    # path('income_statement/<int:pid>/<int: year>/<int: month>/<str: incomename>', views.income_statement_add, name='mlm_admin_user_dashboard_3_add'),
    path('income_statement_details/<str:detail>/', views.income_statement_details, name='income_statement_details'),

    path('payout_statement', views.payout_statement, name='mlm_admin_user_dashboard_4'),
    path('payout_statement/<int:pid>/', views.payout_statement_add, name='mlm_admin_user_dashboard_4_add'),
    path('loyalty_purchase', views.loyalty_purchase, name='mlm_admin_user_dashboard_5'),
    path('loyalty_purchase/<int:pid>/', views.loyalty_purchase_add, name='mlm_admin_user_dashboard_5_add'),
    path('fund_statement', views.fund_statement, name='mlm_admin_user_dashboard_6'),
    path('fund_statement/<int:pid>/', views.fund_statement_add, name='mlm_admin_user_dashboard_6_add'),
    path('download_certificate', views.download_certificate, name='mlm_admin_user_dashboard_1_download_certificate'),
    path('download_ID_card', views.download_ID_card, name='mlm_admin_user_dashboard_1_download_ID_card'),
    path('upline_details', views.upline_details, name='mlm_admin_user_dashboard_7'),
    path('downline_details', views.downline_details, name='mlm_admin_user_dashboard_8_old'),
    path('downline_details/', views.downline_details, name='mlm_admin_user_dashboard_8'),
    path('downline_details/<int:pid>/', views.downline_details_add, name='user_dashboard_8_add'),
    path('pgxv/', views.pgxv_details, name='user_dashboard_pgxv'),
    path('pgxv/<int:pid>/', views.pgxv_details_add, name='user_dashboard_pgxv_add'),
    path('group_summary', views.group_summary, name='user_dashboard_8_complete'),
    path('group_summary_add/<int:pid>/', views.group_summary_add, name='user_dashboard_8_add_complete'),
    path('circle_details', views.dyn_active_details, name='mlm_admin_user_dashboard_9'),
    path('circle_details/<int:pid>/', views.dyn_active_details_add, name='user_dashboard_9_add'),
    path('dyn_active_details', views.dyn_active_details, name='mlm_admin_user_dashboard_9_active'),
    path('dyn_active_details/<int:pid>/', views.dyn_active_details_add, name='user_dashboard_9_active_add'),
    path('dyn_director_details', views.dyn_director_details, name='mlm_admin_user_dashboard_9_director'),
    path('dyn_director_details/<int:pid>/', views.dyn_director_details_add, name='user_dashboard_9_director_add'),
    path('dyn_tbb_details', views.dyn_tbb_details, name='mlm_admin_user_dashboard_9_tbb'),
    path('dyn_tbb_details/<int:pid>/', views.dyn_tbb_details_add, name='user_dashboard_9_tbb_add'),
    path('commission_wallet', views.commission_wallet, name='mlm_admin_user_dashboard_10'),
    path('welcome_letter', views.welcome_letter, name='user_welcome_letter'),
    path('order_summary', order_summary.order_summary, name='order_summaries'),
    path('order_summary/<int:myid>/', order_summary.order_summary_add, name='order_summary_add'),

    # Whatsapp Greetings Section
    path('change_avatar', views_wa.change_avatar, name='change_avatar'),
    path('view_greetings', views_wa.view_greetings, name='view_greetings'),
    path('download_greeting/<int:greeting_id>', views_wa.download_greeting, name='download_greeting'),

    # path('download_greeting/<int:greeting_id>', views_wa.download_greeting, name='download_greeting'),
]
