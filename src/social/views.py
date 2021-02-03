from django.http import HttpResponse
from django.shortcuts import render


def home_page_view(request):
	#return HttpResponse('<h3> Hello World </h3>')
	user			= request.user
	template_name 	= 'main/home.html'
	context 		= {
		'usuario'	: user,
		'page_title': 'Home Page',
	}
	return render(request, template_name, context)
