from django.utils.timezone import now
from .models import Profile


class SetLastVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_anonymous:
            # Update last visit time after request finished processing.
            Profile.objects.filter(pk=request.user.pk).update(last_visit=now())
        response = self.get_response(request)
        return response
