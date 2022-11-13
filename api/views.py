from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, response, permissions, generics, decorators, pagination, permissions as rest_framework_permissions, exceptions as rest_framework_exceptions
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.core import serializers as django_serializers
from django.db.models import Count, Q, F, Sum, Subquery, OuterRef, Value
from datetime import date
from django.utils.timezone import now
from django.contrib.auth import login, authenticate, logout
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.geos import Point
from random import randint
from django.http import QueryDict
from twilio.rest import Client
from django.conf import settings
from django.core.files.base import ContentFile
from functools import wraps
from secrets import choice
import string
import base64
import random
import json
from .models import *
from .filters import *
from .serializers import *
from .notifications import send_notification
from api import exceptions as api_exceptions


###########
# HELPERS #
###########

def mutable(request, value):
    if hasattr(request.data, '_mutable'):
        request.data._mutable = value


def get_page(queryset, page):
    paginator = Paginator(queryset, settings.REST_FRAMEWORK['PAGE_SIZE'])
    try: 
        return paginator.page(page)
    except PageNotAnInteger: 
        page = 1
    except EmptyPage: 
        page = paginator.num_pages
    return paginator.page(page)

class NoPagination(pagination.PageNumberPagination):       
    page_size = 1000

class LargePagination(pagination.PageNumberPagination):       
    page_size = 30


############
# WEBHOOKS #
############

@csrf_exempt
def amity_webhook(request):
    if 'X-Amity-Signature' in request.headers:
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        #New chat message
        if body_data['event'] == "message.didCreate":
            message = body_data['data']['messages'][0]

            like = Like.objects.filter(amity_channel=message['channelId']).first()
            sender = Profile.objects.filter(id=message['userId']).first()

            recipient = None
            if like.liker.id == int(message['userId']):
                recipient = like.subject
            elif like.subject.id == int(message['userId']):
                recipient = like.liker

            send_notification(
                firebase_token=recipient.firebase_token,
                title="{0} sent you a message 😊".format(sender.first_name), 
                body="Tap to chat!"
                )

    return HttpResponse(status=204)


def respond_SMS(text):
    return HttpResponse("""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Message>{0}</Message>
        </Response>""".format(text))


@csrf_exempt
def receive_sms(request):
    message = request.POST.get('Body', None)
    sender = request.POST.get('From', None)

    if sender.startswith('+'):
        sender = sender[1:]

    profiles = Profile.objects.filter(phone=sender)
    if profiles.count() > 0:
        if message.lower() == 'end':
            profiles.update(is_phone_permission_denied=True)
            return respond_SMS('We have updated your SMS preferences. Reply "BEGIN" to enable SMS notificaitons.')
        elif message.lower() == 'begin':
            profiles.update(is_phone_permission_denied=False)
            return respond_SMS('We have updated your SMS preferences. Reply "END" to disable SMS notificaitons.')
    else:
        return respond_SMS('We cannot find your account on Autum.')
    return respond_SMS('Reply "END" to disable SMS notifications. Reply "BEGIN" to enable them.')


##############
# DECORATORS #
##############

def track_activity(f):
  @wraps(f)
  def wrap(request, *args, **kwargs):
        res = f(request, *args, **kwargs)
        if args[0] and args[0].user and args[0].user.id:
            Profile.objects.filter(id=args[0].user.id).update(last_visit=now())
        return res
  return wrap


#########
# VIEWS #
#########

class AmbassadorViewSet(viewsets.ModelViewSet):
    queryset = Ambassador.objects.all()
    serializer_class = AmbassadorSerializer
    pagination_class = NoPagination
    permission_classes = [
        permissions.AllowAny
    ]

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [
        permissions.AllowAny
    ]

class SignupViewSet(viewsets.ModelViewSet):
    queryset = Signup.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def create(self, request, *args, **kwargs):
        code = random.randint(1111,9999)
        mutable(request, True)
        request.data['phone_verification_code'] = code
        mutable(request, False)

        if Profile.objects.filter(phone=request.data['phone'], is_archived=False).count() > 0:
            return response.Response({"phone":"User with this phone already exists."}, status=400)
        
        #User signing up with previously deleted account's phone number -> delete old record to avoid conflict
        if Profile.objects.filter(phone=request.data['phone'], is_archived=True).count() > 0:
            Profile.objects.filter(phone=request.data['phone'], is_archived=True).delete()

        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        message = Client(settings.TWILIO_SID,settings.TWILIO_AUTH_TOKEN).messages.create(
            body='Your Autum verification code is: {0}'.format(code),
            from_='+1{0}'.format(settings.TWILIO_SENDER_VERIFICATION),
            to=request.data['phone']
        )
        return response.Response(serializer.data, status=201)

    def partial_update(self, request, pk=None, *args, **kwargs):
        kwargs['partial'] = True
        signup = Signup.objects.get(pk=pk)

        if not signup.is_phone_verified:
            submitted_code = request.data['phone_verification_code']
            mutable(request, True)
            if submitted_code != str(signup.phone_verification_code):
                del request.data['phone_verification_code']
                #request.data['phone_verification_code'] = signup.phone_verification_code
                request.data['is_phone_verified'] = False
            else:
                request.data['is_phone_verified'] = True
            mutable(request, False)

        return self.update(request, *args, **kwargs)

    @decorators.action(detail=True)
    def male(self, request, pk=None):
        signup = self.get_queryset().get(id=pk)
        gender = Gender.objects.filter(name__iexact='Male').first()
        signup.gender = gender
        signup.save()

        serializer = self.get_serializer(signup)
        return response.Response(serializer.data, status=200)

    @decorators.action(detail=True)
    def female(self, request, pk=None):
        signup = self.get_queryset().get(id=pk)
        gender = Gender.objects.filter(name__iexact='Female').first()
        signup.gender = gender
        signup.save()

        serializer = self.get_serializer(signup)
        return response.Response(serializer.data, status=200)

    @decorators.action(detail=True)
    def finish(self, request, pk=None):
        signup = self.get_queryset().get(id=pk)
        signup_data = SignupSerializer(signup).data

        signup_data.pop('id')
        signup_data.pop('school')
        signup_data.pop('gender')
        signup_data.pop('phone_verification_code')
        signup_data.pop('pictures')
        signup_data.pop('interests')
        
        try:
            profile = Profile.objects.create_user(username=signup.email, password=None, created_at=datetime.now(), **signup_data)
        except:
            raise api_exceptions.DuplicateEmailError()

        for interest in signup.interests.all():
            ProfileInterest.objects.create(profile=profile, interest=interest.interest)
        for picture in signup.pictures.all():
            ProfilePicture.objects.create(profile=profile, picture=picture.picture, position=picture.position)

        profile.school = signup.school
        profile.gender = signup.gender

        config = AutumConfig.objects.first()
        if config:
            profile.hide_swipedeck = config.profile_hide_swipedeck_default

        profile.save()

        user = authenticate(username=profile.email, password=None)
        token = Token.objects.create(user=profile)

        profile.last_login = datetime.now()
        profile.save()

        if config:
            for autum_phone in config.autum_phones.all():
                message = Client(settings.TWILIO_SID,settings.TWILIO_AUTH_TOKEN).messages.create(
                    body='NEW AUTUM USER!\n\n{0}\n{1}\n{2}\n\nReferred By:\n{3}\n\n{4}'.format(
                        profile.first_name, 
                        profile.phone, 
                        profile.birthday, 
                        profile.referral_code, 
                        profile.pictures.first().picture_url()
                        ),
                    from_='+1{0}'.format(settings.TWILIO_SENDER_INTERNAL),
                    to="{0}".format(autum_phone.phone)
                )

        return response.Response({'token': token.key, 'user': ProfileSerializer(profile).data})


class SignupPictureViewSet(viewsets.ModelViewSet):
    queryset = SignupPicture.objects.all()
    serializer_class = SignupPictureSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def create(self, request, *args, **kwargs):
        if request.data.get('picture'):
            format, imgstr = request.data.get('picture').split(';base64,') 
            ext = format.split('/')[-1] 
            mutable(request, True)
            request.data['picture'] = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            mutable(request, False)

        serializer = SignupPictureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return response.Response({}, status=201)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #Adjust other image positions
        other_pictures = SignupPicture.objects.filter(signup=instance.signup, position__gt=instance.position)
        for picture in other_pictures:
            picture.position -= 1
            picture.save()
        
        self.perform_destroy(instance)
        return response.Response({}, status=201)


class ProfilePictureViewSet(viewsets.ModelViewSet):
    queryset = ProfilePicture.objects.all()
    serializer_class = ProfilePictureSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    @track_activity
    def create(self, request, *args, **kwargs):
        if request.data.get('picture'):
            format, imgstr = request.data.get('picture').split(';base64,') 
            file_name = ''.join([choice(string.ascii_uppercase + string.digits) for _ in range(10)]) + '.' + format.split('/')[-1] 
            
            mutable(request, True)
            request.data['picture'] = ContentFile(base64.b64decode(imgstr), name=file_name)
            mutable(request, False)

        serializer = ProfilePictureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return response.Response({}, status=201)

    @track_activity
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        #Adjust other image positions
        other_pictures = ProfilePicture.objects.filter(profile=request.user, position__gt=instance.position)
        for picture in other_pictures:
            picture.position -= 1
            picture.save()
        
        self.perform_destroy(instance)
        return response.Response({}, status=201)


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_class = SchoolFilter
    permission_classes = [
        permissions.AllowAny
    ]


class InterestViewSet(viewsets.ModelViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    filter_class = InterestFilter
    permission_classes = [
        permissions.AllowAny
    ]


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    filter_class = ExperienceFilter
    permission_classes = [
        permissions.AllowAny
    ]


class GenderViewSet(viewsets.ModelViewSet):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer
    filter_class = GenderFilter
    permission_classes = [
        permissions.AllowAny
    ]


class ProfileInterestViewSet(viewsets.ModelViewSet):
    queryset = ProfileInterest.objects.all()
    serializer_class = ProfileInterestSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class ProfileExperienceViewSet(viewsets.ModelViewSet):
    queryset = ProfileExperience.objects.all()
    serializer_class = ProfileExperienceSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class SignupInterestViewSet(viewsets.ModelViewSet):
    queryset = SignupInterest.objects.all()
    serializer_class = SignupInterestSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    @track_activity
    @decorators.action(detail=False)
    def meMatches(self, request):
        if self.request.user.is_anonymous:
            raise rest_framework_exceptions.PermissionDenied()

        likes = Like.objects.filter(
            Q(liker=self.request.user) | Q(subject=self.request.user), 
            is_active=True
            )

        serializer = self.get_serializer(likes, many=True)
        return response.Response(serializer.data, status=200)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    pagination_class = LargePagination
    permission_classes = [
        permissions.AllowAny
    ]

    def get_serializer_class(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return AnonProfileSerializer
        return ProfileSerializer


    @decorators.action(detail=False)
    def loginPhone(self, request, *args, **kwargs):
        profile = Profile.objects.filter(phone=request.GET.get('phone')).first()
        if not profile:
            return response.Response({"phone":"Can\'t find your number. Try signing up."}, status=400)
        if profile.is_archived:
            return response.Response({"deleted":"Your account was previously deleted. Please sign up."}, status=400)

        #App store verification test account
        if request.GET.get('phone') == '+12122223333':
            return response.Response({ 'id': profile.id }, status=201)

        code = random.randint(1111,9999)
        profile.phone_verification_code = code
        profile.is_phone_verified = False
        profile.save()

        message = Client(settings.TWILIO_SID,settings.TWILIO_AUTH_TOKEN).messages.create(
            body='Your Autum verification code is: {0}'.format(code),
            from_='+1{0}'.format(settings.TWILIO_SENDER_VERIFICATION),
            to=request.GET.get('phone')
        )

        return response.Response({ 'id': profile.id }, status=201)


    @decorators.action(detail=True)
    def loginPhoneVerification(self, request, pk=True, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        if not profile.is_phone_verified:
            if request.GET.get('phone_verification_code') != str(profile.phone_verification_code):
                return response.Response({"phone":"Invalid verification code."}, status=400)
            else:
                profile.is_phone_verified = True
                profile.save()

        user = authenticate(username=profile.email, password=None)
        Token.objects.filter(user=profile).delete()
        token = Token.objects.create(user=profile)

        profile.last_login = datetime.now()
        profile.save()

        return response.Response({'token': token.key, 'user': ProfileSerializer(profile).data})

    @track_activity
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True

        if request.data.get('picture'):
            format, imgstr = request.data.get('picture').split(';base64,') 
            ext = format.split('/')[-1] 
            mutable(request, True)
            request.data['picture'] = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            mutable(request, False)

        if request.data.get('phone'):
            code = random.randint(1111,9999)
            message = Client(settings.TWILIO_SID,settings.TWILIO_AUTH_TOKEN).messages.create(
                body='Your Autum verification code is: {0}'.format(code),
                from_='+1{0}'.format(settings.TWILIO_SENDER_VERIFICATION),
                to=request.data.get('phone')
            )
            mutable(request, True)
            request.data['phone_verification_code'] = code
            request.data['is_phone_verified'] = False
            mutable(request, False)

        if request.data.get('location'):
            location_str = request.data.get('location')
            lat = float(location_str.split('(')[1].split(' ')[0])
            lng = float(location_str.split('(')[1].split(' ')[1][:-1])

            location = Point(lat, lng, srid=4326)
            toronto = Point(-79.39595138526022, 43.6609225143841, srid=4326)
            distance_toronto = location.distance(toronto) * 100#km

            config = AutumConfig.objects.first()
            if config.profile_hide_swipedeck_default:
                mutable(request, True)
                request.data['hide_swipedeck'] = distance_toronto > config.region_lock_distance_toronto
                mutable(request, False)

        return self.update(request, *args, **kwargs)

    @track_activity
    @decorators.action(detail=False)
    def swipeable(self, request):
        user = self.request.user

        if user.is_anonymous:
            raise rest_framework_exceptions.PermissionDenied()

        if user.match_count > 2:   
            serializer = self.get_serializer(Profile.objects.none(), many=True)
            return response.Response(serializer.data, status=200)

        profiles = self.get_queryset()
        #Filter by gender preference
        if not user.show_female:
            profiles = profiles.filter(gender__is_male_group=True)
        if not user.show_male:
            profiles = profiles.filter(gender__is_female_group=True)
        #Filter by orientation preference
        for orientation in [Profile.GAY, Profile.LESBIAN, Profile.ASEXUAL]:
            if user.orientation == orientation:
                profiles = profiles.filter(orientation=orientation)

        profiles = profiles.filter(
            ~Q(id=user.id),#User's profile
            ~Q(pictures=None),#No photos
            ~Q(liked_by__liker=user),#User has already liked
            Q(height__isnull=True) | Q(height__gte=user.height_min, height__lte=user.height_max),#Height filter, if applied
            birthday__gte=date(now().date().year - user.age_max, now().date().month, now().date().day),#Age minimum
            birthday__lte=date(now().date().year - user.age_min, now().date().month, now().date().day),#Age maximum
            is_hidden=False,#Hidden profiles
            match_count__lt=3#Already at match limit
            ).exclude(
                #Already matched, but user was subject (not liker)
                likes__in=Like.objects.filter(is_match=True,subject=user)
            ).exclude(
                #Otherwise swipeable profiles who already rejected user
                likes__in=Like.objects.filter(subject=user,is_rejected=True)
            ).annotate(
                #Prefer profiles who have already liked the user
                is_liked=Count('likes', filter=Q(likes__subject=user, likes__is_match=False, likes__is_rejected=False))
            ).order_by('-is_liked')

        paged_results = get_page(profiles, request.GET.get('page', 1))
        serializer = self.get_serializer(paged_results, many=True)
        return response.Response(serializer.data, status=200)

    @track_activity
    @decorators.action(detail=True)
    def swipeRight(self, request, pk=None):
        if self.request.user.is_anonymous:
            raise rest_framework_exceptions.PermissionDenied()

        profile = self.get_queryset().filter(id=pk).first()
        user = self.get_queryset().filter(id=self.request.user.id).first()

        #If subject profile has already liked user
        existing_like = Like.objects.filter(liker=profile, subject=user).first()
        if existing_like:
            existing_like.dedupe()#Check for dupes and delete
            if not existing_like.is_rejected:
                existing_like.is_match = True
                existing_like.is_active = True
                existing_like.save()

                send_notification(
                    firebase_token=profile.firebase_token,
                    title="Someone is interested in you! 😉", 
                    body="Don't keep {0} waiting".format(user.first_name)
                    )
            return response.Response(LikeSerializer(existing_like).data, status=200)
        else:
            like = Like.objects.create(liker=user, subject=profile)
            return response.Response(LikeSerializer(like, context={'request': request}).data, status=200)

    @track_activity
    @decorators.action(detail=True)
    def swipeLeft(self, request, pk=None):
        if self.request.user.is_anonymous:
            raise rest_framework_exceptions.PermissionDenied()

        profile = self.get_queryset().filter(id=pk).first()
        user = self.get_queryset().filter(id=self.request.user.id).first()

        existing_like = Like.objects.filter(subject=user, liker=profile).first()
        if existing_like:
            existing_like.dedupe()#Check for dupes and delete
            existing_like.is_rejected = True
            existing_like.save()
            return response.Response(LikeSerializer(existing_like).data, status=200)

        like = Like.objects.create(subject=profile, liker=user, is_rejected=True)
        return response.Response(LikeSerializer(like, context={'request': request}).data, status=200)


    @decorators.action(detail=True)
    def swipeUp(self, request, pk=None):
        if self.request.user.is_anonymous:
            raise rest_framework_exceptions.PermissionDenied()

        profile = self.get_queryset().filter(id=pk).first()
        user = self.get_queryset().filter(id=self.request.user.id).first()

        #If subject profile has already liked user
        existing_like = (Like.objects.filter(liker=user, subject=profile) | Like.objects.filter(liker=profile, subject=user)).first()
        if existing_like:
            existing_like.is_match = True
            existing_like.is_active = True
            existing_like.is_subject_paid = True
            existing_like.save()
            return response.Response(LikeSerializer(existing_like).data, status=200)

        like = Like.objects.create(subject=profile, liker=user, is_liker_paid=True)
        return response.Response(LikeSerializer(like, context={'request': request}).data, status=200)

    @track_activity
    def destroy(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            raise rest_framework_exceptions.PermissionDenied()

        profile = self.get_object()
        if self.request.user.id != profile.id:
            raise rest_framework_exceptions.PermissionDenied()

        for like in profile.likes.filter(is_active=True):
            like.is_active = False
            like.is_ended_by = profile
            like.is_ended_reason = Like.ACCOUNT_DELETED
            like.save()#Updates match_count

        for like in profile.liked_by.filter(is_active=True):
            like.is_active = False
            like.is_ended_by = profile
            like.is_ended_reason = Like.ACCOUNT_DELETED
            like.save()#Updates match_count

        profile.is_archived = True
        profile.is_hidden = True
        profile.save()
        return response.Response({}, status=201)

    @track_activity
    @decorators.action(detail=False)
    def clearLikes(self, request):
        user = self.request.user

        if user.is_anonymous:
            raise rest_framework_exceptions.PermissionDenied()
        #Delete all unresponded left swipes
        Like.objects.filter(Q(updated_at__lt=F('created_at') + timedelta(seconds=3)), liker=user, is_rejected=True).delete()
        return response.Response({}, status=201)


class MeView(generics.RetrieveAPIView, generics.CreateAPIView):
    """ special view to load the requesting user's profile """
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly,
    ]

    def get(self, *args, **kwargs):
        user = self.request.user
        if self.request.user.is_anonymous:
            return response.Response({}, status=200)

        return response.Response(ProfileSerializer(user).data, status=200)

    def create(self, *args, **kwargs):
        return self.get(*args, **kwargs)


