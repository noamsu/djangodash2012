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

	return render("home.html", 
			{}, 
			request)
