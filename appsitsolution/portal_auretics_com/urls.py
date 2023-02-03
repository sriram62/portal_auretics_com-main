"""portal_auretics_com URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# from django.conf.urls import url
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('accounts/', include('accounts.urls')),
    path('mlm_admin/', include('mlm_admin.urls')),
    path('distributor/', include('distributor.urls')),
    path('calculation/', include('mlm_calculation.urls')),
    path('business/', include('business.urls')),
    path('realtime/', include('realtime_calculation.urls')),
    # path('realtime_v2/', include('realtime_calculation_v2.urls')),
    path('c_and_f_admin/', include('c_and_f.urls')),
    path('audit/', include('audit.urls')),
    # path('payu/', include('payu_biz.urls')),
    # url(r'^', include('payu_biz.urls')),
    path('mis_reports/', include('mis_reports.urls')),
    path('payment/', include('payment_gateway.urls')),
    path('crm/', include('crm.urls')),
    path('pyjama/', include('pyjama.urls')),
]

handler404 = 'shop.views.error_404_view'

"""for Loading Static files in django """

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

"""End Of  Loading Static files in django """
