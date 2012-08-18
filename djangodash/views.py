from django.shortcuts import render as render_to_response, redirect
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

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

			# FIXME continue the login process

		return render("login.html",{"form":form}, request)

	else:
		assert request.method == "GET"
		form = LoginForm()

	return render("login.html",
		{"form":form},
		request)


def register(request):
	"""
	User registration.
	"""

	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			new_user = form.save()
			# Login as the new user
			if new_user.is_active:
				username = form.cleaned_data["username"]
				password = form.cleaned_data["password1"]
				user = authenticate(username=username,
								    password=password)
				login(request)
				return redirect("/")
	else:
		form = UserCreationForm()
	return render("register.html",
		{"form":form},
		request)

def logout(request):
	"""
	Log the user out.
	"""
	print  "made it here"
	auth_logout(request)
	return redirect(reverse("home"))
