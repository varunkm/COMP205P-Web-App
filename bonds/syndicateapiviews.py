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
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from rest_framework.renderers import *


class SyndicateList(APIView):
    """
    Return a list of the user's syndicates
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request,format=None):
        syndicates = request.user.syndicate_set.all()
        serializer = SyndicateSerializer(syndicates,many=True,context={'request':request})
        return Response(serializer.data)


class AddUser(APIView):
    """
    #POST
    add user by email. Specify email in json: `{"user":"foo@bar.com"}`. The backend will lookup user in database by email and add them to the group if the user is found.
    """

    def post(self,request,syndicate_pk,format=None):
        syndicate = get_object_or_404(Syndicate,pk=syndicate_pk)
        user = request.user
        content = request.data
        if 'user' in content.keys():
            email = content['user']
            user_to_add = get_object_or_404(User,email=email)
            syndicate.addMember(user_to_add)
            return Response({'response':'success'},status=HTTP_200_OK)
        return Response({'response':'failure'},status=HTTP_400_BAD_REQUEST)
    
    
class RemoveUser(APIView):
    """
    #POST
    remove user from syndicate. User must be specified in JSON with their id.
    `{"user":3}`.

    If the owner is removed from the syndicate, the syndicate will be safely deleted.
    """
    def post(self,request,syndicate_pk,format=None):
        syndicate=get_object_or_404(Syndicate,pk=syndicate_pk)
        user = request.user
        content = request.data
        if syndicate.owner != user:
            return HttpResponseForbidden()

        if 'user' in content.keys():
            user_to_delete = get_object_or_404(User,pk=content['user'])
            if user_to_delete==user:
                syndicate.safeDestroy()
                return Response({"response":"success, syndicate deleted"},status=status.HTTP_200_OK)
            else:
                syndicate.removeMember(user_to_delete)
                return Response({"response":"success, user removed"},status=status.HTTP_200_OK)
        return Response({"response":"failure"},status=status.HTTP_400_BAD_REQUEST)
            

class SyndicateDetail(APIView):
    """
    Returns details of syndicate with primary key specified in URL. Will only give information if logged in user belongs to the syndicate
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

   
class BondsList(APIView):
    """
    #POST:
    Buy/Sell a number of bonds on behalf of logged in user within the syndicate specified in URL. Expects JSON object specifiying amount and transaction type. e.g. : 

    `{"kind":"BUY","amount":5}`
    
    #GET:
    Return list of bonds belonging to syndicate with primary specified in URL. Logged in user must belong to the syndicate.


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
        user=request.user
        
        if 'amount' in content.keys() and 'kind' in content.keys():
            amount = content['amount']
            if content['kind']=='BUY':
                success = syndicate.buyBonds(user,amount)
                if not success:
                    return Response({'response':'failure'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'response':'success'},status=status.HTTP_200_OK)
            elif content['kind']=='SELL':
                success = syndicate.sellBonds(user,amount)
                if not success:
                    return Response({'response':'failure'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'response':'success'},status=status.HTTP_200_OK)
            else:
                return Response({'response':'failure'},status=status.HTTP_400_BAD_REQUEST)
