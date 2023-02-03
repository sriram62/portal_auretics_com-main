from django.shortcuts import render, redirect
from accounts.models import Profile
import traceback
import sys
from django.contrib import messages

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request,*args,**kwargs):
            try:
                # if allowed_roles[1] in request.user.menu_permission.allowed_roles[0]:
                data = allowed_roles[1]
                management = allowed_roles[0]

                if management == 'category_management':
                    permissions = request.user.menu_permission.category_management
                if management == 'product_management':
                    permissions = request.user.menu_permission.product_management
                if management == 'order_management':
                    permissions = request.user.menu_permission.order_management
                if management == 'batch_management':
                    permissions = request.user.menu_permission.batch_management
                if management == 'mc_management':
                    permissions = request.user.menu_permission.mc_management
                if management == 'user_management':
                    permissions = request.user.menu_permission.user_management
                if management == 'purchase_management':
                    permissions = request.user.menu_permission.purchase_management
                if management == 'sale_management':
                    permissions = request.user.menu_permission.sale_management
                if management == 'inventory_management':
                    permissions = request.user.menu_permission.inventory_management
                if management == 'cron_management':
                    permissions = request.user.menu_permission.cron_management
                if management == 'manual_configure':
                    permissions = request.user.menu_permission.manual_configure
                if management == 'manual_verification':
                    permissions = request.user.menu_permission.manual_verification
                if management == 'wallet_configuration':
                    permissions = request.user.menu_permission.wallet_configuration
                if management == 'crm_management':
                    permissions = request.user.menu_permission.crm_management
                if management == 'mis_report':
                    permissions = request.user.menu_permission.mis_report
                if management == 'pincode':
                    permissions = request.user.menu_permission.pincode
                if management == 'calculations':
                    permissions = request.user.menu_permission.calculations
                if management == 'realtime':
                    permissions = request.user.menu_permission.realtime

                
                for i in data:
                    if i in permissions:
                        permission_check = True
                    # return redirect('mlm_admin')
                if permission_check == False:
                    return redirect('mlm_admin')
                else:
                    return view_func(request,*args,**kwargs)
            except Exception as e:
                messages.warning(request, "An error occurred: " + str(e))
                messages.warning(request, "Trace: " + str(traceback.format_exc()))
                return redirect('mlm_admin')
        return wrapper_func
    return decorator