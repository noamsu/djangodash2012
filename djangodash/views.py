from django.shortcuts import render as render_to_response, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse

def render(template, data, request):
	"""
	Wrapper for rendering a response.
	"""
	return render_to_response(request, template, data)

def home(request):
	"""
	Home page.
	"""

	user = request.user

	return render("home.html", 
			{"user":user,
			 "is_logged_in":user.is_authenticated()}, 
			request)

def login(request):
	"""
	Login view.
	"""

	return render("login.html",
		{},
		request)