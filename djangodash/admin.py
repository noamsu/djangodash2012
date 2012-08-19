from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from djangodash.models import *

class ThreadAdmin(admin.ModelAdmin):
	pass

class CommentAdmin(admin.ModelAdmin):
	pass

class VoteAdmin(admin.ModelAdmin):
	pass

admin.site.register(Vote, VoteAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Thread, ThreadAdmin)

