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

	def create_comment(self, comment=None):
		"""
		When testing parent and tree structures of threaded 
		comments, it's convinient to generate comments and not
		have to worry about filling in other (necessary) fields.
		"""
		new_comment = Comment(author=self.user, content="test_content",
				parent=comment, thread=self.thread)
		new_comment.save()
		return new_comment

class TestCommentsTree(TestBase):
	"""
	Test class for testing comments.
	"""

	def testGetChildren(self):
		comment = self.create_comment()
		assert comment.parent == None

		second_comment = self.create_comment(comment)
		assert second_comment.parent == comment
		
		children = comment.get_children()
		assert len(children) == 1
		assert children[0] == second_comment

		further_children = second_comment.get_children()
		assert len(further_children) == 0

		third_comment = self.create_comment(second_comment)
		fourth_comment= self.create_comment(third_comment)
		sibling_of_third = self.create_comment(second_comment)

		expecting_two_children = second_comment.get_children()
		assert len(expecting_two_children) == 2
		assert third_comment in expecting_two_children
		assert sibling_of_third in expecting_two_children

		thirds_children = third_comment.get_children()
		assert len(thirds_children) == 1
		assert fourth_comment in thirds_children

	def testGetTree(self):
		# Create a small testable tree structure

		self.testGetChildren()
		assert Comment.objects.count() == 5

		



