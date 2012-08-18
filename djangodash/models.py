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
		"""
		Return the immediate children of the current comment.
		"""
		return self.comment_set.filter(parent=self)

	def get_tree(self, c):
		"""
		Recursively generate a threaded comment tree.
		"""
		return [c, [self.get_tree(x) for x in c.get_children()]]

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


class Vote(models.Model):
	"""
	Represents a vote. 
	A vote object is created every time a user votes on a comment.
	It is used to keep track of the comments that users has voted on.
	"""

	user = models.ForeignKey(User)
	comment = models.ForeignKey(Comment)

	# A Vote can represent an upvote or a downvote.

	VOTE_DOWN = 0
	VOTE_UP = 1

	VOTE_TYPES = (
		(VOTE_UP, "Voted Up"),
		(VOTE_DOWN, "Voted Down")
	)

	vote_type = models.IntegerField(choices=VOTE_TYPES)





	

