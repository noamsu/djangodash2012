from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver

class Comment(models.Model):
	"""
	Represents a comment.
	"""

	author = models.ForeignKey(User)
	content = models.TextField("Comment body")
	parent = models.ForeignKey("self", null=True, blank=True)
	thread = models.ForeignKey("Thread")
	votes = models.IntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)

	def get_children(self):
		"""
		Return the immediate children of the current comment.
		"""
		return self.comment_set.filter(parent=self).order_by("-votes")

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
	date = models.DateTimeField(auto_now_add=True)

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


class UserProfile(models.Model):
    """
    Store more information about the user.
    """

    user = models.OneToOneField(
        User
    )

    following = models.ManyToManyField(User, 
                                       symmetrical=False,
                                       related_name="followers")

    def display_name(self):
    	if (self.user.first_name + self.user.last_name).strip():
    		return self.user.first_name + " " + self.user.last_name
    	return self.user.username

@receiver(post_save, sender=User, dispatch_uid='userprofile.create')
def create_profile(sender, **kwargs):
    """
    Create a UserProfile when a User is created.
    """
    if kwargs['created']:
        UserProfile(user=kwargs['instance']).save()


