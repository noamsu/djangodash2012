from django.contrib.auth.models import User
from django.db import models

class Thread(models.Model):
	"""
	Represents a Thread.
	"""
	creator = models.ForeignKey(User)
	content =  models.TextField("Thread content")

	def __unicode__(self):
		return u"(%s, %s, %s)" % (self.id, self.creator, self.content)