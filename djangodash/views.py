from django.shortcuts import render as render_to_response, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt

from djangodash.forms import *
from djangodash.models import *

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

	if request.method == "POST":
		if not user.is_authenticated():
			return redirect(reverse("home"))

		form = ThreadForm(request.POST)
		if form.is_valid():
			# Create a new thread
			thread_content = form.cleaned_data["content"]

			new_thread = Thread(content=thread_content,
							    creator=user)

			new_thread.save()
	else:
		form = ThreadForm()

	# Get all threads
	threads = Thread.objects.all() 

	return render("home.html", 
			{"user":user,
			 "is_logged_in":user.is_authenticated(),
			 "threads":threads,
			 "form":form}, 
			request)

def thread(request, thread_id):
	"""
	Page for a thread. This page will contain all the comments
	assosiated with the given thread.
	"""

	# Get the thread
	try:
		thread = Thread.objects.get(id=thread_id)
	except Thread.DoesNotExist:
		raise Http404()

	top_comments = Comment.objects.filter(thread=thread, parent=None)
	structure = [t.get_tree(t) for t in top_comments]

	return render("thread.html",
		{"thread":thread,
		 "structure":structure},
		request)

# make this require a POST request
# make login required
@csrf_exempt
def add_comment(request):
	"""
	Add a new comment.
	"""

	user = request.user

	thread_id = request.POST.get("thread_id")
	thread = Thread.objects.get(id=thread_id)
	comment_id = request.POST.get("comment_id")

	comment = None
	if comment_id:
		comment = Comment.objects.get(id=comment_id)

	form = CommentForm(request.POST)
	if form.is_valid():
		content = form.cleaned_data["content"]
		new_comment = Comment(author=user,
							  content=content,
							  parent=comment,
							  thread=thread)
		new_comment.save()

	# Redirect back to the thread 
	return redirect(reverse("thread", kwargs={"thread_id": int(thread_id)}))

	return HttpResponse("hello")

def user_profile(request, username):
	"""
	Show the profile page for a user.
	"""
	user = request.user

	return render("profile.html", {
		"user":user
		}, request)

def login(request):
	"""
	Display the login page and log the user in.
	"""

	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data["username"]
			password = form.cleaned_data["password"]

			user = authenticate(username=username,
				         password=password)

			if user is not None:
				auth_login(request, user)
				return redirect(reverse("home"))

			# Incorrect username/password
			return render("login.html", {"form":form,
										 "login_error":True}, request)

		# Invalid form
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
				authenticate(username=username,
						     password=password)
				auth_login(request)
				return redirect(reverse("home"))
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
