from django.test import TestCase
from djangodash.models import *

from django.test.client import Client
from django.core.urlresolvers import reverse

class TestBase(TestCase):
	"""
	Base class for tests.
	"""
	def setUp(self):
		self.user = User(username="test", password="!")
		self.user.set_password("password")
		self.user.save()

		self.user.save()
		self.thread = Thread(creator=self.user, 
						     content="test_thread_content")
		self.thread.save()

		# Client configuration
		self.client = Client()

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

		# Get the single parent comment
		comment = Comment.objects.get(parent=None)

		# Get the entire structure
		s = comment.get_tree(comment)

		# Test the structure. It should look like:
		# [<6>, [[<7>, [[<8>, [[<9>, []]]], <10>, []]]]]

		assert s[0].id == 6
		assert s[1][0][0].id == 7
		assert s[1][0][1][0][0].id == 8
		assert s[1][0][1][0][1][0][0].id == 9
		assert s[1][0][1][1][0].id == 10

class TestVotes(TestBase):
	"""
	Test comment voting.
	"""

	def setUp(self):
		super(TestVotes, self).setUp()
		self.vote_url = "/ajax/vote/"
		self.client.login(username="test", password="password")

	def testVoteUp(self):
		comment = self.create_comment()
		assert comment.votes == 0
		
		response = self.client.post(self.vote_url, {"comment_id":comment.id,
													"action":"up"})

		assert response.status_code == 200

		comment = Comment.objects.get(id=comment.id)
		assert comment.votes == 1

	def testVoteUpTwice(self):
		# Vote up once
		comment = self.create_comment()
		assert comment.votes == 0

		response = self.client.post(self.vote_url, {"comment_id":comment.id,
													"action":"up"})

		comment = Comment.objects.get(id=comment.id)
		assert comment.votes == 1

		# Vote up again. This should take back the vote
		# and comment.votes should == 0

		response = self.client.post(self.vote_url, {"comment_id":comment.id,
													"action":"up"})
		comment= Comment.objects.get(id=comment.id)
		assert comment.votes == 0

	def testVoteDown(self):
		comment = self.create_comment()
		assert comment.votes == 0
		
		response = self.client.post(self.vote_url, {"comment_id":comment.id,
													"action":"down"})

		assert response.status_code == 200

		comment = Comment.objects.get(id=comment.id)
		assert comment.votes == -1

	def testVoteUpTwice(self):
		# Vote up once
		comment = self.create_comment()
		assert comment.votes == 0

		response = self.client.post(self.vote_url, {"comment_id":comment.id,
													"action":"down"})

		comment = Comment.objects.get(id=comment.id)
		assert comment.votes == -1

		# Vote up again. This should take back the vote
		# and comment.votes should == 0

		response = self.client.post(self.vote_url, {"comment_id":comment.id,
													"action":"down"})
		comment= Comment.objects.get(id=comment.id)
		assert comment.votes == 0


class TestThreads(TestBase):
	"""
	Test class for testing threads.
	"""
	def setUp(self):
		super(TestThreads, self).setUp()
		self.url = "/"
		self.client.login(username="test", password="password")

	def testCreateNewThread(self):
		threads = Thread.objects.all()
		assert len(threads) == 1
		assert threads[0].content == "test_thread_content"

		# Create a new thread 

		response = self.client.post(self.url, {"content":"new thread"})

		assert response.status_code == 302

		threads = Thread.objects.all()
		assert len(threads) == 2
		assert threads[1].content == "new thread"
		assert threads[1].creator == self.user

	def testDeleteThread(self):
		threads = Thread.objects.all()
		assert len(threads) == 1
		thread = threads[0]

		# Delete the thread

		delete_url = "/delete"
		self.client.post(delete_url, {"type":"thread",
								      "_id":thread.pk})

		threads = Thread.objects.all()
		assert len(threads) == 0

	def testDeleteNonExistingThreads(self):
		threads = Thread.objects.all()
		assert len(threads) == 1

		thread = threads[0]

		# Delete a thread that does not exist
		delete_url = "/delete"
		response = self.client.post(delete_url, {"type":"thread",
									  "_id":"11109977000"})

		assert response.status_code == 302

		# There should still be one thread
		threads = Thread.objects.all()
		assert len(threads) == 1

	def testCannotDeleteSomeoneElsesThread(self):
		threads = Thread.objects.all()
		assert len(threads) == 1
		thread = threads[0]

		new_user = User(username="new", password="!")
		new_user.set_password("user")
		new_user.save()

		assert new_user != thread.creator

		# Login as the new user
		self.client.login(userame="new", password="user")

		# Try to delete another user's thread
		delete_url = "/delete"
		response = self.client.post(delete_url, {"type":"thread",
									  "_id":"11109977000"})

		assert response.status_code == 302

		# The thread should still be there
		threads = Thread.objects.all()
		assert len(threads) == 1

class TestFollowing(TestBase):
    """
    Test the follower/following system.
    """
    def setUp(self):
        super(TestFollowing, self).setUp()

        self.url = "/follow"
        self.client.login(username="test", password="password")

    def create_new_user(self, username, password):
        user = User(username=username, password="!")
        user.set_password(password)
        user.save()
        return user

    def testFollowUser(self):
        user_one = self.user
        user_two = self.create_new_user("u","p")

        assert user_one != user_two
        assert user_one.get_profile().is_following(user_two) == False

        user_two_id = user_two.id
        self.client.post(self.url, {"profile_user_id":user_two_id,
                                    "action":"follow"})

        assert user_one.get_profile().is_following(user_two) == True

    def testFollowSeveralUsers(self):
        user_one = self.create_new_user("1","1")
        user_two = self.create_new_user("2","2")
        user_three = self.create_new_user("3","3")
        user_four = self.create_new_user("4","4")

        # User one should follow user three
        # User three should follow user four
        # User two should follow user three
        # User three should follow user two

        assert user_one != user_two != user_three != user_four

        assert user_one.get_profile().is_following(user_two) == False
        assert user_three.get_profile().is_following(user_four) == False
        assert user_two.get_profile().is_following(user_three) == False
        assert user_three.get_profile().is_following(user_two) == False

        self.client.login(username="1", password="1")
        self.client.post(self.url,
                        {"profile_user_id":user_three.id,
                         "action":"follow"})

        # Login as user one
        self.client.login(username="3", password="3")
        self.client.post(self.url,
                        {"profile_user_id":user_four.id,
                         "action":"follow"})

        # Login as user two
        self.client.login(username="2", password="2")
        self.client.post(self.url,
                        {"profile_user_id":user_three.id,
                         "action":"follow"})

        # Login as user three
        self.client.login(username="3", password="3")
        self.client.post(self.url,
                        {"profile_user_id":user_two.id,
                         "action":"follow"})

        assert user_one.get_profile().is_following(user_three) == True
        assert user_three.get_profile().is_following(user_four) == True
        assert user_two.get_profile().is_following(user_three) == True
        assert user_three.get_profile().is_following(user_two) == True


    def testFollowUserThatDoesNotExist(self):
        bad_id = 0
        response = self.client.post(self.url, {"profile_user_id":bad_id,
                                               "action":"follow"})



        assert response.status_code == 302


    def testUnfollowUser(self):
        user_one = self.user
        user_two = self.create_new_user("2","2")
        assert user_one != user_two

        user_two_id = user_two.id
        self.client.post(self.url,
                            {"profile_user_id":user_two_id,
                             "action":"follow"})

        assert user_one.get_profile().is_following(user_two)

        self.client.post(self.url,
                            {"profile_user_id":user_two_id,
                             "action":"unfollow"})

        assert user_one.get_profile().is_following(user_two) == False