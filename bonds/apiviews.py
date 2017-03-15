from django.contrib.auth.models import User
from models import *
from serializers import *
from django.http import Http404, HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

class UserDetail(APIView):
    def get_object(self,pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self,request,pk,format=None):
        user=self.get_object(pk)
        if request.user == user:
            serializer = UserSerializer(user,context={'request':request})
            return Response(serializer.data)
        else:
            serializer = UserShortSerializer(user,context={'request':request})
            return Response(serializer.data)

class SyndicateList(APIView):
    def get(self,request,format=None):
        syndicates = request.user.userprofile.syndicate_set.all()
        serializer = SyndicateSerializer(syndicates,many=True,context={'request':request})
        return Response(serializer.data)

class SyndicateDetail(APIView):
    def get_object(self,pk):
        try:
            return Syndicate.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self,request,pk,format=None):
        syndicate = self.get_object(pk)
        if syndicate in request.user.userprofile.syndicate_set.all():
            serializer = SyndicateSerializer(syndicate,context={'request':request})
            return Response(serializer.data)
        else:
            return HttpResponseForbidden()

class AccountList(APIView):
    def get(self,request,format=None):
        accounts = request.user.userprofile.account_set.all()
        serializer = AccountSerializer(accounts,many=True,context={'request':request})
        return Response(serializer.data)

class AccountDetail(APIView):
    def get(self,request,pk,format=None):
        account = get_object_or_404(Account,pk=pk)
        if account.owner == request.user.userprofile:
            serializer = AccountSerializer(account,context={'request':request})
            return Response(serializer.data)
        else:
            return HttpResponseForbidden()

class BondsList(APIView):
    
    def get(self,request,syndicate_pk,format=None):
        syndicate = get_object_or_404(Syndicate,syndicate_pk)
        if syndicate in request.user.user_profile.syndicate_set.all():
            bonds = PremiumBond.objects.filter(group_owner=syndicate)
            serializer = PremiumBondSerializer(bonds,many=True,context={'request':request})
            return Response(serializer.data)
        else:
            return HttpResponseForbidden()

        
