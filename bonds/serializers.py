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
        return str(obj.getTotalInvestment())+'.00'

    def getInfo(self,obj):
        info = ProductInfo.objects.get(pk=7)
        serialized = AcctTypeSerializer(info).data
        serialized['name'] = obj.name
        return serialized

class UserPremiumBondsAsAcctSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField(method_name='getDate')
    balance = serializers.SerializerMethodField(method_name='getTotalInvestment')
    info    = serializers.SerializerMethodField(method_name='getInfo')
    class Meta:
        model=User
        fields=('created','id','info','balance')

    def getInfo(self,obj):
        info = ProductInfo.objects.get(pk=6)
        return AcctTypeSerializer(info).data
    
    def getTotalInvestment(self,obj):
        bonds = PremiumBond.objects.filter(group_owned=False,user_owner=obj,live=True)
        return len(bonds)
    def getDate(self,obj):
        return obj.date_joined
        
class SyndicateSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField(method_name='getMembersAndShares')
    owner = UserShortSerializer(read_only=True)
    balance = serializers.SerializerMethodField(method_name='getTotalInvestment')
    class Meta:
        model=Syndicate
        fields=('name','owner','balance','winnings','members')
    def getTotalInvestment(self,obj):
        return obj.getTotalInvestment()

    def getMembersAndShares(self,obj):
        mem_list =[]
        user_share = obj.getSharesAsMoney()
        for (user,share) in user_share:
            user_data = UserShortSerializer(user).data
            user_data['share']=share
            mem_list+=[user_data]
        return mem_list
    
    def getUserShares(self,obj):
        shares = {}
       
        
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
