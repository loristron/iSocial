from .models import Profile, Relationship

def profile_pic(request):
	if request.user.is_authenticated:
		profile_obj = Profile.objects.get(user=request.user)
		pic 		= profile_obj.avatar
		#returns a dictionary
		return {'picture': pic,}
	#has to return a empty dictionary to users not authenticated
	return {}

def number_invatations_received(request):
	if request.user.is_authenticated:
		profile_obj = Profile.objects.get(user=request.user)
		qs_count 	= Relationship.objects.invatations_received(profile_obj).count()
		return {
			'invites_number': qs_count,
		}
	return {}
