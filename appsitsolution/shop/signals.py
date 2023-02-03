from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from shop.models import Order, Address, State


@receiver(post_save, sender=Order)
def manage_initial_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.original_material_center = instance.material_center
        instance.save()


@receiver(pre_save, sender=Address)
def handle_user_address(sender, instance, *args, **kwargs):
    profile = instance.user.profile
    if instance.state:
        state_instance, _ = State.objects.get_or_create(state_name=instance.state.state_name)
        profile.state = state_instance
        profile.save()
