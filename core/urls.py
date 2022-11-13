"""exercise URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from api.urls import router as api_router
from api.urls import urlpatterns as api_urlpatterns

from core.auth.views import *
from .views import *


urlpatterns = [
    #APPS
    path('v1/', include('api.urls', namespace='v1')),
    path('admin/', admin.site.urls),
    path('.well-known/assetlinks.json', verify_android_deeplinks, name='verify_android_deeplinks'),
    path('tiktok', app_view, name='tiktok_view'),#duplicate
    path('app', app_view, name='app_view'),#duplicate
    #TOOLS
    url('tools', ToolsView.as_view(), name='tools'),
    url('map/deleted', DeletedMapView.as_view(), name='profiles-map-deleted'),
    url('map/waiting-list', WaitingListMapView.as_view(), name='profiles-map-waiting-list'),
    url('map', MapView.as_view(), name='profiles-map'),
    url('stats', StatsView.as_view(), name='stats'),
    #FORMS
    url(r'^auth/register', PasswordRegisterView.as_view(), name='auth-register'),
    url(r'^auth/password', PasswordAuthView.as_view(), name='auth-password'),
    url(r'^auth/forgot-password', ForgotPasswordView.as_view(), name='auth-forgot-password'),
    url(r'^auth/logout', LogoutView, name='auth-logout'),
    url(r'^password-reset/$', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    url(r'^password-reset-submitted/$', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_submitted.html'), name='password_reset_submitted'),
    path(r'password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    url(r'^password-reset-done/$', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_confirm_submitted.html'), name='password_reset_complete'),
]

if settings.STORAGE_BACKEND != 'S3':
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL.replace(settings.API_BASE_URL, ''), document_root=settings.MEDIA_ROOT)

