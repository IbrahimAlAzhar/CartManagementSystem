# signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Transaction

@receiver(post_save, sender=User)
def create_transaction_for_new_user(sender, instance, created, **kwargs):
    if created:
        Transaction.objects.create(
            _id=instance.username,  # Assuming you use the username as a primary key
            name=instance.username,
            # Set other fields with default or specified values
        )
