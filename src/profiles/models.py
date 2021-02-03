from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from .utils import get_random_code
from django.shortcuts import reverse
from django.db.models import Q

# Create your models here.

class ProfileManager(models.Manager):

	def get_all_profiles_to_invite(self, sender):
		#we are always the sender
		profiles 	= Profile.objects.all().exclude(user=sender)
		profile 	= Profile.objects.get(user=sender)

		qs			= Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))
		print(qs)
		accepted	= set([])

		for relation in qs:
			if relation.status == 'accepted':
				accepted.add(relation.receiver)
				accepted.add(relation.sender)
		print(accepted)

		available = [profile for profile in profiles if profile not in accepted]
		print(available)

		return available


	#sender and me are basically the same
	def get_all_profiles(self, me):
		profiles = Profile.objects.all().exclude(user=me)
		return profiles

	def get_friends(self, me):
		return self.friends.all().exclude(user=me)


#Cada campo representa uma coluna no banco de dados. As linhas serão chamadas de objetos
class Profile(models.Model):
	first_name 	= models.CharField(max_length=200, blank=True)
	last_name	= models.CharField(max_length=200, blank=True)
	user 		= models.OneToOneField(User, on_delete=models.CASCADE) #Cada usuário só poderá ter um perfil, vinculado ao banco de dados
	bio			= models.TextField(blank=True, default='Ainda não escreveu nada!', max_length=300)
	email		= models.EmailField(max_length=200, blank=True)
	country		= models.CharField(max_length=200, blank=True)
	avatar		= models.ImageField(default='avatar.png', upload_to='')
	#install pillow
	#create media_root
	#find avatar.png
	friends		= models.ManyToManyField(User, blank=True, related_name='friends')
	slug		= models.SlugField(unique=True, blank=True) #será preenchida com o nome, sobrenome ou user
	updated 	= models.DateTimeField(auto_now=True)
	created 	= models.DateTimeField(auto_now_add=True)

	objects 	= ProfileManager()

	def __str__(self):
		return f"{self.user.username}"

	def get_absolute_url(self):
		return reverse("profiles:profile-detail-view", kwargs={"slug": self.slug,})


	def get_friends(self):
		return self.friends.all()

	def get_friends_number(self):
		return self.friends.all().count()

	def get_posts_no(self):
		return self.posts.all().count()

	def get_all_authors_posts(self):
		return self.posts.all()

	def get_likes_given_no(self):
		likes = self.like_set.all()
		total_liked = 0
		for item in likes:
			if item.value=='Like' or item.value=='like':
				total_liked += 1
		return total_liked

	def get_likes_recieved_no(self):
		posts = self.posts.all()
		total_liked = 0
		for item in posts:
			total_liked += item.liked.all().count()
		return total_liked


	def save(self, *args, **kwargs):
			#vamos usar uma lógica pra que mesmo se o mesmo nome e sobrenome for usado, ainda
			#vai ser capaz de usar uma slug baseada no nome de usuário. Essa lógica vai estar dentro do arquivo utils.py
			#dava pra ter feito essa lógica com sinais também, pre ou post save
		aux = False
		if self.first_name and self.last_name:
			to_slug 	= slugify(str(self.first_name) + ' ' + str(self.last_name))
			aux			= Profile.objects.filter(slug=to_slug).exists()
			while aux:
				to_slug = slugify(to_slug + '-' + str(get_random_code()))
				aux		= Profile.objects.filter(slug=to_slug).exists()
		else:
			to_slug		= str(self.user)

		self.slug 		= to_slug
		super().save(*args, **kwargs)




STATUS_CHOICES = (
	('send', 'send'),
	('accepted', 'accepted')
)


class RelationshipManager(models.Manager):
	def invatations_received(self, receiver):
		qs 		= Relationship.objects.filter(receiver=receiver, status='send')
		return qs
		


class Relationship(models.Model):
	sender		= models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
	receiver	= models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
	status		= models.CharField(max_length=8, choices=STATUS_CHOICES)
	updated 	= models.DateTimeField(auto_now=True)
	created 	= models.DateTimeField(auto_now_add=True)

	objects 	= RelationshipManager()

	def __str__(self):
		return f'{self.sender}-{self.receiver}-{self.status}'