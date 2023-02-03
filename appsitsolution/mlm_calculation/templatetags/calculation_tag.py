from django import template
from shop.models import *
from accounts.models import *
from mlm_calculation.models import *
register = template.Library()


def test_user(user_id,position):
    referal_users = ReferralCode.objects.get(parent_id_id__pk = user_id,position = position)
    if referal_users.position =='LEFT':
        title = title_qualification_calculation_model.objects.filter(user = referal_users.user_id,calculation_stage = 'Public').latest('pk')
        if title.user_active:
            return  '/static/mlm_admin/images/mlm_dashboard/active_binary.png'
        else:
            return '/static/mlm_admin/images/mlm_dashboard/inactive_binary.png'

    return True
