from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from models import *
from .forms import *
from django.db.models import Sum
# Create your views here.


def index(request):
    if request.user.is_authenticated():
        user = request.user
        syndicates = user.syndicate_set.all()
        context = {'profile': user.userprofile, 'syndicates': syndicates}
        return render(request, 'bonds/index.html', context)
    else:
        return render(request, 'bonds/index.html')


def syndicateManage(request, syn_id):
    syndicate = get_object_or_404(Syndicate, pk=syn_id)
    user = request.user
    if request.method == "POST":
        form = SyndicateForm(
            data=request.POST, instance=syndicate, user=user)
        if form.is_valid():
            form.save()
            syndicate.members.add(user)
            return redirect('syndicateView', syn_id=syndicate.pk)
    else:
        form = SyndicateForm(instance=syndicate, user=user)
    endpoint = ''
    return render(request, 'bonds/create_manage_syndicate.html',
                  {'manage': True,
                   'endpoint': endpoint,
                   'form': form})


def UserView(request,user_id):
    user = get_object_or_404(User,pk=user_id)
    if request.user==user:
        return redirect('profile')
    #shared_syndicates = Syndicate.objects.filter
    return render(request,'bonds/userview.html',
                  {'user':user})

def syndicateNew(request):
    user = request.user
    if request.method == "POST":
        form = SyndicateForm(request.POST, user=user)
        if form.is_valid():
            new_syn = form.save(commit=False)
            new_syn.winnings = 0
            new_syn.owner = request.user
            new_syn.save()
            form.save_m2m()
            new_syn.members.add(user)
            return redirect('syndicateView', syn_id=new_syn.pk)
    else:
        form = SyndicateForm(user=user)
    endpoint = ''
    return render(request, 'bonds/create_manage_syndicate.html',
                  {'manage': False,
                   'endpoint': endpoint,
                   'form': form})

# on syndicate deletion, first we must check that request comes from
# owner. Then we delete the syndicate and credit each users balance with
# their current stake in the group
def syndicateDelete(request, syn_id):
    syndicate_to_delete = get_object_or_404(Syndicate, pk=syn_id)
    request_user = request.user
    if request_user != syndicate_to_delete.owner:
        return redirect('index')
    syndicate_members = syndicate_to_delete.members.all()

    for member in syndicate_members:
        # get all live bonds belonging to member in this group
        live_user_bonds = PremiumBond.objects.filter(
            group_owner=syndicate_to_delete, user_owner=member, live=True)
        balance = live_user_bonds.count()
        member.userprofile.balance += balance
        for bond in live_user_bonds:
            bond.live = False
            bond.save()
        member.userprofile.save()
        member.save()
    syndicate_to_delete.delete()
    return redirect('index')
    
    
def syndicateView(request, syn_id):
    if request.user.is_authenticated():
        user = request.user
        userprofile = user.userprofile
        user_syndicates = user.syndicate_set.all()
        syndicate = get_object_or_404(Syndicate, pk=syn_id)
        syn_users = syndicate.members.all()
        if syndicate in user_syndicates:
            groupbonds = PremiumBond.objects.filter(group_owner=syndicate)
            userbonds = groupbonds.filter(user_owner=user)
            groupwinnings = syndicate.winnings
            groupinvested = groupbonds.filter(live=True).count()
            user_syn_win = UserSyndicateWinnings.objects.filter(user=user, syndicate=syndicate)
            userwinnings=0
            if len(user_syn_win) == 0:
                new_user_syn_win = UserSyndicateWinnings(user=user,syndicate=syndicate,winnings=0)
                new_user_syn_win.save()
                userwinnings = 0
            else:
                userwinnings = UserSyndicateWinnings.objects.filter(user=user, syndicate=syndicate)[0].winnings
            userinvested = userbonds.filter(live=True).count()
            bonds_per_user = syndicate.getSharesAsMoney()
            user_shares    = syndicate.getSharesAsFractions()

            chat_messages = ChatMessage.objects.filter(syndicate=syndicate)
            return render(request, 'bonds/view_syndicate.html', {
                'syndicate':
                syndicate,
                'members':
                syndicate.members.all(),
                'user_profile':
                userprofile,
                'user_invested':
                userinvested,
                'user_winnings':
                userwinnings,
                'group_invested':
                groupinvested,
                'group_winnings':
                groupwinnings,
                'group_members':
                syn_users,
                'bonds_per_user':
                bonds_per_user,
                'user_shares':
                user_shares,
                'chat_messages':
                chat_messages,
            })
        else:
            return redirect('index')
    else:
        return redirect('index')
def newMessage(request,syn_id):
    if request.method=="POST":
        user = request.user
        syndicate = get_object_or_404(Syndicate, pk=syn_id)
        message = str(request.POST.get("messagetext",""))
        if user.is_authenticated() and syndicate in user.syndicate_set.all():
            message = ChatMessage(syndicate=syndicate,writer=user,message=message)
            message.save()
            return redirect('syndicateView',syn_id=syn_id)
    return redirect('index')
            

def invest(request, syn_id):
    if request.method == "POST":
        user = request.user
        syndicate = get_object_or_404(Syndicate, pk=syn_id)
        amount = int(request.POST.get("amount", 0))
        if syndicate in user.syndicate_set.all():
            # if user belongs to the syndicate
            if user.userprofile.balance > amount:
                for i in range(amount):  # create "amount" premium bonds
                    x = PremiumBond(
                        live=True,
                        user_owner=user,
                        group_owner=syndicate,
                        winnings=0)
                    x.save()
                user.userprofile.balance -= amount
                user.userprofile.save()
        return redirect('syndicateView', syn_id=syn_id)
    return redirect('syndicateView', syn_id=syn_id)

def register(request):
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        upf = UserProfileForm(request.POST, prefix='userprofile')
        if uf.is_valid() * upf.is_valid():
            user_data = uf.cleaned_data
            user = User(username=user_data['username'],first_name=user_data['first_name'],last_name=user_data['last_name'],email=user_data['email'])
            user.set_password(user_data['password'])
            user.save()
            userprofile = upf.save(commit=False)
            userprofile.user = user
            userprofile.save()
            return redirect('index')
    else:
        uf = UserForm(prefix='user')
        upf = UserProfileForm(prefix='userprofile')
    return render(request,'registration/register.html',{'userform':uf,'userprofileform':upf})
