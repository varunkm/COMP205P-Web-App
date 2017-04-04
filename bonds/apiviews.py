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
        possible_user_keys=['username','password','email','first_name','last_name']
        possible_userprofile_keys=['language','security_question','answer']
        
        user = request.user
        change_content = request.data

        for key in change_content.keys():
            if key in possible_user_keys:
                setattr(user,key,change_content[key])
            elif key in possible_userprofile_keys:
                setattr(user.userprofile,key,change_content[key])
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


class ProductInfoList(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self,request,format=None):
        info = ProductInfo.objects.all()
        serializer=AcctTypeSerializer(info,many=True,context={'request':request})
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

class AccountWithdrawal(APIView):
    """
    #POST
    Post to this endpoint to create a withdrawal transaction against the account with pk specified in URL. Amount should be specified in JSON data: `{"amount":500}`
    """

    def post(self,request,pk,format=None):
        content = request.data
        account = get_object_or_404(Account,pk=pk)
        if account.owner != request.user:
            return HttpResponseForbidden()

        if 'amount' in content.keys():
            amt = content['amount']
            if amt > 0 and account.balance >= amt:
                account.balance -= amt
                account.save()
                transaction = Transaction(account=account,amount=amt,kind="WITHDRAWAL")
                transaction.save()
                return Response({"response":"withdrew","amount":amt},status=status.HTTP_200_OK)
            else:
                return Response({"response":"insufficient funds to complete transaction"},status=status.HTTP_409_CONFLICT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
class AccountDeposit(APIView):
    """
    #POST
    Post to this endpoint to create a deposit transaction against the account with pk specified in URL. Amount should be specified in JSON data: `{"amount":500}`
    """

    def post(self,request,pk,format=None):
        content = request.data
        account = get_object_or_404(Account,pk=pk)
        if account.owner != request.user:
            return HttpResponseForbidden()

        if 'amount' in content.keys():
            amt = content['amount']
            if amt > 0:
                account.balance += amt
                account.save()
                transaction = Transaction(account=account,amount=amt,kind="WITHDRAWAL")
                transaction.save()
                return Response({"response":"deposited","amount":amt},status=status.HTTP_200_OK)
            else:
                return Response({"response":"cannot deposit negative amount"},status=status.HTTP_409_CONFLICT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class AccountTransfer(APIView):
    """
    #POST
    Transfer amount specified in JSON from account specified in URL to recipient account specified in JSON.
    Expecting: `{"amount":500,"destination":<pk of destination account>}`
    """
    def post(self,request,pk,format=None):
        account = get_object_or_404(Account,pk=pk)
        content = request.data
        if not("amount" in content.keys() and "destination" in content.keys()):
            return Response(status.status.HTTP_400_BAD_REQUEST)
        destination_pk = content['destination']
        amt = content['amount']
        destination_acct = get_object_or_404(Account,pk=destination_pk)
        if not (account.owner==request.user and destination_acct.owner==request.user):
            return HttpResponseForbidden()
        if amt > 0 and amt <= account.balance:
            #transfer the money
            account.balance-=amt
            destination_acct.balance+=amt
            account.save()
            destination_acct.save()
            #create the transactions
            out_transaction = Transaction(account=account,amount=amt,kind="OUTGOING TRANSFER")
            in_transaction  = Transaction(account=destination_acct,amount=amt,kind="INCOMING TRANSFER")
            out_transaction.save()
            in_transaction.save()
            return Response({"response":"transfer successful"},status=status.HTTP_200_OK)
        
class AccountTransactions(APIView):
    """
    #GET
    Get a list of all transactions that have occurred within one account
    """
    def get(self,request,pk,format=None):
        account = get_object_or_404(Account,pk=pk)
        if request.user != account.owner:
            return HttpResponseForbidden()
        transactions = Transaction.objects.filter(account=account)
        serializer = TransactionSerializer(transactions,many=True,context={'request':request})
        return Response(serializer.data)

class UserTransactions(APIView):
    """
    #GET
    Get a list of all of the logged in users' transactions 
    """
    def get(self,request,format=None):
        transactions = Transaction.objects.filter(account__owner__exact=request.user)
        serializer = TransactionSerializer(transactions,many=True,context={'request':request})
        return Response(serializer.data)
    
class BondsList(APIView):
    """
    #POST:
    Buy a number of bonds on behalf of logged in user within the syndicate specified in URL. Expects JSON object specifiying amount. e.g. : 

    `{"amount":5}`
    
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
    
class APIRoot(APIView):
    renderer_classes = (StaticHTMLRenderer,)
    def get(self,request):
        return Response(
            "<h1>API ROOT</h1>"+
            "<h3>user detail by username : <a href='"+str(reverse("user-detail",kwargs={'username':'varunmathur'},request=request))+"'>"+str(reverse("user-detail",kwargs={'username':'varunmathur'},request=request))+"</a></h3>"+
            "<h3>logged in user update/view : <a href='"+str(reverse("user-view-and-modify",request=request))+"'>"+str(reverse("user-view-and-modify",request=request))+"</a></h3>"+
            "<h3>user create : <a href='"+str(reverse("user-create",request=request))+"'>"+str(reverse("user-create",request=request))+"</a></h3>"+
            "<h3>syndicate list : <a href='"+str(reverse("syndicate-list",request=request))+"'>"+str(reverse("syndicate-list",request=request))+"</a></h3>"+
            "<h3>syndicate detail : <a href='"+str(reverse("syndicate-detail",kwargs={'pk':2},request=request))+"'>"+str(reverse("syndicate-detail",kwargs={'pk':2},request=request))+"</a></h3>"+
            "<h3>syndicate bonds : <a href='"+str(reverse("bonds-list",kwargs={'syndicate_pk':1},request=request))+"'>"+str(reverse("bonds-list",kwargs={'syndicate_pk':1},request=request))+"</a></h3>"+
            "<h3>account list : <a href='"+str(reverse("account-list",request=request))+"'>"+str(reverse("account-list",request=request))+"</a></h3>"+
            "<h3>account detail : <a href='"+str(reverse("account-detail",kwargs={"pk":1},request=request))+"'>"+str(reverse("account-detail",kwargs={"pk":1},request=request))+"</a></h3>"+
            "<h3>account withdrawal : <a href='"+str(reverse("account-withdrawal",kwargs={"pk":1},request=request))+"'>"+str(reverse("account-withdrawal",kwargs={"pk":1},request=request))+"</a></h3>"+
            "<h3>account deposit : <a href='"+str(reverse("account-deposit",kwargs={"pk":1},request=request))+"'>"+str(reverse("account-deposit",kwargs={"pk":1},request=request))+"</a></h3>"+
            "<h3>account transfer : <a href='"+str(reverse("account-transfer",kwargs={"pk":1},request=request))+"'>"+str(reverse("account-transfer",kwargs={"pk":1},request=request))+"</a></h3>"+
            "<h3>account transactions : <a href='"+str(reverse("account-transactions",kwargs={"pk":1},request=request))+"'>"+str(reverse("account-transactions",kwargs={"pk":1},request=request))+"</a></h3>"+
            "<h3>user transactions : <a href='"+str(reverse("user-transactions",request=request))+"'>"+str(reverse("user-transactions",request=request))+"</a></h3>"+
            "<h3>product info list : <a href='"+str(reverse("product-list",request=request))+"'>"+str(reverse("product-list",request=request))+"</a></h3>"
            )
    
