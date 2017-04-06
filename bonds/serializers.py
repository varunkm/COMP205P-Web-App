from django.contrib.auth.models import User
from models import *
from rest_framework import serializers


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','first_name']
    

class SyndicateShortSerializer(serializers.ModelSerializer):
    class Meta:
        model=Syndicate
        fields=['name']

        
class UserSerializer(serializers.ModelSerializer):
    balance=serializers.IntegerField(source='userprofile.balance')
    winnings=serializers.IntegerField(source='userprofile.winnings')
    language=serializers.CharField(source='userprofile.language')
    security_question=serializers.CharField(source='userprofile.dummy_sq')
    answer=serializers.CharField(source='userprofile.dummy_ans')
    profilepicture=serializers.CharField(source='userprofile.profilepicture')
    password=serializers.CharField(source='userprofile.dummy_pwd')
    
    class Meta:
        model = User
        exclude=['password','groups','user_permissions','date_joined','is_staff','is_active','is_superuser','last_login']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    class Meta:
        model=UserProfile
        fields=['user']


class SyndicateAsAcctSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(method_name='getTotalInvestment')
    info    = serializers.SerializerMethodField(method_name='getInfo')
    class Meta:
        model=Syndicate
        fields=('created','id','info','balance')
        
    def getTotalInvestment(self,obj):
        return obj.getTotalInvestment()

    def getInfo(self,obj):
        info = ProductInfo.objects.get(pk=7)
        serialized = AcctTypeSerializer(info).data
        serialized['name'] = obj.name
        return serialized
        
    
        
class SyndicateSerializer(serializers.ModelSerializer):
    members = UserShortSerializer(read_only=True,many=True)
    owner = UserShortSerializer(read_only=True)
    balance = serializers.SerializerMethodField(method_name='getTotalInvestment')
    shares  = serializers.SerializerMethodField(method_name='getUserShares')
    class Meta:
        model=Syndicate
        fields=('name','owner','balance','winnings','shares','members')
    def getTotalInvestment(self,obj):
        return obj.getTotalInvestment()

    def getUserShares(self,obj):
        shares = {}
        user_share = obj.getSharesAsMoney()
        for (user,share) in user_share:
            shares[user.pk]=share
        return shares
        
class AcctTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductInfo
        exclude=[]
        
class AccountSerializer(serializers.ModelSerializer):
    info = AcctTypeSerializer(read_only=True)
    class Meta:
        model=Account
        fields=('created','id','info','balance')
        

class PremiumBondSerializer(serializers.ModelSerializer):
    user_owner = UserShortSerializer(read_only=True)
    group_owner= SyndicateShortSerializer(read_only=True)
    class Meta:
        model = PremiumBond
        fields=('created','live','user_owner','group_owner','winnings')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
