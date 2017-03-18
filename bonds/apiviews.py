from django.contrib.auth.models import User
from models import *
from serializers import *
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404, HttpResponseForbidden
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework import status


class UserDetail(APIView):
    """
####Return information about user with primary key specified in URL. Will return more detailed information about logged in user
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get_object(self,pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    
    def get(self,request,pk,format=None):
        user=self.get_object(pk)
        if request.user == user:
            serializer = UserSerializer(user,context={'request':request})
            data = serializer.data
            data['password']=''
            data['security_question']=''
            data['answer']=''
            return Response(data)
        else:
            serializer = UserShortSerializer(user,context={'request':request})
            return Response(serializer.data)

class SyndicateList(APIView):
    """
####Return a list of the user's syndicates
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request,format=None):
        syndicates = request.user.syndicate_set.all()
        serializer = SyndicateSerializer(syndicates,many=True,context={'request':request})
        return Response(serializer.data)

class SyndicateDetail(APIView):
    """
####Returns details of syndicate with primary key specified in URL. Will only give information if logged in user belongs to the syndicate
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get_object(self,pk):
        try:
            return Syndicate.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self,request,pk,format=None):
        syndicate = self.get_object(pk)
        if syndicate in request.user.syndicate_set.all():
            serializer = SyndicateSerializer(syndicate,context={'request':request})
            return Response(serializer.data)
        else:
            return HttpResponseForbidden()

class AccountList(APIView):
    """
####Return a list of the logged in user's accounts
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request,format=None):
        accounts = request.user.account_set.all()
        serializer = AccountSerializer(accounts,many=True,context={'request':request})
        return Response(serializer.data)

class AccountDetail(APIView):
    """
####Returns details of account with primary key specified in URL. Will only give information if account belongs to logged in user
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request,pk,format=None):
        account = get_object_or_404(Account,pk=pk)
        if account.owner == request.user:
            serializer = AccountSerializer(account,context={'request':request})
            return Response(serializer.data)
        else:
            return HttpResponseForbidden()

class BondsList(APIView):
    """
    get:
####Return list of bonds belonging to syndicate with primary specified in URL. Logged in user must belong to the syndicate.
    post:
####Buy a number of bonds on behalf of logged in user within the syndicate specified in URL. Expects JSON object specifiying amount. e.g. : 
###`{"amount":5}`
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request,syndicate_pk,format=None):
        syndicate = get_object_or_404(Syndicate,pk=syndicate_pk)
        if syndicate in request.user.syndicate_set.all():
            bonds = PremiumBond.objects.filter(group_owner=syndicate)
            serializer = PremiumBondSerializer(bonds,many=True,context={'request':request})
            return Response(serializer.data)
        else:
            return HttpResponseForbidden()
        
    parser_classes = (JSONParser,)
    def post(self,request,syndicate_pk,format=None):
        syndicate = get_object_or_404(Syndicate,pk=syndicate_pk)
        content = request.data
        profile = request.user.userprofile
        
        if syndicate in request.user.syndicate_set.all():
            if 'amount' in content.keys():
                if content['amount'] <= profile.balance:
                    amt = content['amount']
                    for b in range(0,amt):
                        new_bond = PremiumBond(user_owner=request.user,group_owner=syndicate)
                        new_bond.save()
                    profile.balance-=amt
                    profile.save()
                    return Response({'response':'success'},status=status.HTTP_201_CREATED)
                else:
                    return Response({'response':'failure','reason':'insufficient balance'},status=status.HTTP_409_CONFLICT)
            else:
                return Response({'response':'failure','reason':'unexpected request content'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponseForbidden()
    
