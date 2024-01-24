from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import User


@receiver(post_save, sender=Group)
def add_superuser_to_created_group(sender, instance, created, **kwargs):
    if created:
        superusers = User.objects.filter(is_superuser=True)
        instance.user_set.add(*superusers)      
