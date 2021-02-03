from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship
from .forms import ProfileModelForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q

from posts.models import Like

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin



# Create your views here.
@login_required
def main_profile_view(request):
	profile 		= Profile.objects.get(user=request.user)
	form 			= ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)

	confirm			= False

	if request.method == 'POST':
		if form.is_valid():
			form.save()
			confirm = True


	template_name 	= 'profiles/main_profile.html'
	context 		=	 {
		'page_title': 	'Perfil - '+ profile.first_name,
		'profile'	: profile,
		'form'		: form,
		'confirm'	: confirm,
	}
	return render(request, template_name, context)

@login_required
def invites_received_view(request):
	profile 	= Profile.objects.get(user=request.user)
	qs 			= Relationship.objects.invatations_received(profile)
	result		= list(map(lambda x: x.sender, qs))

	is_empty	= False

	if len(result) == 0:
		is_empty = True

	context = {

		'qs': result,
		'is_empty': is_empty,
	}

	template_name = 'profiles/my-invites.html'

	return render(request, template_name, context)

@login_required
def accept_invatation(request):
	if request.method == 'POST':
		pk 			= request.POST.get('profile_pk')
		sender 		= Profile.objects.get(pk=pk)
		receiver 	= Profile.objects.get(user=request.user)

		relation 	= get_object_or_404(Relationship, sender=sender, receiver=receiver)
		
		if relation.status == 'send':
			relation.status = 'accepted'
			relation.save()

	return redirect('profiles:my-invites-view')

@login_required
def reject_invatation(request):
	if request.method == 'POST':
		pk 			= request.POST.get('profile_pk')
		sender 		= Profile.objects.get(pk=pk)
		receiver 	= Profile.objects.get(user=request.user)

		relation 	= get_object_or_404(Relationship, sender=sender, receiver=receiver)
		relation.delete()

	return redirect('profiles:my-invites-view')

@login_required
def profiles_list_view(request):
	user 		= request.user
	qs			= Profile.objects.get_all_profiles(user)

	context 		= {'qs': qs,}
	template_name 	= 'profiles/profiles-list.html'

	return render(request, template_name, context)

@login_required
def invite_list_view(request):
	user 			= request.user
	qs				= Profile.objects.get_all_profiles_to_invite(user)
	profile 		= Profile.objects.get(user=user)

	rel_r 			= Relationship.objects.filter(sender=profile)
	#relationships were I am the RECEIVER
	rel_s 			= Relationship.objects.filter(receiver=profile)

	relat_sender 	= []
	relat_receiver 	= []

	for item in rel_r:
		relat_receiver.append(item.receiver.user)
	for item in rel_s:
		relat_sender.append(item.sender.user)

	context 		= {
		'qs': qs, 
		'relation_receiver': relat_receiver,
		'relation_sender': relat_sender,
		}
		
	template_name 	= 'profiles/to-invite-list.html'

	return render(request, template_name, context)

@login_required
def friends_list_view(request):
	user 			= request.user
	profile 		= Profile.objects.get(user=user)

	friends 		= profile.get_friends().exclude(username__iexact=user)
	friends_list 	= []

	for q in friends:
		profile = Profile.objects.get(user=q)
		friends_list.append(profile)


	print('2: ', friends_list)

	context 		= {
		'qs': friends_list,
	}
	template_name	= 'profiles/friends-list.html'

	return render(request, template_name, context)





class ProfileDetailView(LoginRequiredMixin, DetailView):
	model 			= Profile
	template_name	= 'profiles/detail.html'

	def get_object(self, **kwargs):
				#overridden the get_object method with basically the same thing, only to see if we can make some 
				#extra logif if we want to 
		slug 			= self.kwargs.get('slug')
		profile 		= Profile.objects.get(slug=slug)
		return profile

	def get_context_data(self, **kwargs):
		context 		= super().get_context_data(**kwargs)
		user 			= User.objects.get(username__iexact=self.request.user)
		profile 		= Profile.objects.get(user=user)
		#relationships were I am the SENDER 
		rel_r 			= Relationship.objects.filter(sender=profile)
		#relationships were I am the RECEIVER
		rel_s 			= Relationship.objects.filter(receiver=profile)

		relat_sender 	= []
		relat_receiver 	= []

		context['postnav'] 				= True


		for item in rel_r:
			relat_receiver.append(item.receiver.user)
		for item in rel_s:
			relat_sender.append(item.sender.user)

		context['relation_sender'] 	= relat_sender
		context['relation_receiver'] = relat_receiver 
									#self.get object = returns profile
									#get_all_authors_posts is a method defined at posts.models
		context['posts']		= self.get_object().get_all_authors_posts()
		context['len_posts']	= True if len(self.get_object().get_all_authors_posts()) > 0 else False 
		
		return context

	#OVERRIDDEN METHOD POST 
	# def post(self, request, *args, **kwargs):
	# 	self.object = self.get_object()
	# 	context = self.get_context_data(object=self.object)
	# 	return self.render_to_response(context)


class ProfileListView(LoginRequiredMixin, ListView):
	# é importante que o nome dessas variáveis seja esse mesmo
	model 				= Profile
	template_name		= 'profiles/profiles-list.html'
	context_object_name	= 'qs'


	#sobrescrevendo o método que já existe para classes
	def get_queryset(self):
		qs 			= Profile.objects.get_all_profiles(self.request.user)
		return  qs

	def get_context_data(self, **kwargs):
		context 			= super().get_context_data(**kwargs)
		user 				= User.objects.get(username__iexact=self.request.user)
		profile 			= Profile.objects.get(user=user)
		rel_r				= Relationship.objects.filter(sender=profile)
		rel_s				= Relationship.objects.filter(receiver=profile)
		context['profile'] 	= profile

		list_relation_sender 	= []
		list_relation_receiver	= []

		for item in rel_r:
			list_relation_receiver.append(item.receiver.user)

		for item in rel_s:
			list_relation_sender.append(item.sender.user)

		context['relation_receiver'] 	= list_relation_receiver
		context['relation_sender']		= list_relation_sender
		context['is_empty']				= False

		if len(self.get_queryset()) == 0:
			context['is_empty'] = True


		return context

@login_required
def send_invatation(request):
	print('send send_invatation')
	if request.method == 'POST':

		pk 			= request.POST.get('profile_pk')
		user 		= request.user

		sender 		= Profile.objects.get(user=user)
		receiver 	= Profile.objects.get(pk=pk)

		rel 		= Relationship.objects.create(sender=sender, receiver=receiver, status='send')

		return redirect(request.META.get('HTTP_REFERER')) #redireciona pra mesma página 

	return redirect('profiles:user-profile')

@login_required
def remove_from_friends(request):
	print('remove invatation')

	if request.method == 'POST':

		pk 			= request.POST.get('profile_pk')
		user 		= request.user

		sender 		= Profile.objects.get(user=user)
		receiver 	= Profile.objects.get(pk=pk)

		rel 		= Relationship.objects.get(
			(Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
			)
		
		rel.delete()
		return redirect(request.META.get('HTTP_REFERER')) #redireciona pra mesma página 

	return redirect('profiles:user-profile')
