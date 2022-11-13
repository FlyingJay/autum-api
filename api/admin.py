from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.db.models import Count, Q, F, Sum, Subquery, OuterRef, Value, Avg
from import_export import resources
#Maps widget not needed yet, but needs to be fixed for production implementation.
#from mapwidgets.widgets import GooglePointFieldWidget
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.html import format_html

from .models import *
from .notifications import send_notification

admin.site.empty_value_display = 'Unknown'


def custom_titled_filter(title):
	class Wrapper(admin.FieldListFilter):
		def __new__(cls, *args, **kwargs):
			instance = admin.FieldListFilter.create(*args, **kwargs)
			instance.title = title
			return instance
	return Wrapper

class InterestResource(resources.ModelResource):
	class Meta:
		model = Interest

class ExperienceResource(resources.ModelResource):
	class Meta:
		model = Experience

class GenderResource(resources.ModelResource):
	class Meta:
		model = Gender


#################
# ADMIN FILTERS #
#################

class CreatedDateFilter(admin.SimpleListFilter):
	title = _('Created')
	parameter_name = 'created_date'

	def lookups(self, request, model_admin):
		return (
			('Today (only)', _('Today (only)')),
			('Yesterday (only)', _('Yesterday (only)')),
			('Last Week', _('Last Week')),
			('Last Month', _('Last Month')),
			('All Time', _('All Time')),
		)

	def queryset(self, request, queryset):
		now = datetime.now()
		if self.value() == 'Today (only)':
			return queryset.filter(created_at__year=now.year,created_at__month=now.month,created_at__day=now.day)
		if self.value() == 'Yesterday (only)':
			yesterday = now - timedelta(days=1)
			return queryset.filter(created_at__year=yesterday.year,created_at__month=yesterday.month,created_at__day=yesterday.day)
		if self.value() == 'Last Week':
			last_week = now - timedelta(days=7)
			return queryset.filter(created_at__gte=last_week)
		if self.value() == 'Last Month':
			last_month = now - timedelta(days=30)
			return queryset.filter(created_at__gte=last_month)
		if self.value() == 'All Time':
			return queryset


class UpdatedDateFilter(admin.SimpleListFilter):
	title = _('Last updated')
	parameter_name = 'updated_date'

	def lookups(self, request, model_admin):
		return (
			('Today (only)', _('Today (only)')),
			('Yesterday (only)', _('Yesterday (only)')),
			('Last Week', _('Last Week')),
			('Last Month', _('Last Month')),
			('All Time', _('All Time')),
		)

	def queryset(self, request, queryset):
		now = datetime.now()
		if self.value() == 'Today (only)':
			return queryset.filter(updated_at__year=now.year,updated_at__month=now.month,updated_at__day=now.day)
		if self.value() == 'Yesterday (only)':
			yesterday = now - timedelta(days=1)
			return queryset.filter(updated_at__year=yesterday.year,updated_at__month=yesterday.month,updated_at__day=yesterday.day)
		if self.value() == 'Last Week':
			last_week = now - timedelta(days=7)
			return queryset.filter(updated_at__gte=last_week)
		if self.value() == 'Last Month':
			last_month = now - timedelta(days=30)
			return queryset.filter(updated_at__gte=last_month)
		if self.value() == 'All Time':
			return queryset


class InactiveSinceFilter(admin.SimpleListFilter):
	title = _('Inactive since')
	parameter_name = 'last_visit_since'

	def lookups(self, request, model_admin):
		return (
			('Yesterday', _('Yesterday')),
			('7 Days', _('7 Days')),
			('30 Days', _('30 Days')),
			('60 Days', _('60 Days')),
			('90 Days', _('90 Days')),
		)

	def queryset(self, request, queryset):
		now = datetime.now()
		if self.value() == 'Yesterday':
			date = now - timedelta(days=1)
			return queryset.filter(last_visit__lte=date)
		if self.value() == '7 Days':
			date = now - timedelta(days=7)
			print(queryset.filter(last_visit__lte=date).count())
			return queryset.filter(last_visit__lte=date)
		if self.value() == '30 Days':
			date = now - timedelta(days=30)
			return queryset.filter(last_visit__lte=date)
		if self.value() == '60 Days':
			date = now - timedelta(days=60)
			return queryset.filter(last_visit__lte=date)
		if self.value() == '90 Days':
			date = now - timedelta(days=90)
			return queryset.filter(last_visit__lte=date)


class LastVisitFilter(admin.SimpleListFilter):
	title = _('Last visit')
	parameter_name = 'last_visit_date'

	def lookups(self, request, model_admin):
		return (
			('Today (only)', _('Today (only)')),
			('Yesterday (only)', _('Yesterday (only)')),
			('Last Week', _('Last Week')),
			('Last Month', _('Last Month')),
			('All Time', _('All Time')),
		)

	def queryset(self, request, queryset):
		now = datetime.now()
		if self.value() == 'Today (only)':
			return queryset.filter(last_visit__year=now.year,last_visit__month=now.month,last_visit__day=now.day)
		if self.value() == 'Yesterday (only)':
			yesterday = now - timedelta(days=1)
			return queryset.filter(last_visit__year=yesterday.year,last_visit__month=yesterday.month,last_visit__day=yesterday.day)
		if self.value() == 'Last Week':
			last_week = now - timedelta(days=7)
			return queryset.filter(last_visit__gte=last_week)
		if self.value() == 'Last Month':
			last_month = now - timedelta(days=30)
			return queryset.filter(last_visit__gte=last_month)
		if self.value() == 'All Time':
			return queryset


class HasMatchedFilter(admin.SimpleListFilter):
	title = _('Has Matched')
	parameter_name = 'has_matched'

	def lookups(self, request, model_admin):
		return (
			('Yes', _('Yes')),
			('No', _('No')),
		)

	def queryset(self, request, queryset):
		if self.value() == 'Yes':
			return queryset.filter(id__gt=552).annotate(
			match_count=Count("likes", filter=Q(likes__is_match=True), distinct=True) + Count("liked_by", filter=Q(liked_by__is_match=True), distinct=True)
			).filter(match_count__gt=0)
		if self.value() == 'No':
			return queryset.filter(id__gt=552).annotate(
			match_count=Count("likes", filter=Q(likes__is_match=True), distinct=True) + Count("liked_by", filter=Q(liked_by__is_match=True), distinct=True)
			).filter(match_count=0)


class ActiveMatchesFilter(admin.SimpleListFilter):
	title = _('Active Matches')
	parameter_name = 'active_matches'

	def lookups(self, request, model_admin):
		return (
			('0', _('0')),
			('1', _('1')),
			('1+', _('1+')),
			('2', _('2')),
			('2+', _('2+')),
			('3', _('3')),
			('4+ (bug)', _('4+ (bug)')),
		)

	def queryset(self, request, queryset):
		if self.value() == '0':
			return queryset.filter(id__gt=552, match_count=0)
		if self.value() == '1':
			return queryset.filter(id__gt=552, match_count=1)
		if self.value() == '1+':
			return queryset.filter(id__gt=552, match_count__gt=0)
		if self.value() == '2':
			return queryset.filter(id__gt=552, match_count=2)
		if self.value() == '2+':
			return queryset.filter(id__gt=552, match_count__gt=1)
		if self.value() == '3':
			return queryset.filter(id__gt=552, match_count=3)
		if self.value() == '4+ (bug)':
			return queryset.filter(id__gt=552,match_count__gt=3)


class MissingProfileDetailsFilter(admin.SimpleListFilter):
	title = _('Missing Details')
	parameter_name = 'missing_profile_details'

	def lookups(self, request, model_admin):
		return (
			('Phone Number', _('Phone Number')),
			('First Name', _('First Name')),
			('Birthday', _('Birthday')),
			('Bio', _('Bio')),
			('Job', _('Job')),
			('Company', _('Company')),
			('School', _('School')),
			('Gender', _('Gender')),
			('Orientation', _('Orientation')),
			('Height', _('Height')),
			('Pictures', _('Pictures')),
			('Interests', _('Interests')),
			('Experiences', _('Experiences')),
			('Firebase Token', _('Firebase Token')),
		)

	def queryset(self, request, queryset):
		if self.value() == 'Phone Number':
			return queryset.filter(id__gt=552, phone=None)
		if self.value() == 'First Name':
			return queryset.filter(id__gt=552, first_name='')
		if self.value() == 'Birthday':
			return queryset.filter(id__gt=552, birthday=None)
		if self.value() == 'Bio':
			return queryset.filter(id__gt=552, description='')
		if self.value() == 'Job':
			return queryset.filter(id__gt=552, job='')
		if self.value() == 'Company':
			return queryset.filter(id__gt=552, company='')
		if self.value() == 'School':
			return queryset.filter(id__gt=552, school=None)
		if self.value() == 'Gender':
			return queryset.filter(id__gt=552, gender=None)
		if self.value() == 'Orientation':
			return queryset.filter(id__gt=552, orientation=None)
		if self.value() == 'Height':
			return queryset.filter(id__gt=552, height=None)
		if self.value() == 'Pictures':
			return queryset.filter(id__gt=552, pictures=None)
		if self.value() == 'Interests':
			return queryset.filter(id__gt=552, interests=None)
		if self.value() == 'Experiences':
			return queryset.filter(id__gt=552, experiences=None)
		if self.value() == 'Firebase Token':
			return queryset.filter(id__gt=552, firebase_token=None)


class IsReportedFilter(admin.SimpleListFilter):
	title = _('Is Reported')
	parameter_name = 'is_reported'

	def lookups(self, request, model_admin):
		return (
			('Yes', _('Yes')),
			('No', _('No')),
		)

	def queryset(self, request, queryset):
		if self.value() == 'Yes':
			return queryset.filter(is_ended_reason__gt=100, is_ended_reason__lt=200)
		if self.value() == 'No':
			return queryset.filter(~Q(is_ended_reason__gt=100, is_ended_reason__lt=200))


class IsEndedFilter(admin.SimpleListFilter):
	title = _('Is Ended')
	parameter_name = 'is_like_ended'

	def lookups(self, request, model_admin):
		return (
			('Yes', _('Yes')),
			('No', _('No')),
		)

	def queryset(self, request, queryset):
		if self.value() == 'Yes':
			return queryset.filter(~Q(is_ended_reason=None))
		if self.value() == 'No':
			return queryset.filter(is_ended_reason=None)


###################
# ADMIN FUNCTIONS #
###################

def reset_likes(modeladmin, request, queryset):
	Like.objects.filter(liker__in=queryset).delete()
	Like.objects.filter(subject__in=queryset, is_rejected=True).delete()
reset_likes.short_description = "Clear likes for selected users"

def reset_likes_safe(modeladmin, request, queryset):
	Like.objects.filter(liker__in=queryset, is_rejected=True).delete()
reset_likes_safe.short_description = "Clear left-swipes for selected users"

def show_swipedeck(modeladmin, request, queryset):
	queryset.update(hide_swipedeck=False, location=None)
show_swipedeck.short_description = "Open swiping for user"

def clear_location(modeladmin, request, queryset):
	queryset.update(location=None)
clear_location.short_description = "Clear user's location"

def reset_tutorials(modeladmin, request, queryset):
	queryset.update(hide_tutorial_swiping=False,hide_tutorial_matchlimit=False,hide_tutorial_matches=False,hide_tutorial_endconvo=False)
reset_tutorials.short_description = "Re-activate user's tutorials"


def send_notifications(self, request, queryset):
	if 'send' in request.POST:
		if len(request.POST['title']) == 0:
			self.message_user(request, "Didn't send, no title text provided.")
			return HttpResponseRedirect(request.get_full_path())
		elif len(request.POST['body']) == 0:
			self.message_user(request, "Didn't send, no body text provided.")
			return HttpResponseRedirect(request.get_full_path())

		for profile in queryset.exclude(firebase_token=None).all():
			send_notification(
				firebase_token=profile.firebase_token,
				title=request.POST['title'], 
				body=request.POST['body']
				)

		self.message_user(request, "Sent notifications to {} profiles.".format(queryset.exclude(firebase_token=None).count()))
		return HttpResponseRedirect(request.get_full_path())

	return render(request, 'core/send-notifications.html', context={'profiles':queryset})
send_notifications.short_description = "Send Notifications"


###########
# INLINES #
###########

# class LikeLikerInline(admin.TabularInline):
# 	model = Like
# 	fk_name = "liker"
# 	verbose_name = "Like"
# 	verbose_name_plural = "Likes"

# class LikeSubjectInline(admin.TabularInline):
# 	model = Like
# 	fk_name = "subject"
# 	verbose_name = "Liked By"
# 	verbose_name_plural = "Liked By"

class ProfileInterestInline(admin.TabularInline):
	model = ProfileInterest
	verbose_name = "Interest"
	verbose_name_plural = "Interests"

class ProfileExperienceInline(admin.TabularInline):
	model = ProfileExperience
	verbose_name = "Experience"
	verbose_name_plural = "Experiences"

class ProfilePictureInline(admin.TabularInline):
	model = ProfilePicture
	verbose_name = "Picture"
	verbose_name_plural = "Pictures"

class SignupInterestInline(admin.TabularInline):
	model = SignupInterest
	verbose_name = "Interest"
	verbose_name_plural = "Interests"

class SignupPictureInline(admin.TabularInline):
	model = SignupPicture
	verbose_name = "Picture"
	verbose_name_plural = "Pictures"

class AutumPhoneInline(admin.TabularInline):
	model = AutumPhone
	verbose_name = "Autum Phone"
	verbose_name_plural = "Autum Phones"
	

##########
# MODELS #
##########

@admin.register(AutumConfig)
class AutumConfigAdmin(ImportExportModelAdmin):
	list_display = ('profile_hide_swipedeck_default','region_lock_distance_toronto',)
	inlines = (AutumPhoneInline,)

@admin.register(Ambassador)
class AmbassadorAdmin(ImportExportModelAdmin):
	list_display = ('first_name','last_name',)
	list_filter = (CreatedDateFilter,UpdatedDateFilter,)
	search_fields = (
		'first_name',
		'last_name',
	)

@admin.register(School)
class SchoolAdmin(ImportExportModelAdmin):
	list_display = ('name','country',)
	list_filter = ('country',)
	search_fields = (
		'name',
		'country',
	)

@admin.register(Gender)
class GenderAdmin(ImportExportModelAdmin):
	list_display = ('name',)
	resource_class = GenderResource
	search_fields = (
		'name',
	)

@admin.register(Signup)
class SignupAdmin(ImportExportModelAdmin):
	list_display = ('first_name','email','phone','is_phone_verified',)
	list_filter = ('gender','referral_code',CreatedDateFilter,UpdatedDateFilter,)
	search_fields = (
		'phone',
		'first_name',
	)
	inlines = (SignupInterestInline,SignupPictureInline,)

@admin.register(SignupPicture)
class SignupPictureAdmin(ImportExportModelAdmin):
	list_display = ('signup','picture','position',)
	search_fields = (
		'signup__phone',
		'signup__first_name',
	)

@admin.register(SignupInterest)
class SignupInterestAdmin(ImportExportModelAdmin):
	list_display = ('signup','interest',)
	list_filter = ('interest',)
	search_fields = (
		'signup__first_name',
		'signup__phone',
		'interest__name',
	)

@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
	list_display = ('profile_pic','first_name','phone','is_hidden','is_archived','allows_notifications','referral_code','created_at','updated_at','last_visit',)
	list_filter = ('gender','is_hidden','is_archived','allows_notifications','referral_code', ActiveMatchesFilter,HasMatchedFilter,MissingProfileDetailsFilter,CreatedDateFilter,UpdatedDateFilter,LastVisitFilter,InactiveSinceFilter,)
	search_fields = (
		'first_name',
		'phone',
		'username',
	)
	inlines = (ProfileInterestInline,ProfileExperienceInline,ProfilePictureInline,)
	actions = [reset_likes,reset_likes_safe,show_swipedeck,reset_tutorials,send_notifications]

	def profile_pic(self, obj):
		return format_html("<img src='{url}' width='80px'/>", url=obj.profile_picture_url())


@admin.register(ProfilePicture)
class ProfilePictureAdmin(ImportExportModelAdmin):
	list_display = ('profile','picture','position',)
	search_fields = (
		'profile__first_name',
		'profile__phone',
	)

@admin.register(Interest)
class InterestAdmin(ImportExportModelAdmin):
	list_display = ('name',)
	list_filter = (CreatedDateFilter,UpdatedDateFilter,)
	resource_class = InterestResource
	search_fields = (
		'name',
	)

@admin.register(ProfileInterest)
class ProfileInterestAdmin(ImportExportModelAdmin):
	list_display = ('profile','interest',)
	list_filter = ('interest',)
	search_fields = (
		'profile__first_name',
		'profile__phone',
		'interest__name',
	)

@admin.register(Experience)
class ExperienceAdmin(ImportExportModelAdmin):
	list_display = ('name',)
	list_filter = (CreatedDateFilter,UpdatedDateFilter,)
	resource_class = ExperienceResource
	search_fields = (
		'name',
	)

@admin.register(ProfileExperience)
class ProfileExperienceAdmin(ImportExportModelAdmin):
	list_display = ('profile','experience',)
	list_filter = ('experience',)
	search_fields = (
		'profile__first_name',
		'profile__phone',
		'experience__name',
	)

@admin.register(Like)
class LikeAdmin(ImportExportModelAdmin):
	list_display = ('id','_liker','_subject','is_match','is_rejected','is_active','is_ended_reason','ended_by','in_queue','created_at','updated_at',)
	list_filter = ('is_match','is_rejected','is_active',IsEndedFilter,'is_ended_reason',IsReportedFilter,CreatedDateFilter,UpdatedDateFilter,)
	search_fields = (
		'liker__first_name',
		'liker__phone',
		'subject__first_name',
		'subject__phone',
	)

	def _liker(self, obj):
		return format_html("<a href='{url}'><span>{name}</span><br/><img src='{picture}' width='80px'/></a>", name=obj.liker.first_name, url=obj.liker.admin_url(), picture=obj.liker.profile_picture_url())

	def _subject(self, obj):
		return format_html("<a href='{url}'><span>{name}</span><br/><img src='{picture}' width='80px'/></a>", name=obj.subject.first_name, url=obj.subject.admin_url(), picture=obj.subject.profile_picture_url())

	def ended_by(self, obj):
		if obj.is_ended_by:
			return obj.is_ended_by.first_name
		return None


@admin.register(NotificationLog)
class NotificationLogAdmin(ImportExportModelAdmin):
	list_display = ('token','title','body',)
	list_filter = (CreatedDateFilter,UpdatedDateFilter,)
	search_fields = (
		'token',
		'title',
		'body',
	)


#######
# GEO #
#######

# @admin.register(Country)	
# class CountryAdmin(admin.ModelAdmin):
# 	search_fields = (
# 		'name',
# 		)

# @admin.register(Province)	
# class ProvinceAdmin(admin.ModelAdmin):
# 	list_display = ('name','country',)

# 	search_fields = (
# 		'name',
# 		'country__name',
# 		)

# 	list_filter = (
# 		('country', admin.RelatedOnlyFieldListFilter),
# 	)


# @admin.register(City)	
# class CityAdmin(admin.ModelAdmin):
# 	list_display = ('name','province',)

# 	search_fields = (
# 		'name',
# 		'province__name',
# 		'province__country__name'
# 		)

# 	list_filter = (
# 		('province', admin.RelatedOnlyFieldListFilter),
# 	)

