from . import cart


def cart_item_count(request):
    item_count = cart.item_count(request)
    a_sub_total = cart.a_subtotal(request)
    return {'cart_item_count' : item_count,'a_sub_total':a_sub_total }
