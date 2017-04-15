import logging
import datetime
import random

import os

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'syndicate.settings'
application = get_wsgi_application()

from bonds.models import *

def main():
    print("Running end of day process...")
    applyInterest()
    processPremiumBonds()
    
def applyInterest():
    print('applying interest...')
    for account in Account.objects.all():
        if account.eligibleForPayout():
            amount = account.payout()
            account.save()
            credit = Transaction(account=account,amount=amount,kind="INTEREST CREDIT")
            credit.save()

def rewardGroupOwned(bond,amount):
    bond.winnings+=amount
    syndicate = bond.group_owner
    syndicate_members= syndicate.members
    current_shares = syndicate.getSharesAsFractions()
    syndicate.winnings+=amount
    for (user,share) in current_shares:
        user.userprofile.balance+=amount*share
        user.userprofile.winnings+=amount*share
        user_syndicate_win = UserSyndicateWinnings.objects.filter(user=user,syndicate=syndicate)[0]
        user_syndicate_win.winnings +=amount*share
        user_syndicate_win.save()
        user.userprofile.save()
    syndicate.save()
    bond.save()
        
def rewardSoleOwned(bond, amount):
    user = bond.user_owner
    bond.winnings+=amount
    user.userprofile.balance+=amount
    user.userprofile.save()
    bond.save()
        
def pickReward():
    TOTAL_RESOLUTION = 2224513
    REWARDS_PROB ={
        25:2076942,
        50:2147892,
        100:2218842,
        500:2223012,
        1000:2224402,
        5000:2224460,
        10000:2224491,
        25000:2224502,
        50000:2224508,
        100000:2224511
    }
    NUMBER_CHOSEN = random.randint(1,TOTAL_RESOLUTION)
    print(NUMBER_CHOSEN)
    for reward in sorted(REWARDS_PROB.keys()):
        if NUMBER_CHOSEN <= REWARDS_PROB[reward]:
            return reward
    return 1000000

def processPremiumBonds():
    new_draw = PrizeDraw()
    new_draw.save()
    bond_rewards = BondReward(total_payout=0,winning_number=0)
    
    print('processing premium bond rewards...')
    WINNING_CHANCE = 30000
    all_bonds = PremiumBond.objects.filter(live=True)
    winning_number = random.randint(1,WINNING_CHANCE)
    print(str(winning_number))

    bond_rewards.winning_number=winning_number
    bond_rewards.save()
    for bond in all_bonds:
        if bond.pk % WINNING_CHANCE == winning_number:
            print('bond ['+str(bond.pk)+'] has won')
            bond_rewards.winning_bonds.add(bond)
            #bond has won
            reward = pickReward()
            bond_rewards.total_payout+=reward
            print('reward: '+str(reward))
            if bond.group_owned:
                rewardGroupOwned(bond,reward)
            else:
                rewardSoleOwned(bond,reward)
            bond_rewards.save()

if __name__ == '__main__':    
    main()
        
        
