from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Relationship


@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
	# print('sender: ', sender)
	# print('instance: ', instance)
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=Relationship)
def post_save_add_friends(sender, instance, created, **kwargs):
	sender_invite 	= instance.sender
	receiver_invite = instance.receiver
	if instance.status == 'accepted':
		sender_invite.friends.add(receiver_invite.user)
		receiver_invite.friends.add(sender_invite.user)
		sender_invite.save()
		receiver_invite.save()

@receiver(pre_delete, sender=Relationship)
def pre_delete_remove_from_friends(sender, instance, **kwargs):
	sender 		= instance.sender
	receiver 	= instance.receiver

	sender.friends.remove(receiver.user)
	receiver.friends.remove(sender.user)

	sender.save()
	receiver.save()