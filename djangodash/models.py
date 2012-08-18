from django.contrib.auth.models import User
from django.db import models

class Comment(models.Model):
	"""
	Represents a comment.
	"""

	author = models.ForeignKey(User)
	content = models.TextField("Comment body")
	parent = models.ForeignKey("self", null=True, blank=True)
	thread = models.ForeignKey("Thread")
	votes = models.PositiveIntegerField(default=0)

	def get_children(self):
		return self.comment_set.filter(parent=self)

	def __unicode__(self):
		return u"(%s, %s)" % (self.pk, self.content)



class Thread(models.Model):
	"""
	Represents a Thread.
	"""
	creator = models.ForeignKey(User)
	content =  models.TextField("Thread content")

	def __unicode__(self):
		return u"(%s, %s, %s)" % (self.id, self.creator, self.content)