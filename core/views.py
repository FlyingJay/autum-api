import json
import itertools
from django.db.models import Count, Q, F, Sum, Subquery, OuterRef, Value, Avg
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay, Coalesce
from django.http import FileResponse, HttpResponsePermanentRedirect
from django.views.generic.base import TemplateView
from datetime import datetime
from api import settings

from api.models import *


class AutmRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = ['autum']

#Native app redirect
def app_view(request):
    return AutmRedirect('autum://login')

#Android deeplinks verification
def verify_android_deeplinks(response):
    return FileResponse(open(settings.BASE_DIR + '/assetlinks.json', 'rb'))


#########
# VIEWS #
#########

class ToolsView(TemplateView):
    template_name = "core/tools.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['API_BASE_URL'] = settings.API_BASE_URL
        return context


class MapView(TemplateView):
    template_name = "core/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profiles = Profile.objects.filter(id__gt=552).exclude(location=None).values('id','first_name','location','phone',)

        for profile in profiles:
            if profile['location']:
                location_str = str(profile['location'])
                lng = float(location_str.split('(')[1].split(' ')[0])
                lat = float(location_str.split('(')[1].split(' ')[1][:-1])
                profile['location'] = { 'lat':lat, 'lng':lng }

        context['profiles'] = json.dumps(list(profiles))
        context['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
        return context


class DeletedMapView(TemplateView):
    template_name = "core/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profiles = Profile.objects.filter(id__gt=552, is_archived=True).exclude(location=None).values('id','first_name','location','phone',)

        for profile in profiles:
            if profile['location']:
                location_str = str(profile['location'])
                lng = float(location_str.split('(')[1].split(' ')[0])
                lat = float(location_str.split('(')[1].split(' ')[1][:-1])
                profile['location'] = { 'lat':lat, 'lng':lng }

        context['profiles'] = json.dumps(list(profiles))
        context['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
        return context


class WaitingListMapView(TemplateView):
    template_name = "core/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profiles = Profile.objects.filter(id__gt=552, is_archived=False, hide_swipedeck=True).exclude(location=None).values('id','first_name','location','phone',)

        for profile in profiles:
            if profile['location']:
                location_str = str(profile['location'])
                lng = float(location_str.split('(')[1].split(' ')[0])
                lat = float(location_str.split('(')[1].split(' ')[1][:-1])
                profile['location'] = { 'lat':lat, 'lng':lng }

        context['profiles'] = json.dumps(list(profiles))
        context['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
        return context


class StatsView(TemplateView):
    template_name = "core/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['API_BASE_URL'] = settings.API_BASE_URL
        context['ENDED_CHOICES'] = Like.ENDED_CHOICES

        context['power_users'] = list(Profile.objects.filter(id__gt=552, is_archived=False).annotate( 
            historical_match_count=Count("likes", filter=Q(likes__is_match=True), distinct=True) + Count("liked_by", filter=Q(liked_by__is_match=True), distinct=True) 
            ).filter(historical_match_count__gt=0).order_by('-historical_match_count').values('first_name','historical_match_count'))[0:10] 

        context['recent_likes'] = Like.objects.filter(is_match=True,is_ended=False).annotate(last_modified=Coalesce('updated_at','created_at')).order_by('-last_modified')[0:20]
        context['ended_likes'] = Like.objects.filter(is_match=True,is_ended=True).annotate(last_modified=Coalesce('updated_at','created_at')).order_by('-last_modified')[0:20]

        unanswered_swipes = Like.objects.filter(Q(updated_at__lt=F('created_at') + timedelta(seconds=3)), liker__id__gt=552, subject__id__gt=552)
        answered_swipes = Like.objects.filter(~Q(updated_at__lt=F('created_at') + timedelta(seconds=3)), liker__id__gt=552, subject__id__gt=552)
        total_swipes = unanswered_swipes.count() + answered_swipes.count() * 2

        context['unanswered_swipes'] = unanswered_swipes.count()
        context['answered_swipes'] = answered_swipes.count()
        context['total_swipes'] = total_swipes

        unanswered_swipes_registered_users = Like.objects.filter(Q(updated_at__lt=F('created_at') + timedelta(seconds=3)), liker__id__gt=552, subject__id__gt=552, liker__is_archived=False, subject__is_archived=False)
        answered_swipes_registered_users = Like.objects.filter(~Q(updated_at__lt=F('created_at') + timedelta(seconds=3)), liker__id__gt=552, subject__id__gt=552, liker__is_archived=False, subject__is_archived=False)
        total_swipes_registered_users = unanswered_swipes_registered_users.count() + answered_swipes_registered_users.count() * 2

        context['unanswered_swipes_registered_users'] = unanswered_swipes_registered_users.count()
        context['answered_swipes_registered_users'] = answered_swipes_registered_users.count()
        context['total_swipes_registered_users'] = total_swipes_registered_users

        signups = Signup.objects.filter(id__gt=1393)
        signups_phone_not_verified = signups.filter(is_phone_verified=False)
        signups_phone_verified = signups.filter(is_phone_verified=True)

        signups_no_email = signups_phone_verified.filter(email='')
        signups_email = signups_phone_verified.filter(~Q(email=''))

        signups_no_name = signups_email.filter(first_name='')
        signups_name = signups_email.filter(~Q(first_name=''))

        signups_no_birthday = signups_name.filter(birthday=None)
        signups_birthday = signups_name.filter(~Q(birthday=None))

        signups_no_gender = signups_birthday.filter(gender=None)
        signups_gender = signups_birthday.filter(~Q(gender=None))
        
        signups_no_orientation = signups_gender.filter(orientation=None)#Optional
        signups_orientation = signups_gender.filter(~Q(orientation=None))#Optional
        signups_no_showme = signups_gender.filter(show_male=False, show_female=False)
        signups_showme = signups_gender.filter(~Q(show_male=False, show_female=False))

        signups_no_school = signups_showme.filter(school=None)#Optional
        signups_school = signups_showme.filter(~Q(school=None))#Optional
        signups_no_pictures = signups_showme.filter(pictures=None)
        signups_pictures = signups_showme.filter(~Q(pictures=None))
        
        signups_no_interests = signups_pictures.filter(interests=None)#Optional
        signups_interests = signups_pictures.filter(~Q(interests=None))#Optional
        signups_no_referral = signups_pictures.filter(referral_code=None)#Optional
        signups_referral = signups_pictures.filter(~Q(referral_code=None))#Optional

        context['signups'] = signups.count()
        context['signups_phone_not_verified'] = signups_phone_not_verified.count()
        context['signups_phone_verified'] = signups_phone_verified.count()

        context['signups_no_email'] = signups_no_email.count()
        context['signups_email'] = signups_email.count()

        context['signups_no_name'] = signups_no_name.count()
        context['signups_name'] = signups_name.count()

        context['signups_no_birthday'] = signups_no_birthday.count()
        context['signups_birthday'] = signups_birthday.count()

        context['signups_no_gender'] = signups_no_gender.count()
        context['signups_gender'] = signups_gender.count()
        
        context['signups_no_orientation'] = signups_no_orientation.count()
        context['signups_orientation'] = signups_orientation.count()
        context['signups_no_showme'] = signups_no_showme.count()
        context['signups_showme'] = signups_showme.count()

        context['signups_no_school'] = signups_no_school.count()
        context['signups_school'] = signups_school.count()
        context['signups_no_pictures'] = signups_no_pictures.count()
        context['signups_pictures'] = signups_pictures.count()
        
        context['signups_no_interests'] = signups_no_interests.count()
        context['signups_interests'] = signups_interests.count()
        context['signups_no_referral'] = signups_no_referral.count()
        context['signups_referral'] = signups_referral.count()

        users = Profile.objects.filter(id__gt=552)
        users_matched = users.annotate( 
            historical_match_count=Count("likes", filter=Q(likes__is_match=True), distinct=True) + Count("liked_by", filter=Q(liked_by__is_match=True), distinct=True) 
            ).filter(historical_match_count__gt=0) 
        context['users_matched_matches_sum'] = users_matched.aggregate(Sum('historical_match_count'))['historical_match_count__sum']

        context['users_online_now'] = users.filter(last_visit__gt=datetime.now() - timedelta(minutes=10)).count()
        context['users_online_1h'] = users.filter(last_visit__gt=datetime.now() - timedelta(minutes=60)).count()
        context['users_online_24h'] = users.filter(last_visit__gt=datetime.now() - timedelta(days=1)).count()
        context['users_online_7d'] = users.filter(last_visit__gt=datetime.now() - timedelta(days=7)).count()
        context['users_online_30d'] = users.filter(last_visit__gt=datetime.now() - timedelta(days=30)).count()

        users_registered = users.filter(is_archived=False)
        users_registered_matched = users_registered.annotate( 
            historical_match_count=Count("likes", filter=Q(likes__is_match=True), distinct=True) + Count("liked_by", filter=Q(liked_by__is_match=True), distinct=True) 
            ).filter(historical_match_count__gt=0) 
        context['users_registered_matched_matches_sum'] = users_registered_matched.aggregate(Sum('historical_match_count'))['historical_match_count__sum']

        context['users_registered_online_hours'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        context['users_registered_online_hours_labels'] = ['0:00','1:00','2:00','3:00','4:00','5:00','6:00','7:00','8:00','9:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00']
        users_registered_online_hours = users_registered.annotate(hour=ExtractHour('last_visit')).values('hour').annotate(count=Count('hour')).order_by('-count','hour')
        for result in users_registered_online_hours:
            context['users_registered_online_hours'][result['hour']] = result['count']

        context['users_registered_online_days'] = [0,0,0,0,0,0,0,0]
        context['users_registered_online_days_labels'] = ['Mon','Tues','Wed','Thurs','Fri','Sat','Sun']
        users_registered_online_days = users_registered.annotate(day=ExtractWeekDay('last_visit')).values('day').annotate(count=Count('day')).order_by('-count','day')

        for result in users_registered_online_days:
            context['users_registered_online_days'][result['day']-1] = result['count']

        users_registered_male = users_registered.filter(gender__is_male_group=True).annotate(
            pictures_count=Count('pictures', distinct=True),
            interests_count=Count('interests', distinct=True),
            experiences_count=Count('experiences', distinct=True)
            )
        users_registered_female = users_registered.filter(gender__is_female_group=True).annotate(
            pictures_count=Count('pictures', distinct=True),
            interests_count=Count('interests', distinct=True),
            experiences_count=Count('experiences', distinct=True)
            )
        context['users_registered_male'] = users_registered_male.count()
        context['users_registered_female'] = users_registered_female.count()

        context['users_registered_male_bio'] = users_registered_male.filter(~Q(description='')).count()
        context['users_registered_male_job'] = users_registered_male.filter(~Q(job='')).count()
        context['users_registered_male_company'] = users_registered_male.filter(~Q(company='')).count()
        context['users_registered_male_school'] = users_registered_male.filter(~Q(school=None)).count()
        context['users_registered_male_orientation'] = users_registered_male.filter(~Q(orientation=None)).count()
        context['users_registered_male_height'] = users_registered_male.filter(~Q(height=None)).count()
        context['users_registered_male_interests'] = users_registered_male.filter(~Q(interests=None)).count()
        context['users_registered_male_experiences'] = users_registered_male.filter(~Q(experiences=None)).count()

        context['users_registered_male_pictures_avg'] = users_registered_male.aggregate(Avg('pictures_count'))['pictures_count__avg']
        context['users_registered_male_interests_avg'] = users_registered_male.aggregate(Avg('interests_count'))['interests_count__avg']
        context['users_registered_male_experiences_avg'] = users_registered_male.aggregate(Avg('experiences_count'))['experiences_count__avg']

        context['users_registered_female_bio'] = users_registered_female.filter(~Q(description='')).count()
        context['users_registered_female_job'] = users_registered_female.filter(~Q(job='')).count()
        context['users_registered_female_company'] = users_registered_female.filter(~Q(company='')).count()
        context['users_registered_female_school'] = users_registered_female.filter(~Q(school=None)).count()
        context['users_registered_female_orientation'] = users_registered_female.filter(~Q(orientation=None)).count()
        context['users_registered_female_height'] = users_registered_female.filter(~Q(height=None)).count()
        context['users_registered_female_interests'] = users_registered_female.filter(~Q(interests=None)).count()
        context['users_registered_female_experiences'] = users_registered_female.filter(~Q(experiences=None)).count()

        context['users_registered_female_pictures_avg'] = users_registered_female.aggregate(Avg('pictures_count'))['pictures_count__avg']
        context['users_registered_female_interests_avg'] = users_registered_female.aggregate(Avg('interests_count'))['interests_count__avg']
        context['users_registered_female_experiences_avg'] = users_registered_female.aggregate(Avg('experiences_count'))['experiences_count__avg']

        users_registered_active_matches = users_registered.filter(match_count__gt=0)
        users_registered_active_matches_full = users_registered_active_matches.filter(match_count=3)

        users_swipeable = users_registered.filter(is_hidden=False, hide_swipedeck=False)
        users_waiting_list = users_registered.filter(hide_swipedeck=True)

        users_deleted = users.filter(is_archived=True)
        users_deleted_bugs = users_deleted.filter(deleted_reason_bugs=True)
        users_deleted_quality = users_deleted.filter(deleted_reason_quality=True)
        users_deleted_quantity = users_deleted.filter(deleted_reason_quantity=True)
        users_deleted_another_onapp = users_deleted.filter(deleted_reason_another_onapp=True)
        users_deleted_another_offapp = users_deleted.filter(deleted_reason_another_offapp=True)
        users_deleted_other = users_deleted.filter(deleted_reason_other=True)

        context['users'] = users.count()
        context['users_matched'] = users_matched.count()
        context['users_registered'] = users_registered.count()
        context['users_registered_matched'] = users_registered_matched.count()
        context['users_registered_active_matches'] = users_registered_active_matches.count()
        context['users_registered_active_matches_full'] = users_registered_active_matches_full.count()
        context['users_registered_active_matches_avg'] = users_registered_active_matches.aggregate(Avg('match_count'))['match_count__avg']
        context['users_swipeable'] = users_swipeable.count()
        context['users_waiting_list'] = users_waiting_list.count()

        context['users_deleted'] = users_deleted_bugs.count() + users_deleted_quality.count() + users_deleted_quantity.count() + users_deleted_another_onapp.count() + users_deleted_another_offapp.count() + users_deleted_other.count()
        context['users_deleted_bugs'] = users_deleted_bugs.count()
        context['users_deleted_quality'] = users_deleted_quality.count()
        context['users_deleted_quantity'] = users_deleted_quantity.count()
        context['users_deleted_another_onapp'] = users_deleted_another_onapp.count()
        context['users_deleted_another_offapp'] = users_deleted_another_offapp.count()
        context['users_deleted_other'] = users_deleted_other.count()

        context['labels'] = ['bugs', 'quality', 'quantity', 'another on-app', 'another off-app', 'other']
        context['data'] = [
            context['users_deleted_bugs'],
            context['users_deleted_quality'],
            context['users_deleted_quantity'],
            context['users_deleted_another_onapp'],
            context['users_deleted_another_offapp'],
            context['users_deleted_other']
            ]

        context['deleted_labels'] = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        context['created_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
        context['deleted_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
        context['deleted_bugs_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
        context['deleted_quality_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
        context['deleted_quantity_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
        context['deleted_another_onapp_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
        context['deleted_another_offapp_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]
        context['deleted_other_data'] = [0,0,0,0,0,0,0,0,0,0,0,0]

        created_months = users.annotate(month=TruncMonth('created_at')).values('month').annotate(created_accounts=Count('id')).order_by()
        for created_month in created_months:
            context['created_data'][created_month['month'].month-1] = created_month['created_accounts']

        deleted_months = users_deleted.annotate(month=TruncMonth('updated_at')).values('month').annotate(deleted_accounts=Count('id')).order_by()
        for deleted_month in deleted_months:
            context['deleted_data'][deleted_month['month'].month-1] = deleted_month['deleted_accounts']

        deleted_bugs_months = users_deleted.filter(deleted_reason_bugs=True).annotate(month=TruncMonth('updated_at')).values('month').annotate(deleted_accounts=Count('id')).order_by()
        for deleted_month in deleted_bugs_months:
            context['deleted_bugs_data'][deleted_month['month'].month-1] = deleted_month['deleted_accounts']

        deleted_quality_months = users_deleted.filter(deleted_reason_quality=True).annotate(month=TruncMonth('updated_at')).values('month').annotate(deleted_accounts=Count('id')).order_by()
        for deleted_month in deleted_quality_months:
            context['deleted_quality_data'][deleted_month['month'].month-1] = deleted_month['deleted_accounts']

        deleted_quanity_months = users_deleted.filter(deleted_reason_quantity=True).annotate(month=TruncMonth('updated_at')).values('month').annotate(deleted_accounts=Count('id')).order_by()
        for deleted_month in deleted_quanity_months:
            context['deleted_quantity_data'][deleted_month['month'].month-1] = deleted_month['deleted_accounts']

        deleted_another_onapp_months = users_deleted.filter(deleted_reason_another_onapp=True).annotate(month=TruncMonth('updated_at')).values('month').annotate(deleted_accounts=Count('id')).order_by()
        for deleted_month in deleted_another_onapp_months:
            context['deleted_another_onapp_data'][deleted_month['month'].month-1] = deleted_month['deleted_accounts']

        deleted_another_offapp_months = users_deleted.filter(deleted_reason_another_offapp=True).annotate(month=TruncMonth('updated_at')).values('month').annotate(deleted_accounts=Count('id')).order_by()
        for deleted_month in deleted_another_offapp_months:
            context['deleted_another_offapp_data'][deleted_month['month'].month-1] = deleted_month['deleted_accounts']

        deleted_other_months = users_deleted.filter(deleted_reason_other=True).annotate(month=TruncMonth('updated_at')).values('month').annotate(deleted_accounts=Count('id')).order_by()
        for deleted_month in deleted_other_months:
            context['deleted_other_data'][deleted_month['month'].month-1] = deleted_month['deleted_accounts']

        return context