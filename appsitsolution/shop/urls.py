from django.urls import path, re_path
from django.views.generic.base import RedirectView

from . import cron
from . import loyalty_purchase_views as lp_views
# from django.conf.urls import url
from . import views

# from .order_id import update_order_id
# app_name = "shop"

urlpatterns = [
    path('', views.home, name="home"),
    path('products_sample/', views.latest_sold_products, name='latest_sold_products'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:user_id>', views.product_list, name='product_list'),
    path('distributor/list/', views.DistributorList.as_view(), name='distributor_list'),
    path('product/<int:product_id>/<slug:product_slug>/', views.show_product, name='product_detail'),
    path('product/<int:product_id>/<slug:product_slug>/<int:user_id>', views.show_product, name='product_detail'),
    # path('product/<int:product_id>/<slug:product_slug>/ target= target=', views.show_product, name='product_detail_t2'),
    # path('product/<int:product_id>/<slug:product_slug>/ target=', views.show_product, name='product_detail_t1'),
    path('products/<int:variant_id>/<int:product_id>/', views.show_product_variant, name='product_variant'),
    path('cart/', views.show_cart, name='show_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_address/', views.update_address, name='update_address'),
    path('about/', views.about_us, name='about'),
    path('ajax/validate_ref/', views.validate_ref, name='validate_ref'),
    path('ajax/validate_email/', views.validate_email, name='validate_email'),
    path('ajax/validate_mobile/', views.validate_mobile, name='validate_mobile'),
    path('product_category/<str:name>/', views.ProductCategory, name='product_category'),
    path('categry_name/<str:cat>/', views.categry_name, name='categry_name'),
    path('category/<str:main_cat>/<str:cat>', views.categry_name, name='categry_name'),
    path('search/', views.product_search, name='search'),
    path('filetr_view/', views.filetr_view, name='filetr_view'),
    path('order_summary/', views.order_summary, name='order_summary'),
    path('order_details/<str:email>', views.order_details, name='order_details'),
    path('contact/', views.contact_us, name='contact'),
    path('return_policy/', views.return_policy, name='return_policy'),
    path('support_policy/', views.support_policy, name='support_policy'),
    path('faqs/', views.faqs, name='faqs'),
    path('size_guide/', views.size_guide, name='size_guide'),
    path('filter_list/', views.filter_list, name='filter_list'),
    path('edit_address/', views.address_edit, name='edit_address'),
    path('js_product/<int:myid>', views.js_product, name='js_product'),
    path('cron/', cron.cron_manu, name='cron'),
    path('ajax_product_qty/',views.ajax_product_quantity, name='ajax_product_quantity'),
    path('payment/',views.payment, name='a'),
    path('demo/',views.payu_demo, name='demo'),
    path('invoice_check/<int:myid>',views.invoice_check, name='shop_invoice_check'),
    path('failure', views.failure, name="failure"),
    path('payu/success', views.payu_success, name="payusuccess"),
    path('clear/cart/',views.clear_cart,name='cart_clear'),
    path('latest_sold_products/',views.LatestSoldProductsView.as_view(), name='latest_sold_products'),

    path('profile/withdraw/checkout', views.withdraw_checkout, name='withdraw_checkout'),
    # path('order_id1', update_order_id, name="order_id1"),
    path('set/distributor/checkout/<int:pk>/', views.SetDistributorCheckout.as_view(), name='set-distributor-checkout'),
    path('remove/distributor/checkout/', views.RemoveDistributorCheckout.as_view(), name='remove-distributor-checkout'),
    path('checkout_distributor/<int:distributor_id>/', views.checkout, name='checkout-distributor'),
    path('add/items/group-checkout/', views.AddItemsGroupCheckout.as_view(), name='new-items-group-checkout'),
    path('group/cart/<str:group_cart>/', views.show_cart, name='group-cart'),
    path('checkout/group_checkout/', views.group_checkout, name='group-checkout'),
    path('pincode', views.pincode_upload_excel, name="pincode_upload_excel"),
    re_path(r'^sitemap.xml', views.sitemap_xml),
    re_path(r'^robots.txt', views.robots_txt),
    path('zaakpay_callback/', views.zaakpay_callback, name="zaakpay_callback"),
    path('razorpay_payment_success/', views.razorpay_success, name='paymenthandler'),

    # if nothing matches we will redirect it to the homepage
    # url(r'^.*$', RedirectView.as_view(url='/static/html/404.html', permanent=False), name='redirect_to_home_page'),
    path('login/', RedirectView.as_view(url='/')),
]
#### loyalty purchase views ###
urlpatterns += [
    path('enable_loyalty_purchase', lp_views.enable_loyalty_purchase, name='enable_loyalty_purchase'),
    path('disable_loyalty_purchase', lp_views.disable_loyalty_purchase, name='disable_loyalty_purchase'),
]

handler404 = 'shop.views.error_404_view'
