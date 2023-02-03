from django.contrib import admin
from .models import RealTimeDetail, RealTimeOrder, RealTimeAudit


admin.site.register(RealTimeDetail)
admin.site.register(RealTimeOrder)
admin.site.register(RealTimeAudit)