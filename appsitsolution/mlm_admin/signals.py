from django.db.models import Q
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from shop.models import Material_center, State


@receiver(m2m_changed, sender=Material_center.associated_states.through)
def handle_state(sender, instance, action, pk_set, *args, **kwargs):
    if instance.advisory_owned == 'YES':
        return
    frontend_mc_qs = Material_center.objects.filter(frontend=True)
    if frontend_mc_qs.exists():
        frontend_mc = frontend_mc_qs.first()
        if frontend_mc.pk == instance.pk:
            return
        if action == 'post_add':
            for pk in pk_set:
                frontend_mc.associated_states.remove(State.objects.get(pk=pk))
        if action == 'post_remove':
            for pk in pk_set:
                frontend_mc.associated_states.add(State.objects.get(pk=pk))
        if State.objects.filter(associated_material_center=None).exists():
            frontend_mc.associated_states.set(
                State.objects.filter(Q(associated_material_center=frontend_mc) | Q(associated_material_center=None)))
        # print(action, args,kwargs)
        print(action)


