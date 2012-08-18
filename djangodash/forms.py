from django import forms
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
	"""
	Form for loggin in.
	"""
	username = forms.CharField(max_length=100)
	password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=100)

class ThreadForm(forms.Form):
	"""
	Form for adding a new thread.
	"""
	content = forms.CharField(label='New Thread', 
                              widget=forms.Textarea(),
                              required=True)
