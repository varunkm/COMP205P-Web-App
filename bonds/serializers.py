from django.contrib.auth.models import User
from models import *
from rest_framework import serializers


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['pk','username','first_name']
    

class SyndicateShortSerializer(serializers.ModelSerializer):
    class Meta:
        model=Syndicate
        fields=['name']

        
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('pk','username', 'email','first_name','last_name')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    class Meta:
        model=UserProfile
        fields=['user']
        
class SyndicateSerializer(serializers.ModelSerializer):
    members = UserProfileSerializer(read_only=True,many=True)
    owner = UserSerializer(read_only=True)
    class Meta:
        model=Syndicate
        fields=('name','owner','winnings','members')
        
class AcctTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductInfo
        exclude=[]
        
class AccountSerializer(serializers.ModelSerializer):
    info = AcctTypeSerializer(read_only=True)
    owner = UserProfileSerializer(read_only=True)
    class Meta:
        model=Account
        fields=('created','owner','info','balance')
        

class PremiumBondSerializer(serializers.ModelSerializer):
    user_owner = UserShortSerializer(read_only=True)
    group_owner= SyndicateShortSerializer(read_only=True)
    class Meta:
        model = PremiumBond
        fields=('created','live','user_owner','group_owner','winnings')


