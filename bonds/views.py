from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from models import *
from .forms import *
from django.db.models import Sum
# Create your views here.


def index(request):
    if request.user.is_authenticated():
        profile = request.user.userprofile
        syndicates = profile.syndicate_set.all()
        context = {'profile': profile, 'syndicates': syndicates}
        return render(request, 'bonds/index.html', context)
    else:
        return render(request, 'bonds/index.html')


def syndicateManage(request, syn_id):
    syndicate = get_object_or_404(Syndicate, pk=syn_id)
    userprofile = request.user.userprofile
    if request.method == "POST":
        form = SyndicateForm(
            request.POST, instance=syndicate, userprofile=userprofile)
        if form.is_valid():
            form.save()
            return redirect('syndicateView', syn_id=syndicate.pk)
    else:
        form = SyndicateForm(instance=syndicate, userprofile=userprofile)
    endpoint = ''
    return render(request, 'bonds/create_manage_syndicate.html',
                  {'manage': True,
                   'endpoint': endpoint,
                   'form': form})


def syndicateNew(request):
    userprofile = request.user.userprofile
    if request.method == "POST":
        form = SyndicateForm(request.POST, userprofile=userprofile)
        if form.is_valid():
            new_syn = form.save(commit=False)
            new_syn.winnings = 0
            new_syn.owner = request.user
            new_syn.save()
            form.save_m2m()
            new_syn.members.add(userprofile)
            return redirect('syndicateView', syn_id=new_syn.pk)
    else:
        form = SyndicateForm(userprofile=userprofile)
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
            group_owner=syndicate_to_delete, user_owner=member.user, live=True)
        balance = live_user_bonds.count()
        member.balance += balance
        for bond in live_user_bonds:
            bond.live = False
            bond.save()
        member.save()
    syndicate_to_delete.delete()
    return redirect('index')
    
    
def syndicateView(request, syn_id):
    if request.user.is_authenticated():
        user = request.user
        userprofile = user.userprofile
        user_syndicates = userprofile.syndicate_set.all()
        syndicate = get_object_or_404(Syndicate, pk=syn_id)
        syn_users = syndicate.members.all()
        if syndicate in user_syndicates:
            groupbonds = PremiumBond.objects.filter(group_owner=syndicate)
            userbonds = groupbonds.filter(user_owner=user)
            groupwinnings = groupbonds.aggregate(Sum('winnings'))
            groupinvested = groupbonds.filter(live=True).count()
            userwinnings = UserSyndicateWinnings.objects.filter(
                user=user).filter(
                    syndicate=syndicate).aggregate(Sum('winnings'))
            userinvested = userbonds.filter(live=True).count()
            bonds_per_user = [{
                'name':
                member.user.first_name,
                'investment':
                groupbonds.filter(user_owner=member.user).count()
            } for member in syn_users]
            return render(request, 'bonds/view_syndicate.html', {
                'syndicate':
                syndicate,
                'user_profile':
                userprofile,
                'user_invested':
                userinvested,
                'user_winnings':
                userwinnings.get('winnings_sum', 0),
                'group_invested':
                groupinvested,
                'group_winnings':
                groupwinnings.get('winnings_sum', 0),
                'group_members':
                syn_users,
                'bonds_per_user':
                bonds_per_user,
            })
        else:
            return redirect('index')
    else:
        return redirect('index')


def invest(request, syn_id):
    if request.method == "POST":
        user = request.user
        syndicate = get_object_or_404(Syndicate, pk=syn_id)
        amount = int(request.POST.get("amount", 0))
        if syndicate in user.userprofile.syndicate_set.all():
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
