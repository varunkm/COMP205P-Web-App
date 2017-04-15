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

class ProductInfoList(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self,request,format=None):
        info = ProductInfo.objects.all()
        serializer=AcctTypeSerializer(info,many=True,context={'request':request})
        return Response(serializer.data)
    
class AccountList(APIView):
    """
    #POST
    Post to this endpoint to create a new user account
    Expects product info key. i.e. {"product":1} 
    
    #GET
    Return a list of the logged in user's accounts
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request,format=None):
        accounts = request.user.account_set.all()
        acctserializer = AccountSerializer(accounts,many=True,context={'request':request})

        syndicates = request.user.syndicate_set.all()
        synserializer = SyndicateAsAcctSerializer(syndicates,many=True,context={'request':request})

        user = request.user
        pbserializer = UserPremiumBondsAsAcctSerializer(user,context={'request':request})
        return Response(acctserializer.data+[pbserializer.data]+synserializer.data)
    
    def post(self,request,format=None):
        user = request.user
        content = request.data
        if 'product' in content.keys():
            info = get_object_or_404(ProductInfo,pk=content['product'])
            new_acct = Account(owner=user,info=info,balance=0.00)
            new_acct.save()
            return Response({'response':'success','new_acct_id':new_acct.pk},status=status.HTTP_200_OK)
        return Response({'response':'failure'},status=status.HTTP_400_BAD_REQUEST)

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
                transaction = Transaction(account=account,amount=amt,kind="DEPOSIT")
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

 
class APIRoot(APIView):
    renderer_classes = (StaticHTMLRenderer,)
    def genAPIRow(self,text,link):
        string = ''
        string+='<h3>'
        string+=text
        string+=' : <a href="'
        string+=link
        string+='">'
        string+=link
        string+='</a></h3>'
        return string
    def header(self,text):
        return '<h2>'+text+'</h2>'

    def br(self):
        return '<br>'
    
    def get(self,request):
        return Response(
            "<h1>API ROOT</h1>"+
            self.header('User Queries')+
            self.genAPIRow("user detail by username",str(reverse("user-detail",kwargs={'username':'varunmathur'},request=request)))+
            self.genAPIRow("logged in user update/view",str(reverse("user-view-and-modify",request=request)))+
            self.genAPIRow("user create",str(reverse("user-create",request=request)))+
            self.genAPIRow("user self owned bonds",str(reverse("user-bonds",request=request)))+
            self.genAPIRow("user have i won?",str(reverse("user-haveiwon",request=request)))+
            self.br()+self.header('Syndicate Queries')+
            self.genAPIRow("syndicate list",str(reverse("syndicate-list",request=request)))+
            self.genAPIRow("syndicate detail",str(reverse("syndicate-detail",kwargs={'pk':2},request=request)))+
            self.genAPIRow("syndicate bonds",str(reverse("bonds-list",kwargs={'syndicate_pk':1},request=request)))+
            self.genAPIRow("syndicate remove user",str(reverse("remove-user",kwargs={'syndicate_pk':1},request=request)))+
            self.genAPIRow("syndicate add user",str(reverse("add-user",kwargs={'syndicate_pk':1},request=request)))+
            self.genAPIRow("syndicate have i won?",str(reverse("syndicate-haveiwon",kwargs={'syndicate_pk':1},request=request)))+
            self.br()+self.header('Account Queries')+
            self.genAPIRow("account list",str(reverse("account-list",request=request)))+
            self.genAPIRow("account detail",str(reverse("account-detail",kwargs={"pk":1},request=request)))+
            self.genAPIRow("account withdrawal",str(reverse("account-withdrawal",kwargs={"pk":1},request=request)))+
            self.genAPIRow("account deposit",str(reverse("account-deposit",kwargs={"pk":1},request=request)))+
            self.genAPIRow("account transfer",str(reverse("account-transfer",kwargs={"pk":1},request=request)))+
            self.genAPIRow("account transactions",str(reverse("account-transactions",kwargs={"pk":1},request=request)))+
            self.genAPIRow("user transactions",str(reverse("user-transactions",request=request)))+
            self.genAPIRow("product info list",str(reverse("product-list",request=request)))
            )
    
