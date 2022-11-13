import rest_framework_filters as filters
from django.contrib.auth.models import User
from api import models
from django.db.models import Q
from datetime import datetime

# FILTER CLASSES

class SchoolFilter(filters.FilterSet):
    class Meta:
        model = models.School
        fields = {
            'id': ['exact','in'],
            'name': ['icontains']
        }

class InterestFilter(filters.FilterSet):
    class Meta:
        model = models.Interest
        fields = {
            'id': ['exact','in'],
            'name': ['icontains']
        }

class ExperienceFilter(filters.FilterSet):
    class Meta:
        model = models.Experience
        fields = {
            'id': ['exact','in'],
            'name': ['icontains']
        }


class GenderFilter(filters.FilterSet):
    class Meta:
        model = models.Gender
        fields = {
            'id': ['exact','in'],
            'name': ['icontains']
        }
