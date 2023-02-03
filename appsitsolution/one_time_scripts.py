from shop.models import Material_center


def manage_mc_and_state():
    Material_center.objects.filter(advisory_owned='Yes').update(associated_states=None)