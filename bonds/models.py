from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):
    LANG_CHOICES = (('EN','ENGLISH'),('FR','FRENCH'))
    user = models.OneToOneField(User)
    balance = models.IntegerField(default=0)
    winnings = models.IntegerField(default=0)
    language = models.TextField(default="EN",choices=LANG_CHOICES)
    security_question = models.TextField(default="")
    answer = models.TextField(default="")
    profilepicture = models.TextField(default="")
    dummy_sq = models.TextField(default="")
    dummy_ans = models.TextField(default="")
    dummy_pwd = models.TextField(default="")

    def __unicode__(self):
        return self.user.first_name+' '+self.user.last_name

class Syndicate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.TextField()
    owner = models.ForeignKey(User,related_name='managed')
    winnings = models.IntegerField()
    members  = models.ManyToManyField(User)

    def __unicode__(self):
        return self.name+': '+self.owner

class PremiumBond(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    live = models.BooleanField(default=True)
    user_owner = models.ForeignKey(User)
    group_owner = models.ForeignKey(Syndicate)
    winnings = models.IntegerField(default=0)

class UserSyndicateWinnings(models.Model):
    user=models.ForeignKey(User)
    syndicate=models.ForeignKey(Syndicate)
    winnings=models.IntegerField()

class ChatMessage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    syndicate = models.ForeignKey(Syndicate)
    writer = models.ForeignKey(User)
    message = models.CharField(max_length=140)

class ProductInfo(models.Model):
    name = models.TextField()
    description = models.TextField()
    interest_rate = models.DecimalField(max_digits=6,decimal_places=5)
    min_deposit = models.IntegerField()
    payout_period = models.IntegerField()
    
    
class Account(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
    info  = models.ForeignKey(ProductInfo)
    balance = models.DecimalField(max_digits=12,decimal_places=2)

class Transaction(models.Model):
    account = models.ForeignKey(Account)
    amount = models.DecimalField(max_digits=12,decimal_places=2)
    kind = models.TextField()
