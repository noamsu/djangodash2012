from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from djangodash.models import *

class ThreadAdmin(admin.ModelAdmin):
	pass

admin.site.register(Thread, ThreadAdmin)
