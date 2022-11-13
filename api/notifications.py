
from firebase_admin import messaging
from django.conf import settings
from api import models

#######################
# Send a notification #
#######################

def send_notification(firebase_token, title, body):
    if firebase_token: #Edge case check in case user's device is not yet registered
        notification = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body, 
                image=settings.LOGO_URL
            ),
            token=firebase_token
        )
        try:
            messaging.send(notification)
            models.NotificationLog.objects.create(token=firebase_token,title=title, body=body, is_success=True)
        except:
            models.NotificationLog.objects.create(token=firebase_token,title=title, body=body)
    else:
        models.NotificationLog.objects.create(title=title, body=body)