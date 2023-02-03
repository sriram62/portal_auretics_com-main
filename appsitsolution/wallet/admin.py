from django.contrib import admin
from .models import Wallet, Transaction, JuspayDipostedData

# Register your models here.
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_balance', 'created_at']
    search_fields=('id', 'user', 'created_at')

admin.site.register(Wallet, WalletAdmin)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'value','running_balance', 'created_at']
    search_fields=('id', 'wallet', 'created_at')

admin.site.register(Transaction, TransactionAdmin)


class JuspayDipostedDataAdmin(admin.ModelAdmin):
    list_display = ['id','order_id', 'created_at']
    search_fields=('id', 'order_id', 'created_at')

admin.site.register(JuspayDipostedData, JuspayDipostedDataAdmin)
