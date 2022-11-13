from django.test import TestCase
from rest_framework.test import APIClient
from .models import * 
from string import ascii_uppercase, digits
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
import time


##################
# HELPER CLASSES #
##################

from django.apps import apps
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

class TestMigrations(TestCase):
	@property
	def app(self):
		return apps.get_containing_app_config(type(self).__module__).name

	migrate_from = None
	migrate_to = None

	def setUp(self):
		assert self.migrate_from and self.migrate_to, \
			"TestCase '{}' must define migrate_from and migrate_to     properties".format(type(self).__name__)
		self.migrate_from = [(self.app, self.migrate_from)]
		self.migrate_to = [(self.app, self.migrate_to)]
		executor = MigrationExecutor(connection)
		old_apps = executor.loader.project_state(self.migrate_from).apps

		# Reverse to the original migration
		executor.migrate(self.migrate_from)

		self.setUpBeforeMigration(old_apps)

		# Run the migration to test
		executor = MigrationExecutor(connection)
		executor.loader.build_graph()  # reload.
		executor.migrate(self.migrate_to)

		self.apps = executor.loader.project_state(self.migrate_to).apps

	def setUpBeforeMigration(self, apps):
		pass


####################
# FIELD GENERATORS #
####################

def random_datetime(start=None, end=None):
	# Get a time at a proportion of a range of two formatted times.
	f = '%Y-%d-%mT%H:%M'
	start_date = time.mktime(time.strptime(start, f)) if start else time.mktime(time.strptime(datetime.now().strftime(f), f))
	end_date = time.mktime(time.strptime(end, f)) if end else time.mktime(time.strptime((datetime.now() + timedelta(days=10)).strftime(f), f))
	middle_date = start_date + random.random()/2 * (end_date - start_date)
	return time.strftime(f, time.localtime(middle_date))

def random_date(start=None, end=None):
	# Get a time at a proportion of a range of two formatted times.
	f = '%Y-%d-%m'
	start_date = time.mktime(time.strptime(start, f)) if start else time.mktime(time.strptime(datetime.now().strftime(f), f))
	end_date = time.mktime(time.strptime(end, f)) if end else time.mktime(time.strptime((datetime.now() + timedelta(days=10)).strftime(f), f))
	middle_date = start_date + random.random()/2 * (end_date - start_date)
	return time.strftime(f, time.localtime(middle_date))

def random_text(length=10):
	return ''.join(random.choice(ascii_uppercase) for i in range(length))

def random_number(length=10):
	return ''.join(random.choice(digits) for i in range(length))

def random_object(Model):
	return Model.objects.get(pk=random.choice(Model.objects.values_list('id', flat=True)))

def random_birthday(min_age=18, max_age=50):
	return datetime.now() - relativedelta(years=random.randint(min_age,max_age))

def random_height(min_height=1, max_height=99):
	return random.randint(min_height,max_height)

####################
# MODEL GENERATORS #
####################

def build_country():
	return Country.objects.create(
		name=random_text(5)
		)

def build_province():
	return Province.objects.create(
		name=random_text(5),
		country=build_country()
		)

def build_city():
	return City.objects.create(
		name=random_text(5),
		province=build_province()
		)

def build_genders():
	Gender.objects.bulk_create([
		Gender(name='Male'),
		Gender(name='Female'),
		])

def build_profile(username=None,password=None,first_name=None,last_name=None,birthday=None,description=None,gender=None,orientation=None,show_male=True,show_female=True,height=random_height(),is_hidden=False,is_archived=False,match_count=0):
	profile = Profile.objects.create(
		username=username if username else random_text(),
		password=password if password else random_number(),
		first_name=first_name if first_name else random_text(length=5),
		last_name=last_name if last_name else random_text(length=5),
		birthday=birthday if birthday else random_birthday(),
		description=description if description else random_text(length=300),
		gender=gender if gender else random_object(Gender),
		orientation=orientation if orientation else random.choice(Profile.ORIENTATION_CHOICES)[0],
		show_male=show_male,
		show_female=show_female,
		height=height,
		is_hidden=is_hidden,
		is_archived=is_archived,
		match_count=match_count,
		)
	ProfilePicture.objects.bulk_create([
		ProfilePicture(profile=profile,picture='fake_img.jpg',position=0),
		ProfilePicture(profile=profile,picture='fake_img2.jpg',position=1),
		ProfilePicture(profile=profile,picture='fake_img3.jpg',position=2),
		])
	return profile

def build_like(liker,subject,is_rejected=False,is_match=False,is_active=False):
	return Like.objects.create(
		liker=liker,
		subject=subject,
		is_rejected=is_rejected,
		is_match=is_match,
		is_active=is_active
		)

def build_swipedeck():
	g_male = Gender.objects.filter(name__iexact='Male').first()
	g_female = Gender.objects.filter(name__iexact='Female').first()
	age_20 = random_birthday(min_age=20, max_age=20)
	return [
		build_profile(gender=g_male,birthday=age_20,orientation=Profile.STRAIGHT),#Generic straight male
		build_profile(gender=g_female,birthday=age_20,orientation=Profile.STRAIGHT),#Generic straight female
		*[build_profile() for i in range(30)]#Additional random profiles
	]
	

###################
# MIGRATION TESTS #
###################
	
class MatchCountTestCase(TestMigrations):
	migrate_from = '0068_auto_20220523_1602'
	migrate_to = '0069_auto_20220524_1323'

	def setUpBeforeMigration(self, apps):
		Profile = apps.get_model('api', 'Profile')
		build_genders()
		self.profile = build_profile()
		self.different_profile = build_profile()
		self.different_profile_2 = build_profile()
		self.different_profile_3 = build_profile()
		build_like(self.profile, self.different_profile, is_match=True, is_active=True)#Counted
		build_like(self.profile, self.different_profile_2, is_match=True, is_active=True)#Counted
		build_like(self.profile, self.different_profile_3)#Not Counted
		build_like(self.different_profile, self.different_profile_2, is_match=True, is_active=False)#Not Counted
		build_like(self.different_profile, self.different_profile_3, is_rejected=True)#Not Counted
		build_like(self.different_profile_3, self.different_profile_2)#Not Counted

	def test_match_count_migrated(self):
		Profile = apps.get_model('api', 'Profile')
		profile = Profile.objects.get(id=self.profile.id)
		different_profile = Profile.objects.get(id=self.different_profile.id)
		different_profile_2 = Profile.objects.get(id=self.different_profile_2.id)
		different_profile_3 = Profile.objects.get(id=self.different_profile_3.id)
		self.assertEqual(profile.match_count, 2)	
		self.assertEqual(different_profile.match_count, 1)	
		self.assertEqual(different_profile_2.match_count, 1)	
		self.assertEqual(different_profile_3.match_count, 0)	


#############
# API TESTS #
#############

class CityViewSetTest(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_get(self):	
		""" Get a specific profile """
		city = build_city()
		res = self.client.get('/v1/cities/{}/'.format(city.id))
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res.json().get('id'), city.id)


class ProfileViewSetTest(TestCase):
	def setUp(self):
		self.client = APIClient()
		build_genders()
		self.user = build_profile(is_hidden=True)
		self.swipedeck = build_swipedeck()

	def test_get(self):	
		""" Get a specific profile """
		profile = build_profile()
		res = self.client.get('/v1/profiles/{}/'.format(profile.id))
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res.json().get('id'), profile.id)

	def test_get_swipeable_anon(self):
		""" anon shouldnt be able to get a stack """
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertEqual(res.status_code, 403)

	def test_swipeable(self):
		""" client should be able to get a stack """
		self.client.force_authenticate(self.user)
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertEqual(res.status_code, 200)
		self.assertEqual(len(res.json()), min(len(self.swipedeck), 50))

	def test_swipeable_filter_gender_straight_male(self):
		""" Male user should not get other male users """
		g_male = Gender.objects.filter(name__iexact='Male').first()
		straight_male = build_profile(gender=g_male,orientation=Profile.STRAIGHT,show_male=False)
		self.client.force_authenticate(straight_male)
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertNotIn(g_male.id, [r.get('gender') for r in res.json()])

	def test_swipeable_filter_gender_straight_female(self):
		""" Female user should not get other female users """
		g_female = Gender.objects.filter(name__iexact='Female').first()
		straight_female = build_profile(gender=g_female,orientation=Profile.STRAIGHT,show_female=False)
		self.client.force_authenticate(straight_female)
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertNotIn(g_female.id, [r.get('gender') for r in res.json()])

	def test_swipeable_filter_match_limit(self):
		""" Profiles who have 3 matches should not be displayed """
		self.client.force_authenticate(self.user)
		match_limited_profile = build_profile(match_count=3)
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertNotIn(match_limited_profile.id, [r.get('id') for r in res.json()])

	def test_swipeable_filter_previously_swiped(self):
		""" Only profiles the user has not swiped on should be displayed """
		self.client.force_authenticate(self.user)
		right_swipe_profile = build_profile()
		left_swipe_profile = build_profile()
		no_swipe_profile = build_profile()
		build_like(self.user, right_swipe_profile)
		build_like(self.user, left_swipe_profile, is_rejected=True)
		build_like(no_swipe_profile, self.user)#Like created by no_swipe_profile to be on the first page of results
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertNotIn(right_swipe_profile.id, [r.get('id') for r in res.json()])
		self.assertNotIn(left_swipe_profile.id, [r.get('id') for r in res.json()])
		self.assertIn(no_swipe_profile.id, [r.get('id') for r in res.json()])

	def test_swipeable_likes_first(self):
		""" Profiles who have liked you should be displayed first """
		self.client.force_authenticate(self.user)
		liker_profile = build_profile()
		like = build_like(liker_profile, self.user)
		different_profile = build_profile()#Create another so liker isn't on top by default
		different_like = build_like(different_profile, self.user, is_rejected=True)
		res = self.client.get('/v1/profiles/swipeable/')
		first_stack_profile = res.json()[0]
		self.assertEqual(liker_profile.id, first_stack_profile.get('id'))

	def test_swipeable_at_match_limit(self):
		""" Profiles with 3 matches should get no results """
		self.client.force_authenticate(self.user)
		self.user.match_count = 3
		self.user.save()
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res.json(), [])

	def test_swipeable_excludes_already_rejected(self):
		""" Profiles with 3 matches should get no results """
		self.client.force_authenticate(self.user)
		different_profile = build_profile()
		left_swipe = build_like(different_profile, self.user, is_rejected=True)
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertEqual(res.status_code, 200)
		self.assertNotIn(different_profile.id, [r.get('id') for r in res.json()])

	def test_swipeable_running_time(self):
		""" Swipe stack should load in a reasonable amount of time """
		self.client.force_authenticate(self.user)
		for i in range(1000):
			build_profile()

		start_time = time.time()
		res = self.client.get('/v1/profiles/swipeable/')
		self.assertTrue(time.time() - start_time < 0.5)

	def test_swipeable_running_time_stress_test(self):
		""" Swipe stack should load in a reasonable amount of time """
		if False:#Don't run this one every time, toggle here for now.
			self.client.force_authenticate(self.user)
			for i in range(100000):
				build_profile()

			start_time = time.time()
			res = self.client.get('/v1/profiles/swipeable/')
			self.assertTrue(time.time() - start_time < 2)
		pass

	def test_swipe_right(self):
		""" A right swipe should delete duplicate likes, and return a match if the other user has swiped """
		self.client.force_authenticate(self.user)
		subject_profile = build_profile()
		build_like(subject_profile, self.user)
		build_like(subject_profile, self.user)
		build_like(self.user, subject_profile, is_rejected=True)
		build_like(self.user, subject_profile, is_rejected=True)
		res = self.client.get('/v1/profiles/{0}/swipeRight/'.format(subject_profile.id))
		self.assertEqual(res.status_code, 200)
		self.assertTrue(res.json().get('is_match'))
		duplicate_count = (Like.objects.filter(liker=self.user, subject=subject_profile) | Like.objects.filter(liker=subject_profile, subject=self.user)).exclude(id=res.json().get('id')).count()
		self.assertEqual(duplicate_count, 0)

	def test_swipe_left(self):
		""" A left swipe should delete duplicate likes, and return no match """
		self.client.force_authenticate(self.user)
		subject_profile = build_profile()
		build_like(subject_profile, self.user)
		build_like(subject_profile, self.user)
		build_like(self.user, subject_profile, is_rejected=True)
		build_like(self.user, subject_profile, is_rejected=True)
		res = self.client.get('/v1/profiles/{0}/swipeLeft/'.format(subject_profile.id))
		self.assertEqual(res.status_code, 200)
		self.assertFalse(res.json().get('is_match'))
		duplicate_count = (Like.objects.filter(liker=self.user, subject=subject_profile) | Like.objects.filter(liker=subject_profile, subject=self.user)).exclude(id=res.json().get('id')).count()
		self.assertEqual(duplicate_count, 0)

	def test_swipe_right_match_count(self):
		""" A new match should increment a profile's match count """
		self.client.force_authenticate(self.user)
		subject_profile = build_profile()
		build_like(subject_profile, self.user)
		match_count = self.user.match_count
		res = self.client.get('/v1/profiles/{0}/swipeRight/'.format(subject_profile.id))
		self.assertEqual(res.status_code, 200)
		self.assertTrue(res.json().get('is_match'))
		updated_user = Profile.objects.get(pk=self.user.id)
		self.assertEqual(updated_user.match_count, match_count+1)

	def test_swipe_left_match_count(self):
		""" A left swipe should not affect the match count """
		self.client.force_authenticate(self.user)
		subject_profile = build_profile()
		build_like(subject_profile, self.user)
		self.user.match_count = 2
		self.user.save()
		res = self.client.get('/v1/profiles/{0}/swipeLeft/'.format(subject_profile.id))
		self.assertEqual(res.status_code, 200)
		self.assertFalse(res.json().get('is_match'))
		updated_user = Profile.objects.get(pk=self.user.id)
		self.assertEqual(updated_user.match_count, 2)

	def test_delete(self):
		""" Deleting user's account should archive and hide their profile """
		new_user = build_profile()
		self.client.force_authenticate(new_user)
		res = self.client.delete('/v1/profiles/{0}/'.format(new_user.id))
		self.assertEqual(res.status_code, 201)
		updated_user = Profile.objects.get(pk=new_user.id)
		self.assertEqual(updated_user.is_hidden, True)
		self.assertEqual(updated_user.is_archived, True)

	def test_delete_updates_matches(self):
		""" Deleting user's account should reset any active matches """
		self.client.force_authenticate(self.user)
		self.user.match_count = 3
		self.user.save()
		different_profile = build_profile(match_count=1)
		different_profile_2 = build_profile(match_count=1)
		different_profile_3 = build_profile(match_count=1)
		match = build_like(self.user, different_profile, is_match=True, is_active=True)
		match_2 = build_like(different_profile_2, self.user, is_match=True, is_active=True)
		match_3 = build_like(different_profile_3, self.user, is_match=True, is_active=True)
		res = self.client.delete('/v1/profiles/{0}/'.format(self.user.id))
		self.assertEqual(res.status_code, 201)
		updated_user = Profile.objects.get(pk=self.user.id)
		updated_different_profile = Profile.objects.get(pk=different_profile.id)
		updated_different_profile_2 = Profile.objects.get(pk=different_profile_2.id)
		updated_different_profile_3 = Profile.objects.get(pk=different_profile_3.id)
		self.assertEqual(updated_user.match_count, 0)
		self.assertEqual(updated_different_profile.match_count, 0)
		self.assertEqual(updated_different_profile_2.match_count, 0)
		self.assertEqual(updated_different_profile_3.match_count, 0)
		match = Like.objects.get(pk=match.id)
		match_2 = Like.objects.get(pk=match_2.id)
		match_3 = Like.objects.get(pk=match_3.id)
		self.assertEqual(match.is_ended_reason, Like.ACCOUNT_DELETED)
		self.assertEqual(match_2.is_ended_reason, Like.ACCOUNT_DELETED)
		self.assertEqual(match_3.is_ended_reason, Like.ACCOUNT_DELETED)

	def test_clearLikes(self):
		""" clearLikes should only clear a user's unresponded left swipes """
		self.client.force_authenticate(self.user)
		self.user.match_count = 1
		self.user.save()
		different_profile = build_profile(match_count=1)
		match = build_like(self.user, different_profile, is_match=True, is_active=True)
		different_profile_2 = build_profile()
		different_profile_3 = build_profile()
		right_swipe_unresponded = build_like(self.user, different_profile_2)
		left_swipe_unresponded = build_like(self.user, different_profile_2, is_rejected=True)
		right_swipe_responded = build_like(self.user, different_profile_2)
		left_swipe_responded = build_like(self.user, different_profile_2)
		time.sleep(3)
		right_swipe_responded.is_rejected = True
		left_swipe_responded.is_rejected = True
		right_swipe_responded.save()
		left_swipe_responded.save()
		res = self.client.get('/v1/profiles/clearLikes/')
		self.assertEqual(res.status_code, 201)
		right_swipe_unresponded_count = Like.objects.filter(id=right_swipe_unresponded.id).count()
		left_swipe_unresponded_count = Like.objects.filter(id=left_swipe_unresponded.id).count()
		right_swipe_responded_count = Like.objects.filter(id=right_swipe_responded.id).count()
		left_swipe_responded_count = Like.objects.filter(id=left_swipe_responded.id).count()
		self.assertEqual(right_swipe_unresponded_count, 1)
		self.assertEqual(left_swipe_unresponded_count, 0)
		self.assertEqual(right_swipe_responded_count, 1)
		self.assertEqual(left_swipe_responded_count, 1)


class LikeViewSetTest(TestCase):
	def setUp(self):
		self.client = APIClient()
		build_genders()
		self.user = build_profile(is_hidden=True)

	def test_update_matched_match_count(self):
		""" A newly matched Like should increase both user's match_count """
		self.client.force_authenticate(self.user)
		subject_profile = build_profile()
		like = build_like(subject_profile, self.user)
		data = {
			'is_match': True,
			'is_active': True 
		}
		res = self.client.patch('/v1/likes/{0}/'.format(like.id), data=data)
		self.assertEqual(res.status_code, 200)
		updated_like = Like.objects.get(pk=like.id)
		self.assertTrue(updated_like.is_match)
		self.assertTrue(updated_like.is_active)
		updated_user = Profile.objects.get(pk=self.user.id)
		self.assertEqual(updated_user.match_count, 1)

	def test_update_ended_match_count(self):
		""" An ended Like should decrease both user's match_count """
		self.client.force_authenticate(self.user)
		subject_profile = build_profile(match_count=1)
		#like = build_like(subject_profile, self.user, is_match=True, is_active=True)
		like = build_like(subject_profile, self.user)
		like.is_match = True
		like.is_active = True
		like.save()#Updates match_count
		updated_user = Profile.objects.get(pk=self.user.id)
		updated_subject = Profile.objects.get(pk=subject_profile.id)
		self.assertEqual(updated_user.match_count, 1)
		self.assertEqual(updated_subject.match_count, 2)
		data = {
			'is_active': False,
			'is_ended_reason': Like.ADMIN_PURPOSES,
			'is_ended_by': self.user.id
		}
		res = self.client.patch('/v1/likes/{0}/'.format(like.id), data=data)
		self.assertEqual(res.status_code, 200)
		updated_like = Like.objects.get(pk=like.id)
		self.assertTrue(updated_like.is_match)
		self.assertFalse(updated_like.is_active)
		updated_user = Profile.objects.get(pk=self.user.id)
		updated_subject = Profile.objects.get(pk=subject_profile.id)
		self.assertEqual(updated_user.match_count, 0)
		self.assertEqual(updated_subject.match_count, 1)
