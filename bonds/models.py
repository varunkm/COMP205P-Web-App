from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
import datetime
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Sum

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
    dummy_sq = models.TextField(default="",null=True,blank=True)
    dummy_ans = models.TextField(default="",null=True,blank=True)
    dummy_pwd = models.TextField(default="",null=True,blank=True)

    def __unicode__(self):
        return self.user.first_name+' '+self.user.last_name
    def getSoleOwnedWinnings(self):
        bonds = PremiumBond.objects.filter(group_owned=False,user_owner=self.user).aggregate(Sum('winnings'))
        if bonds['winnings__sum'] is not None:
            return bonds['winnings__sum']
        else:
            return 0
    def buyBonds(self,amount):
        if amount > self.balance:
            return False
        for i in range(amount):
            new_bond = PremiumBond(group_owned=False,user_owner=self.user,live=True,winnings=0)
            new_bond.save()
        self.balance-=amount
        self.save()
        return True

    def sellBonds(self,amount):
        userBonds = PremiumBond.objects.filter(group_owned=False,user_owner=self.user,live=True)
        if len(userBonds) < amount:
            return False
        bondsToDelete = userBonds[:amount]
        for bond in bondsToDelete:
            bond.live=False
            bond.save()
        self.balance+=amount
        self.save()
        return True

class Syndicate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.TextField()
    owner = models.ForeignKey(User,related_name='managed')
    winnings = models.IntegerField()
    members  = models.ManyToManyField(User)

    def getBonds(self):
        return PremiumBond.objects.filter(group_owner=self)

    def getLiveUserBonds(self,usr):
        return PremiumBond.objects.filter(group_owner=self,user_owner=usr,live=True)
    
    def __unicode__(self):
        return self.name+': '+str(self.owner)

    def getTotalInvestment(self):
        bonds = PremiumBond.objects.filter(group_owner=self,live=True)
        return len(bonds)
    
    def getSharesAsMoney(self):
        user_investment = []
        for user in self.members.all():
            user_bonds = PremiumBond.objects.filter(group_owner=self,user_owner=user,live=True)
            user_investment+=[(user,len(user_bonds))]
        return user_investment
    
    def getSharesAsFractions(self):
        total_investment = self.getTotalInvestment()
        user_investment  = self.getSharesAsMoney()
        user_shares = []
        for (user,investment) in user_investment:
            if total_investment==0:
                user_shares+=[(user,0.0)]
                continue
            user_shares+=[(user,float(investment)/float(total_investment))]
        return user_shares
    
    def sellBonds(self,user,amount):
        if not user in self.members.all():
            return False
        userBonds = PremiumBond.objects.filter(group_owner=self,user_owner=user,live=True)
        if len(userBonds) < amount:
            return False
        bondsToDelete = userBonds[:amount]
        for bond in bondsToDelete:
            bond.live=False
            bond.save()
        user.userprofile.balance+=amount
        user.userprofile.save()
        return True

    def buyBonds(self,user,amount):
        if not user in self.members.all():
            return False
        if user.userprofile.balance < amount:
            return False

        user.userprofile.balance -= amount
        user.userprofile.save()

        for i in range(amount):
            new_bond = PremiumBond(user_owner=user,group_owner=self)
            new_bond.save()
        
        return True

    def removeMember(self,usr):
        if not usr in self.members.all():
            return False
        usr_bonds = self.getLiveUserBonds(usr)
        amt = len(usr_bonds)
        self.sellBonds(usr,amt)
        self.members.remove(usr)  
        
    def safeDestroy(self):
        for member in self.members.all():
            self.removeMember(member)
        self.delete()

    def addMember(self,user):
        if not user in self.members.all():
            self.members.add(user)
        return True

class PremiumBond(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    live = models.BooleanField(default=True)
    group_owned = models.BooleanField(default=True)
    user_owner = models.ForeignKey(User)
    group_owner = models.ForeignKey(Syndicate, blank=True, null=True)
    winnings = models.IntegerField(default=0)
    def __unicode__(self):
        return str(self.pk)

class UserSyndicateWinnings(models.Model):
    user=models.ForeignKey(User)
    syndicate=models.ForeignKey(Syndicate)
    winnings=models.IntegerField()

    def __unicode__(self):
        return str(self.user) +" : "+str(self.syndicate)

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
    link = models.CharField(max_length=140,default="")
    
class Account(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
    info  = models.ForeignKey(ProductInfo)
    balance = models.DecimalField(max_digits=12,decimal_places=2)
    
    def daysSinceInception(self):
        now = datetime.datetime.now()
        created = self.created
        delta = (now.date()-created.date()).days
        return delta
    
    def eligibleForPayout(self):
        days = self.daysSinceInception()
        return days % self.info.payout_period == 0
    def payout(self):
        amount = self.info.interest_rate*self.balance
        self.balance+=amount
        return amount
            

class Transaction(models.Model):
    created=models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account)
    amount = models.DecimalField(max_digits=12,decimal_places=2)
    kind = models.TextField()

class BondReward(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    winning_bonds= models.ManyToManyField(PremiumBond)
    total_payout = models.IntegerField()
    winning_number = models.IntegerField()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
