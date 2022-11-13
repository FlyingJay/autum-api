from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth import login, authenticate, logout
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics
from datetime import *

from api.models import Profile
from api.serializers import ProfileSerializer

from .serializers import *
from .exceptions import *
from .forms import *


#########
# VIEWS #
#########

class PasswordRegisterView(generics.CreateAPIView):
	serializer_class = PasswordRegisterSerializer

	def create(self, request):
		if request.user.is_authenticated:
			raise BadRequest("Must be logged out to create an account.")

		serializer = PasswordRegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		name = request.data.get('name')
		description = request.data.get('description')
		location = request.data.get('location')

		email = request.data.get('email')
		password1 = request.data.get('password1')
		password2 = request.data.get('password2')

		if Profile.objects.filter(email__iexact=email).first():
			raise BadRequest("Email already in use.")
		if password1 != password2:
			raise BadRequest("Passwords don't match.")

		profile = Profile.objects.create_user(
			username=email,
			email=email,
			password=password1,
			name=name,
			description=description,
			location=location
			)

		try:
			token = Token.objects.get(user=profile)
		except:
			token = Token.objects.create(user=profile)

		user = authenticate(username=email, password=password1)
		login(request, user)

		profile.last_login = datetime.now()
		profile.save()

		return Response({'token': token.key, 'user': ProfileSerializer(profile).data})
		#return redirect('settings')


class PasswordAuthView(generics.CreateAPIView):
	serializer_class = PasswordAuthSerializer

	def create(self, request):
		serializer = PasswordAuthSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		email = request.data.get('email')
		password = request.data.get('password')

		try:
			profile = Profile.objects.get(email__iexact=email)
		except:
			raise BadRequest("User not found.")

		if not profile.check_password(password):
			raise BadRequest("Incorrect email/password")

		try:
			token = Token.objects.get(user=profile)
		except:
			token = Token.objects.create(user=profile)

		user = authenticate(username=email, password=password)
		if user is not None:
			login(request, user)
			Profile.objects.filter(id=profile.id).update(last_login=datetime.now())
			return Response({'token': token.key, 'user': ProfileSerializer(profile).data})
		
		raise BadRequest("Incorrect username/password")
		#return redirect('feed')


class ForgotPasswordView(generics.CreateAPIView):
	serializer_class = ForgotPasswordSerializer

	def create(self, request):
		serializer = ForgotPasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		try:
			profile = Profile.objects.get(email=serializer.data.get('email'))
			profile.generate_password_reset_token()
			profile.save()

			send_mail(
				"Reset Password", 
				'',
				settings.DEFAULT_FROM_EMAIL,
				[profile.email], 
				html_message=render_to_string(
					'password_reset_email.html', {
						'url': profile.get_password_reset_url()
					}),
				)
		except ObjectDoesNotExist as e:
			#Add a message template for user not existing.
			pass

		return redirect("/password-reset-submitted")


def LogoutView(request):
	logout(request)
	return Response({})
	#return redirect('login')