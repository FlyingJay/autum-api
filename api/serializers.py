from rest_framework import serializers
from expander import ExpanderSerializerMixin #https://github.com/silverlogic/djangorestframework-expander
from drf_extra_fields import fields as drf_extra_fields, geo_fields
from rest_framework_gis.serializers import GeoModelSerializer

from .models import *


class CountrySerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id',
            'name'
        ]


class ProvinceSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = [
            'id', 
            'name',
            'country'
        ]

        expandable_fields = {
            'country': CountrySerializer
        }


class CitySerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    location = geo_fields.PointField(required=False)

    class Meta:
        model = City
        fields = [
            'id',
            'name',
            'province',
            'location'
        ]

        expandable_fields = {
            'province': ProvinceSerializer
        }


class AmbassadorSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Ambassador
        fields = [
            'id',
            'first_name',
            'last_name',
        ]


class ExperienceSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            'id',
            'name',
        ]


class ProfileExperienceSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProfileExperience
        fields = [
            'id',
            'profile',
            'experience',
        ]

        expandable_fields = {
            'experience': ExperienceSerializer
        }


class InterestSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = [
            'id',
            'name',
        ]


class ProfileInterestSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProfileInterest
        fields = [
            'id',
            'profile',
            'interest',
        ]

        expandable_fields = {
            'interest': InterestSerializer
        }


class SignupInterestSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SignupInterest
        fields = [
            'id',
            'signup',
            'interest',
        ]

        expandable_fields = {
            'interest': InterestSerializer
        }


class GenderSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = [
            'id',
            'name',
        ]


class SignupPictureSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = SignupPicture
        fields = [
            'id',
            'signup',
            'picture',
            'position',
        ]


class ProfilePictureSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = [
            'id',
            'profile',
            'picture',
            'position',
            'picture_url',
        ]


class AnonProfileSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id',
            'first_name',
        ]


class ProfilePhoneLoginSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id',
            'phone',
        ]


class SchoolSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'country',
        ]


class ProfileSerializer(GeoModelSerializer, ExpanderSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Profile
        geo_field = 'location'
        fields = [
            'id',
            'phone',
            'first_name',
            'birthday',
            'height',
            'gender',
            'orientation',
            'description',
            'job',
            'company',
            'school',
            'wants_relationship',
            'age_min',
            'age_max',
            'height_min',
            'height_max',
            'show_male',
            'show_female',
            'location',
            'distance_max',
            'show_distance_km',
            'show_height_cm',
            'allows_notifications',
            'hide_swipedeck',
            'hide_tutorial_swiping',
            'hide_tutorial_matchlimit',
            'hide_tutorial_matches',
            'hide_tutorial_endconvo',
            'deleted_reason_bugs',
            'deleted_reason_quality',
            'deleted_reason_quantity',
            'deleted_reason_another_onapp',
            'deleted_reason_another_offapp',
            'deleted_reason_other',
            'deleted_reason_other_text',
            'is_hidden',
            'is_premium',
            'remaining_likes_count',
            'profile_picture_url',
            'is_phone_verified',
            'phone_verification_code',
            'firebase_token',
            'referral_code',
            'importance_interests',
            'importance_experiences',
            'gradient',
            'pictures',
            'interests',
            'experiences',
        ]

        expandable_fields = {
            'pictures': (ProfilePictureSerializer, (), { 'many': True }),
            'interests': (ProfileInterestSerializer, (), { 'many': True }),
            'experiences': (ProfileExperienceSerializer, (), { 'many': True }),
            'gender': GenderSerializer,
            'school': SchoolSerializer
        }


class SignupSerializer(GeoModelSerializer, ExpanderSerializerMixin, serializers.ModelSerializer):
    pictures = SignupPictureSerializer(required=False, many=True)
    interests = SignupInterestSerializer(required=False, many=True)

    class Meta:
        model = Signup
        geo_field = 'location'
        fields = [
            'id',
            'phone',
            'email',
            'first_name',
            'birthday',
            'height',
            'gender',
            'orientation',
            'description',
            'job',
            'company',
            'school',
            'wants_relationship',
            'age_min',
            'age_max',
            'show_male',
            'show_female',
            'location',
            'distance_max',
            'show_distance_km',
            'allows_notifications',
            'is_hidden',
            'phone_verification_code',
            'is_phone_verified',
            'importance_interests',
            'referral_code',
            'pictures',
            'interests',
        ]

        expandable_fields = {
            'interests': (SignupInterestSerializer, (), { 'many': True }),
            'pictures': (SignupPictureSerializer, (), { 'many': True }),
            'gender': GenderSerializer,
            'school': SchoolSerializer
        }


class LikeSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    liker = ProfileSerializer()
    subject = ProfileSerializer()
    is_user_liker = serializers.SerializerMethodField()
    def get_is_user_liker(self, like):
        request = self.context.get("request")
        if request and request.user:
            return request.user.id == like.liker.id
        return None

    class Meta:
        model = Like
        fields = [
            'id',
            'liker',
            'subject',
            'is_match',
            'is_active',
            'is_rejected',
            'is_user_liker',
            'is_liker_paid',
            'is_subject_paid',
            'is_ended',
            'is_ended_by',
            'is_ended_reason',
            'amity_channel',
        ]

        expandable_fields = {
            'liker': ProfileSerializer,
            'subject': ProfileSerializer
        }





