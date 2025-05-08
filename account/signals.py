from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import User


# This signal is triggered when a registered user is deleted. 
# It updates the registered field of the ID record associated with the user(from registered to unregistered).
