from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    balance = models.IntegerField()
    winnings = models.IntegerField()

    def __unicode__(self):
        return self.user.first_name+' '+self.user.last_name

class Syndicate(models.Model):
    name = models.TextField()
    owner = models.ForeignKey(User)
    winnings = models.IntegerField()
    members  = models.ManyToManyField(UserProfile)

    def __unicode__(self):
        return self.name+': '+self.owner

class PremiumBond(models.Model):
    live = models.BooleanField(default=True)
    user_owner = models.ForeignKey(User)
    group_owner = models.ForeignKey(Syndicate)
    winnings = models.IntegerField(default=0)

class UserSyndicateWinnings(models.Model):
    user=models.ForeignKey(User)
    syndicate=models.ForeignKey(Syndicate)
    winnings=models.IntegerField()

    
