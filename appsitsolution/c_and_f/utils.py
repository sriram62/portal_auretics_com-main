from shop.models import Order, Material_center


def get_order_list_for_cnf_admin(user):
    return Order.objects.filter(material_center=Material_center.objects.filter(advisor_registration_number=user, company_depot='YES').first())
