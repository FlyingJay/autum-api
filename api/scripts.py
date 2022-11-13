

from django.conf import settings
from twilio.rest import Client
from api import models
from django.db.models import Count, Q
from .notifications import send_notification

def test_fcm(token, title, body):
    send_notification(
        firebase_token=token,
        title=title, 
        body=body
        )


def dedupe_likes():
    all_likes = models.Like.objects.values('liker','subject').distinct()

    for a_like in all_likes.all():
        likes = models.Like.objects.filter(liker=a_like['liker'], subject=a_like['subject'])
        mirror_likes = models.Like.objects.filter(liker=a_like['subject'], subject=a_like['liker'])

        dupes = likes | mirror_likes
        if dupes.count() > 1:
            matches = dupes.filter(is_match=True)
            rejections = dupes.filter(is_rejected=True)

            if matches.count() > 0:
                dupes.exclude(id=matches.first().id).delete()
            elif rejections.count() > 0:
                dupes.exclude(id=rejections.first().id).delete()
            else:
                dupes.exclude(id=dupes.first().id).delete()


#Will return nothing if there are no duplicates remaining.
def audit_dupes():
    all_likes = models.Like.objects.values('liker','subject').distinct()
    #print(all_likes)

    for a_like in all_likes.all():
        likes = models.Like.objects.filter(liker=a_like['liker'], subject=a_like['subject'])
        mirror_likes = models.Like.objects.filter(liker=a_like['subject'], subject=a_like['liker'])

        dupes = likes | mirror_likes
        if dupes.count() > 1:
            print("{0} - {1} {2}".format(dupes.count(), a_like['liker'], a_like['subject']))

            matches = dupes.filter(is_match=True)
            rejections = dupes.filter(is_rejected=True)

            if matches.count() > 0:
                print("Found Match among {0} dupes.".format(dupes.count()))
            elif rejections.count() > 0:
                print("Found rejection among {0} dupes.".format(dupes.count()))
            else:
                print("{0} dupe right swipes.".format(dupes.count()))


def party_sms():
    for profile in models.Profile.objects.filter(is_archived=False).exclude(phone=None):
        message = Client(settings.TWILIO_SID,settings.TWILIO_AUTH_TOKEN).messages.create(
            body='Hey {0}! 😊 Thank you for downloading Autum.  You\'re invited to attend our exclusive launch party at Arcane on March 24th! Your first drink is on us. You and your friends can register here: https://www.tinyurl.com/AutumLaunch'.format(profile.first_name),
            from_='+1{0}'.format(settings.TWILIO_SENDER_MARKETING),
            to="{0}".format(profile.phone)
        )
        print("Sent to {0}".format(profile.phone))

def party_sms_2():
    for profile in models.Profile.objects.filter(is_archived=False).exclude(phone=None):
        message = Client(settings.TWILIO_SID,settings.TWILIO_AUTH_TOKEN).messages.create(
            body='Hey {0}! 😊 So excited to have you on Autum! As you know, tomorrow 9PM is our exclusive launch party at Arcane and we\'d love if you could join us. First drink is free and merch for you and your friends!! RSVP here if you haven’t already: https://www.tinyurl.com/AutumLaunch'.format(profile.first_name),
            from_='+1{0}'.format(settings.TWILIO_SENDER_MARKETING),
            to="{0}".format(profile.phone)
        )
        print("Sent to {0}".format(profile.phone))

"""
def test_sms():
    for profile in models.Profile.objects.filter(is_archived=False,phone="+12892086151").exclude(phone=None):
        message = Client(settings.TWILIO_SID,settings.TWILIO_AUTH_TOKEN).messages.create(
            body='Hey {0}! 😊 Thank you for downloading Autum.  You\'re invited to attend our exclusive launch party at Arcane on March 24th! Your first drink is on us. You and your friends can register here: https://www.tinyurl.com/AutumLaunch'.format(profile.first_name),
            from_='+1{0}'.format(settings.TWILIO_SENDER_MARKETING),
            to="{0}".format(profile.phone)
        )
        print("Sent to {0}".format(profile.phone))
"""

def test_signup_sms():
    config = models.AutumConfig.objects.first()
    profile = models.Profile.objects.first()

    for autum_phone in config.autum_phones.all():
        message = Client(settings.TWILIO_SID,settings.TWILIO_AUTH_TOKEN).messages.create(
            body='NEW AUTUM USER!\n\n{0}\n{1}\n{2}\n\nReferred By:\n{3}\n\n{4}'.format(
                profile.first_name, 
                profile.phone, 
                profile.birthday, 
                profile.referral_code, 
                profile.pictures.first().picture_url()
                ),
            from_='+1{0}'.format(settings.TWILIO_SENDER_MARKETING),
            to="{0}".format(autum_phone.phone)
        )
