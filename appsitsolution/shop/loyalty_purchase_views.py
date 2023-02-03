from .utils import has_enough_pv_to_enable_loyalty_purchase
from .views import *


def enable_loyalty_purchase(request):
    from shop.utils import is_eligible_for_loyalty_purchase
    if has_enough_pv_to_enable_loyalty_purchase(request):
        request.session['loyalty_purchase_enabled'] = True
    is_eligible_for_loyalty_purchase(request, group_checkout=None)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def disable_loyalty_purchase(request):
    del request.session['loyalty_purchase_enabled']
    cart.get_all_cart_items(request).filter(is_loyalty_purchase_cart=True).delete()
    is_eligible_for_loyalty_purchase(request, group_checkout=None)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
