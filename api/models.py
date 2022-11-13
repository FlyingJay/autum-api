import os
import subprocess
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models import PointField

from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from phonenumber_field.modelfields import PhoneNumberField

from .notifications import send_notification

#Foreign Key - Many to One
#ManyToMany  - Many to Many
#OneToOne    - OnetoOne (Very Rare) E.g Mapping Django user Default Model to an Extended "User Profile"


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


###############
# Core Classes#
###############

class AutumConfig(TimeStampedModel):
    profile_hide_swipedeck_default = models.BooleanField(help_text='Hide swipedeck before launch?')
    region_lock_distance_toronto = models.IntegerField(default=42, help_text='Max radius around Toronto for launch')

class AutumPhone(TimeStampedModel):
    config = models.ForeignKey('AutumConfig', related_name='autum_phones', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=150, default="", blank=True)
    phone = PhoneNumberField(null=True, blank=True)

class Ambassador(TimeStampedModel):
    class Meta:
        ordering = ['first_name']

    first_name = models.CharField(max_length=150, default="", blank=True)
    last_name = models.CharField(max_length=150, default="", blank=True)


class Signup(TimeStampedModel):
    class Meta:
        ordering = ['-id']

    """ ORIENTATIONS """
    STRAIGHT = 0
    GAY = 1
    LESBIAN = 2
    BISEXUAL = 3
    ASEXUAL = 4
    DEMISEXUAL = 5
    PANSEXUAL = 6
    QUEER = 7
    QUESTIONING = 8

    ORIENTATION_CHOICES = (
        (STRAIGHT, 'STRAIGHT'),
        (GAY, 'GAY'),
        (LESBIAN, 'LESBIAN'),
        (BISEXUAL, 'BISEXUAL'),
        (ASEXUAL, 'ASEXUAL'),
        (DEMISEXUAL, 'DEMISEXUAL'),
        (PANSEXUAL, 'PANSEXUAL'),
        (QUEER, 'QUEER'),
        (QUESTIONING, 'QUESTIONING'),
    )

    NONE = 0
    LEAST = 1
    SOMEWHAT = 2
    VERY = 3

    IMPORTANCE_CHOICES = (
        (NONE, 'NONE'),
        (LEAST, 'LEAST'),
        (SOMEWHAT, 'SOMEWHAT'),
        (VERY, 'VERY'),
        )

    phone = PhoneNumberField(null=True, blank=True)
    first_name = models.CharField(max_length=150, default="", blank=True)
    last_name = models.CharField(max_length=150, default="", blank=True)
    email = models.EmailField(max_length=150, default="", blank=True)
    birthday = models.DateField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True, default=None, help_text='Height (inches)')
    gender = models.ForeignKey('Gender', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    orientation = models.IntegerField(choices=ORIENTATION_CHOICES, blank=True, null=True)
    description = models.CharField(max_length=300, default="", blank=True)
    school = models.ForeignKey('School', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    job = models.CharField(max_length=300, default="", blank=True)
    company = models.CharField(max_length=300, default="", blank=True)
    wants_relationship = models.BooleanField(default=True)
    age_min = models.IntegerField(null=True, blank=True, default=18)
    age_max = models.IntegerField(null=True, blank=True, default=50)
    show_male = models.BooleanField(default=False)
    show_female = models.BooleanField(default=False)
    importance_interests = models.IntegerField(choices=IMPORTANCE_CHOICES, blank=True, null=True)
    referral_code = models.CharField(max_length=255, default=None, blank=True, null=True)

    location = PointField(default=None, null=True, blank=True, geography=True)
    distance_max = models.IntegerField(null=True, blank=True, default=25)
    show_distance_km = models.BooleanField(default=True)

    is_hidden = models.BooleanField(default=False)
    allows_notifications = models.BooleanField(default=True)

    phone_verification_code = models.CharField(max_length=4)
    is_phone_verified = models.BooleanField(default=False)

    def __str__(self):
        if self.phone:
            return str(self.phone) 
        return self.first_name


class Profile(AbstractUser, TimeStampedModel):
    class Meta:
        ordering = ['-id']

    """ ORIENTATIONS """
    STRAIGHT = 0
    GAY = 1
    LESBIAN = 2
    BISEXUAL = 3
    ASEXUAL = 4
    DEMISEXUAL = 5
    PANSEXUAL = 6
    QUEER = 7
    QUESTIONING = 8

    ORIENTATION_CHOICES = (
        (STRAIGHT, 'STRAIGHT'),
        (GAY, 'GAY'),
        (LESBIAN, 'LESBIAN'),
        (BISEXUAL, 'BISEXUAL'),
        (ASEXUAL, 'ASEXUAL'),
        (DEMISEXUAL, 'DEMISEXUAL'),
        (PANSEXUAL, 'PANSEXUAL'),
        (QUEER, 'QUEER'),
        (QUESTIONING, 'QUESTIONING'),
    )

    NONE = 0
    LEAST = 1
    SOMEWHAT = 2
    VERY = 3

    IMPORTANCE_CHOICES = (
        (NONE, 'NONE'),
        (LEAST, 'LEAST'),
        (SOMEWHAT, 'SOMEWHAT'),
        (VERY, 'VERY'),
        )

    phone = PhoneNumberField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, default="", blank=True)
    birthday = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=300, default="", blank=True)
    job = models.CharField(max_length=300, default="", blank=True)
    company = models.CharField(max_length=300, default="", blank=True)
    school = models.ForeignKey('School', default=None, null=True, blank=True, on_delete=models.SET_NULL)

    gender = models.ForeignKey('Gender', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    orientation = models.IntegerField(choices=ORIENTATION_CHOICES, blank=True, null=True)
    show_male = models.BooleanField(default=False)
    show_female = models.BooleanField(default=False)

    location = PointField(default=None, null=True, blank=True, geography=True)
    distance_max = models.IntegerField(blank=True, default=25)
    show_distance_km = models.BooleanField(default=True)

    height = models.IntegerField(null=True, blank=True, default=None, help_text='Height (inches)')
    height_min = models.IntegerField(null=True, blank=True, default=0, help_text='Height (inches)')
    height_max = models.IntegerField(null=True, blank=True, default=100, help_text='Height (inches)')
    show_height_cm = models.BooleanField(default=False)

    age_min = models.IntegerField(null=True, blank=True, default=18)
    age_max = models.IntegerField(null=True, blank=True, default=50)

    importance_interests = models.IntegerField(choices=IMPORTANCE_CHOICES, default=0, blank=True, null=True)
    importance_experiences = models.IntegerField(choices=IMPORTANCE_CHOICES, default=0, blank=True, null=True)
    wants_relationship = models.BooleanField(default=True)
    gradient = models.CharField(max_length=20, default="Orchid", blank=True)

    is_premium = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    allows_notifications = models.BooleanField(default=True)
    
    hide_swipedeck = models.BooleanField(default=False)

    hide_tutorial_swiping = models.BooleanField(default=False)
    hide_tutorial_matchlimit = models.BooleanField(default=False)
    hide_tutorial_matches = models.BooleanField(default=False)
    hide_tutorial_endconvo = models.BooleanField(default=False)
    
    deleted_reason_bugs = models.BooleanField(default=False)
    deleted_reason_quality = models.BooleanField(default=False)
    deleted_reason_quantity = models.BooleanField(default=False)
    deleted_reason_another_onapp = models.BooleanField(default=False)
    deleted_reason_another_offapp = models.BooleanField(default=False)
    deleted_reason_other = models.BooleanField(default=False)
    deleted_reason_other_text = models.CharField(max_length=5000,default=None,blank=True,null=True,)

    match_count = models.IntegerField(default=0, blank=True, null=True)
    phone_verification_code = models.CharField(max_length=4)
    is_phone_verified = models.BooleanField(default=False)
    is_phone_permission_denied = models.BooleanField(default=False)
    firebase_token = models.CharField(max_length=255, default=None, blank=True, null=True)
    referral_code = models.CharField(max_length=255, default=None, blank=True, null=True)

    last_visit = models.DateTimeField(default=timezone.now)

    def remaining_likes_count(self):
        if self.is_premium:
            return 5 - self.match_count
        return 3 - self.match_count

    def profile_picture_url(self):
        if self.pictures.all().count() > 0:
            return self.pictures.all().first().picture_url()
        return settings.DEFAULT_PROFILE_PICTURE

    def generate_password_reset_token(self):
        self.password_reset_token = default_token_generator.make_token(self)

    def get_password_reset_url(self):
        self.generate_password_reset_token()
        return '{}/password-reset-confirm/{}/{}'.format(settings.API_BASE_URL, urlsafe_base64_encode(force_bytes(self.pk)), self.password_reset_token)

    def admin_url(self):
        return '{0}/admin/api/profile/{1}/change/'.format(settings.API_BASE_URL, self.id)

    def __str__(self):
        if self.phone:
            return str(self.phone)
        return self.first_name


class ProfilePicture(TimeStampedModel):
    class Meta:
        ordering = ['position']

    profile = models.ForeignKey(Profile, related_name='pictures', null=True, blank=True, on_delete=models.CASCADE)
    picture = models.ImageField(null=True, blank=True, default=None)
    position = models.IntegerField(null=True, blank=True, default=None)

    def picture_url(self):
        return self.picture.url if self.picture else settings.DEFAULT_PROFILE_PICTURE


class SignupPicture(TimeStampedModel):
    class Meta:
        ordering = ['position']

    signup = models.ForeignKey(Signup, related_name='pictures', null=True, blank=True, on_delete=models.CASCADE)
    picture = models.ImageField(null=True, blank=True, default=None)
    position = models.IntegerField(null=True, blank=True, default=None)

    def picture_url(self):
        return self.picture.url if self.picture else settings.DEFAULT_PROFILE_PICTURE


class School(TimeStampedModel):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class Interest(TimeStampedModel):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class SignupInterest(TimeStampedModel):
    signup = models.ForeignKey(Signup, related_name='interests', on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, related_name='signups', on_delete=models.CASCADE)


class ProfileInterest(TimeStampedModel):
    profile = models.ForeignKey(Profile, related_name='interests', on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, related_name='profiles', on_delete=models.CASCADE)


class Experience(TimeStampedModel):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class ProfileExperience(TimeStampedModel):
    profile = models.ForeignKey(Profile, related_name='experiences', on_delete=models.CASCADE)
    experience = models.ForeignKey(Experience, related_name='profiles', on_delete=models.CASCADE)


class Gender(TimeStampedModel):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200)
    is_male_group = models.BooleanField(default=False)
    is_female_group = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Like(TimeStampedModel):
    class Meta:
        ordering = ['-id']

    NO_CHEMISRY = 1
    UNRESPONSIVE = 2
    SOMEONE_ELSE = 3
    ACCIDENT = 4
    REPORT_PHOTOS = 101
    REPORT_SPAM = 102
    REPORT_HARASSMENT = 103
    ACCOUNT_DELETED = 501
    ADMIN_PURPOSES = 999

    ENDED_CHOICES = (
        (NO_CHEMISRY, 'NO_CHEMISRY'),
        (UNRESPONSIVE, 'UNRESPONSIVE'),
        (SOMEONE_ELSE, 'SOMEONE_ELSE'),
        (ACCIDENT, 'ACCIDENT'),
        (REPORT_PHOTOS, 'REPORT_PHOTOS'),
        (REPORT_SPAM, 'REPORT_SPAM'),
        (REPORT_HARASSMENT, 'REPORT_HARASSMENT'),
        (ACCOUNT_DELETED, 'ACCOUNT_DELETED'),
        (ADMIN_PURPOSES, 'ADMIN_PURPOSES'),
        )

    liker = models.ForeignKey(Profile, related_name='likes', on_delete=models.CASCADE)
    subject = models.ForeignKey(Profile, related_name='liked_by', on_delete=models.CASCADE)
    is_match = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_liker_paid = models.BooleanField(default=False)
    is_subject_paid = models.BooleanField(default=False)

    is_ended = models.BooleanField(default=False)
    is_ended_by = models.ForeignKey(Profile, related_name='ended_conversations', default=None, blank=True, null=True, on_delete=models.CASCADE)
    is_ended_reason = models.IntegerField(choices=ENDED_CHOICES, blank=True, null=True)

    amity_channel = models.CharField(default='', max_length=64, blank=True)
    #Takes a Profile (assumed to be a member of this Like) and provides the (like/subject) Profile that is the other
    def other_profile(self, profile):
        if profile.id == self.liker.id:
            return self.subject
        return self.liker

    def is_ended_reason_text(self):
        if self.is_ended_reason:
            return self.ENDED_CHOICES[self.is_ended_reason][1]
        return ''

    def in_queue(self):
        if self.is_match or self.is_active or self.is_rejected:
            return False
        return True
    #Deletes any other Like objects with a matching liker/subject pair, even if the liker/subject roles are reversed
    def dedupe(self):
        (Like.objects.filter(liker=self.liker, subject=self.subject) | Like.objects.filter(liker=self.subject, subject=self.liker)).exclude(id=self.id).delete()
        return

    was_ended_by = None
    was_active = None
    was_match = None
    def __init__(self, *args, **kwargs):
        super(Like, self).__init__(*args, **kwargs)
        self.was_ended_by = self.is_ended_by
        self.was_active = self.is_active
        self.was_match = self.is_match

    def save(self, *args, **kwargs):
        #Like became a match
        if self.is_match and not self.was_match and self.is_active and not self.was_active:
            self.liker.match_count += 1
            self.liker.save()
            self.subject.match_count += 1
            self.subject.save()
        #Like (match) ended.
        #is_active prevents triggering on pre-match user reporting
        elif self.is_ended_by and not self.was_ended_by and self.was_active and not self.is_active:
            self.is_ended = True
            self.liker.match_count -= 1
            self.liker.save()
            self.subject.match_count -= 1
            self.subject.save()

            recipient = self.subject if self.is_ended_by.id == self.liker.id else self.liker
            send_notification(
                firebase_token=recipient.firebase_token,
                title="{0} ended your conversation".format(self.is_ended_by.first_name), 
                body="Keep swiping! 🥰"
                )
        return super(Like, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} -> {1} | {2} {3} {4}".format(
            str(self.liker), 
            str(self.subject),
            'Active' if self.is_active else '',
            '<3' if self.is_match else '',
            'X' if self.is_rejected else ''
            )


class NotificationLog(TimeStampedModel):
    token = models.CharField(max_length=2000, blank=True, null=True, default=None)
    title = models.CharField(max_length=2000, default='')
    body = models.CharField(max_length=2000, default='')
    is_success = models.BooleanField(default=False)


##############################
#         Geo Classes        #
##############################

class Country(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'GEO - Countries'

    def __str__(self):
        return self.name


class Province(models.Model):
    name    = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='provinces')

    class Meta:
        verbose_name_plural = 'GEO - Provinces'

    def __str__(self):
        return self.name


class City(models.Model):
    name     = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE , related_name='cities')
    location = PointField(default=None, null=True, blank=True, geography=True)

    class Meta:
        verbose_name_plural = 'GEO - Cities'

    def __str__(self):
        return self.name


# check for existing admins
# For testing purposes
# This probably should not make it into production
def admin_exists(shell=False):
    admin_exists = Profile.objects.filter(is_superuser=True).exists()
    if shell: admin_exists = str(admin_exists).lower()
    return admin_exists
