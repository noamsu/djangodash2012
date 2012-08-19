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
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from djangodash.forms import *
from djangodash.models import *

import json

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

        return redirect(reverse("home"))

    else:
        form = ThreadForm()

    # Get all threads
    threads = Thread.objects.all().annotate(comment_count=Count('comment')).order_by("-date")

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

    user = request.user

	# Get the thread
    try:
		thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        raise Http404()

    top_comments = Comment.objects.filter(thread=thread, parent=None)\
                                  .order_by("-votes")
    
    structure = [t.get_tree(t) for t in top_comments]

    user_voting_data = {"positive":[], "negative":[]}
    if user.is_authenticated():
    	# Get all the ids of the comments that the current user
    	# voted on. This is needed to highlight the arrows
    	# of those votes appropriately.
        positive_ids = Vote.objects.filter(user=user,
    	 							   comment__thread=thread, 
    	 							   vote_type=Vote.VOTE_UP) \
    						   .values_list("comment_id", flat=True)


        # Get ids of all negative votes
        negative_ids = Vote.objects.filter(user=user,
    	 							   comment__thread=thread, 
    	 							   vote_type=Vote.VOTE_DOWN) \
    						   .values_list("comment_id", flat=True)

        
        user_voting_data = {
        	"positive":positive_ids,
        	"negative":negative_ids,
        }

    return render("thread.html",
		{"thread":thread,
		 "structure":structure,
		 "user_voting_data":user_voting_data,
		 "is_logged_in":user.is_authenticated(),
		 "user":user},
		request)

# make this require a POST request
@login_required
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
	return redirect(reverse("thread", kwargs={"thread_id": int(thread_id)}) +
                    "#first_%s" % comment.id)

@login_required
@csrf_exempt
# require post
def delete(request):
    """
    Delete a comment or a thread, based on the request.
    """

    user = request.user

    obj_type = request.POST.get("type")
    obj_id = request.POST.get("_id")

    if obj_type == "thread":

        # Get the thread
        try:
            thread = Thread.objects.get(id=int(obj_id))
        except Thread.DoesNotExist:
            return redirect(reverse("home"))

        # We must be the creator of the thread in order to delete it
        if thread.creator != user:
            return redirect(reverse('home'))

        thread.delete()

        # Create redirect url
        scroll_id = int(obj_id) - 1
        append_to_url = "#" + str(scroll_id) if scroll_id > 0 else ""
        return redirect(reverse("home") + append_to_url)

    return redirect(reverse("home"))

# post required
@login_required
@csrf_exempt
def vote(request):
	"""
	Register a vote for a comment.
	"""	

	user = request.user

	comment_id = request.POST.get("comment_id")
	action = request.POST.get("action")

	# Get the comment
	try:
		comment = Comment.objects.get(id=int(comment_id))
	except Comment.DoesNotExist:
		data = json.dumps({"error":True})
		return HttpResponse(data)

	# Does a Vote object exist?
	try:
		vote = Vote.objects.get(user=user,
								comment=comment)
	except Vote.DoesNotExist:
		# We are voting, essentially, for the first time on
		# this comment.

		vote_type = Vote.VOTE_UP

		vote = Vote(user=user, 
					comment=comment,
					vote_type=vote_type)

		# Modify the comment's vote count
		if action == "up":
			comment.votes += 1
		else:
			comment.votes -= 1
		comment.save()

		vote.vote_type = vote.VOTE_UP if action == "up" else Vote.VOTE_DOWN
		vote.save()

		# Return a success response
		data = json.dumps({"error":False,
						   "score":comment.votes,
						   "color_up":1 if action=="up" else 0,
						   "color_down":0 if action=="up" else 1})
		return HttpResponse(data)

	# At this point, a vote exists
	vote_type = vote.vote_type

	# Up and we Up, after this we are neutral
	if vote_type == Vote.VOTE_UP and action == "up":
		# This means we want to take back the vote
		comment.votes -= 1
		comment.save()
		# Back to neutral state, delete Vote object
		vote.delete()
		data = json.dumps({"error":False, "score":comment.votes,
						   "color_up":0, "color_down":0})
		return HttpResponse(data)

	# Up and we Down, after this we are Down
	if vote_type == Vote.VOTE_UP and action=="down":
		comment.votes -= 2
		comment.save()
		vote.vote_type = Vote.VOTE_DOWN
		vote.save()
		data = json.dumps({"error":False, "score":comment.votes,
						   "color_up":0, "color_down":1})
		return HttpResponse(data)

	# Down and we Down, after this we are neutral
	if vote_type == Vote.VOTE_DOWN and action == "down":
		# Take back the down vote
		comment.votes += 1
		comment.save()
		vote.delete()
		data = json.dumps({"error":False, "score":comment.votes,
						   "color_up":0, "color_down":0})
		return HttpResponse(data)

	# Down and we Up, after this we are Up
	if vote_type == Vote.VOTE_DOWN and action == "up":
		comment.votes += 2
		comment.save()
		vote.vote_type = Vote.VOTE_UP
		vote.save()
		data = json.dumps({"error":False, "score":comment.votes,
						   "color_up":1, "color_down":0})
		return HttpResponse(data)


	data = json.dumps({"error":False})
	return HttpResponse(data)

def user_profile(request, username):
    """
    Show the profile page for a user.
    """
    user = request.user

    # Get the user whose profile we are looking at
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404()

    comments = Comment.objects.filter(author=profile_user)


    return render("profile.html", {
		"user":user,
        "comments":comments,
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
	auth_logout(request)
	return redirect(reverse("home"))
