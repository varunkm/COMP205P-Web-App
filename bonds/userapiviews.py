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


class UserDetail(APIView):
    """
####Return information about user with primary key specified in URL. Will return more detailed information about logged in user
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get_object(self,username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
    
    def get(self,request,username,format=None):
        user=self.get_object(username)
        if request.user == user:
            serializer = UserSerializer(user,context={'request':request})
            data = serializer.data
            return Response(data)
        else:
            serializer = UserShortSerializer(user,context={'request':request})
            return Response(serializer.data)


class UserViewModify(APIView):
    """    
    #PUT - Update user info
    Send a "PUT" request with whatever data you want to change about current logged in user 

    #GET - 
    If you run a GET request to this endpoint, it will return the details of the currently logged in user. (based on token)
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def put(self,request,format=None):
        possible_user_keys=['username','email','first_name','last_name']
        possible_userprofile_keys=['balance','language','security_question','answer']
        
        user = request.user
        change_content = request.data

        for key in change_content.keys():
            if key in possible_user_keys:
                setattr(user,key,change_content[key])
            elif key in possible_userprofile_keys:
                setattr(user.userprofile,key,change_content[key])

        if "password" in change_content.keys():
            if change_content['password']!='':
                user.set_password(change_content['password'])
        user.save()
        user.userprofile.save()
        return Response(status=status.HTTP_200_OK)                        
        
        
    def get(self,request):
        userdetailview = UserDetail()
        return userdetailview.get(request,request.user.username)

class UserCreate(APIView):
    """
    #POST - Create new user
    Expected keys: `"username","password","email","first_name","last_name","language","security_question","answer"`
    Post to this endpoint to create a new user.
    """
    def post(self,request,format=None):
        expected_keys=['username','password','email','first_name','last_name','language','security_question','answer']
        content = request.data
        if set(content.keys())!=set(expected_keys) or len(content.keys())!=len(expected_keys):
            return Response({'response':'failure','reason':'unexpected request content'},status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(content['username'],email=content['email'],password=content['password'])
        user.first_name=content['first_name']
        user.last_name=content['last_name']
        
        user.userprofile= UserProfile(language=content['language'],security_question=content['security_question'],answer=content['answer'])
        user.userprofile.save()
        user.save()
        token = Token.objects.get(user=user)
        return Response({"token":token.key})


class UserTransactions(APIView):
    """
    #GET
    Get a list of all of the logged in users' transactions 
    """
    
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request,format=None):
        transactions = Transaction.objects.filter(account__owner__exact=request.user)
        serializer = TransactionSerializer(transactions,many=True,context={'request':request})
        return Response(serializer.data)

class UserBonds(APIView):
    """
    #GET
    Get user's sole owned premium bond account
    
    #POST
    Buy or sell sole owned premium bonds
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self,request,format=None):
        user = request.user
        serializer = UserPremiumBondSerializer(user,context={'request':request})
        return Response(serializer.data)

    def post(self,request,format=None):
        user = request.user
        content = request.data
        up = user.userprofile
        
        if 'amount' in content.keys() and 'kind' in content.keys():
            amount = content['amount']
            if content['kind']=='BUY':
                success = up.buyBonds(amount)
                if not success:
                    return Response({'response':'failure'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'response':'success'},status=status.HTTP_200_OK)
            elif content['kind']=='SELL':
                success = up.sellBonds(amount)
                if not success:
                    return Response({'response':'failure'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'response':'success'},status=status.HTTP_200_OK)
            else:
                return Response({'response':'failure'},status=status.HTTP_400_BAD_REQUEST)

        
    
