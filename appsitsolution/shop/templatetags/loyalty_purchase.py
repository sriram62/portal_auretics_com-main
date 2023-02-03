from django import template

register = template.Library()


@register.filter(name='non_loyalty_items')
def non_loyalty_items(cart_items, request):
    loyalty_items = []
    # if not request.session.get('loyalty_purchase_enabled', False):
    #     return cart_items
    if cart_items:
        for ci in cart_items:
            if not ci.is_loyalty_purchase_cart:
                loyalty_items.append(ci)
    return loyalty_items


@register.filter(name='loyalty_items')
def loyalty_items(cart_items, request):
    loyalty_items = []
    print(request)
    for ci in cart_items:
        if ci.is_loyalty_purchase_cart:
            loyalty_items.append(ci)
    return loyalty_items
