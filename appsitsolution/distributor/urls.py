
from django.urls import path
from . import views
from . import views_new
from . import recalculate

# app_name = "shop"
urlpatterns = [
    path('', views.home, name="distributor_dashboard_home"),
    path('distributor_pending_purchase', views.distributor_purchase_pending, name="distributor_pending_purchase"),
    path('distributor_purchase', views.distributor_purchase, name="distributor_purchase"),
    # path('distributor_sale', views.distributor_sale, name="distributor_sale"),
    path('view_distributor_pending_purchase/<int:myid>', views.view_distributor_pending_purchase, name="view_distributor_pending_purchase"),
    path('view_distributor_purchase/<int:myid>', views.view_distributor_purchase, name="view_distributor_purchase"),
    path('testing', views.testing, name="testing"),
    path('distributor_add_sale', views.distributor_add_sale, name="distributor_add_sale"),
    path('get_user_info', views_new.get_user_info, name="get_user_info"),
    path('get_user_info_for_fmcg_sale', views_new.get_user_info_for_fmcg_sale, name="get_user_info_for_fmcg_sale"),
    # path('distributor_add_loyalty_sale', views.distributor_add_loyalty_sale, name="distributor_add_loyalty_sale"),
    path('distributor_add_loyalty_sale_new', views_new.distributor_add_loyalty_sale_new, name="distributor_add_loyalty_sale_new"),
    path('distributor_add_fmcg_loyalty_sale_new', views_new.distributor_add_fmcg_loyalty_sale_new, name="distributor_add_fmcg_loyalty_sale_new"),
    path('distributor_add_partial_loyalty_sale', views_new.distributor_add_partial_loyalty_sale, name="distributor_add_partial_loyalty_sale"),
    path('distributor_add_partial_loyalty_saleField', views_new.add_partial_loyalty_saleField, name="distributor_add_partial_loyalty_saleField"),
    path('distributor_add_loyalty_saleField', views_new.add_loyalty_saleField, name="distributor_add_loyalty_saleField"),
    path('distributor_add_saleField', views.add_saleField, name="distributor_add_saleField"),
    path('distributor_sale_list', views.distributor_sale_list, name="distributor_sale_list"),
    path('distributor_sale_deleted_list', views.distributor_sale_deleted_list, name="distributor_sale_deleted_list"),
    path('distributor_loyalty_sale_list', views_new.distributor_loyalty_sale_list, name="distributor_loyalty_sale_list"),
    path('distributor_loyalty_deleted_sale_list', views_new.distributor_loyalty_deleted_sale_list, name="distributor_loyalty_deleted_sale_list"),
    path('distributor_view_sale<int:myid>', views.distributor_view_sale, name="distributor_view_sale"),
    path('distributor_edit_sale<int:myid>', views.distributor_edit_sale, name="distributor_edit_sale"),
    path('distributor_edit_loyalty_sale<int:myid>', views_new.distributor_edit_loyalty_sale, name="distributor_edit_loyalty_sale"),
    path('recalculate_everything/<int:myid>', recalculate.recalculate_everything, name="recalculate_everything"),
    path('distributor_delete_sale<int:myid>', views.distributor_delete_sale, name="distributor_delete_sale"),
    path('distributor_delete_loyalty_sale<int:myid>', views_new.distributor_delete_loyalty_sale, name="distributor_delete_loyalty_sale"),
    path('product_detail', views.product_detail, name="D_product_detail"),
    path('D_inventory_details', views.D_inventory_details, name="D_inventory_details"),
    path('D_login', views.D_login, name="D_login"),
    path('edit_saleField', views.edit_saleField, name="edit_saleField"),
    path('download_purchase', views.D_purchase_downlaod, name="D_download_purchase"),
    path('download_sale', views.D_sale_downlaod, name="D_download_sale"),
    path('download_loyalty_sale', views.D_loyalty_sale_download, name="D_loyalty_sale_download"),
    path('downlaod_invoice', views.GeneratePDF.as_view(), name='downlaod_invoice'),
    path('distributor_add_pending_sale/<int:distributor_sale_id>', views.distributor_add_sale, name="distributor_add_pending_sale"),
    path('distributor_sale_list/pending', views.distributor_sale_list_pending, name="distributor_sale_list_pending"),
    path('users_autocomplete', views.users_autocomplete, name='users_autocomplete'),
    path('get_product_based_on_cri_available', views_new.get_product_based_on_cri_available, name='get_product_based_on_cri_available'),
]
