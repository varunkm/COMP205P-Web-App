from django.contrib.auth.models import User
from models import *
from serializers import *
from django.http import Http404
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
            raise Http404
