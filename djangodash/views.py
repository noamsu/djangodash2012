from django.shortcuts import render as render_to_response, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse

from djangodash.forms import LoginForm

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
	Display the login page and log the user in.
	"""

	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data["username"]
			password = form.cleaned_data["password"]
			print username, password
		return render("login.html",{"form":form}, request)

	else:
		assert request.method == "GET"
		form = LoginForm()

	return render("login.html",
		{"form":form},
		request)