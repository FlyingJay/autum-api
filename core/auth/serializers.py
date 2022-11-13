from rest_framework import serializers


class PasswordRegisterSerializer(serializers.Serializer):
    topic = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    location = serializers.CharField()
    email = serializers.EmailField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()


class PasswordAuthSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    password = serializers.CharField()
