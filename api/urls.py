"""dispatch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings

from .views import *


app_name = 'api'

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'ambassadors', AmbassadorViewSet)
router.register(r'genders', GenderViewSet)
router.register(r'interests', InterestViewSet)
router.register(r'experiences', ExperienceViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'profile-pictures', ProfilePictureViewSet)
router.register(r'profile-interests', ProfileInterestViewSet)
router.register(r'profile-experiences', ProfileExperienceViewSet)
router.register(r'schools', SchoolViewSet)
router.register(r'signups', SignupViewSet)
router.register(r'signup-pictures', SignupPictureViewSet)
router.register(r'signup-interests', SignupInterestViewSet)

urlpatterns = [
    #ENDPOINTS
    url(r'^me/', MeView.as_view(), name='me'),
    url(r'^amity-webhook', amity_webhook, name='amity-webhook'),
    url(r'^receive/sms', receive_sms, name='sms-inbound'),
    url('', include((router.urls, 'api'), namespace='models')),
]

