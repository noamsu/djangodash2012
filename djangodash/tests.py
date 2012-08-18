from django.test import TestCase
from djangodash.models import *

class TestBase(TestCase):
	"""
	Base class for tests.
	"""
	def setUp(self):
		self.user = User(username="test", password="password")
		self.user.save()
		self.thread = Thread(creator=self.user, 
						     content="test_thread_content")
		self.thread.save()

class TestCommentsTree(TestBase):
	"""
	Test class for testing comments.
	"""

	def testGetChildren(self):
		comment = Comment(author=self.user, content="test_content",
					      parent=None, thread=self.thread)
		comment.save()

		assert comment.parent == None
		child_comment = Comment(author=self.user, content="test_content",
								parent=comment, thread=self.thread)
		child_comment.save()

		assert child_comment.parent == comment

		children = comment.get_children()
		assert len(children) == 1
		assert children[0] == child_comment



