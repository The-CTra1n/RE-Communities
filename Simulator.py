
import pandas as pd
import math
import random
import matplotlib.pyplot as plt

number_of_houses=5
#this likely depends on number of batteries
max_storage_per_house=[100 for i in range(0,number_of_houses)]
#track local storage of each house
current_household_storage=[0 for i in range(0,number_of_houses)]
# baseline usages of each house
base_energy_usages=[5,6,7,8,9]
#basic peak usage adjustment
peak_usage_add_on=[5,4,3,2,1]
peak_hours=[6,7,8,17,18,19]


#the prices to buy energy locally and from the grid
energy_price_buy_local=1
energy_price_buy_Mains=10

#the amount of energy lost from storage per time unit
energy_decay=0.1

#the amount of energy lost transporting energy from house to local storage
efficiency_coeeficient=0.1

#central energy capacity
central_energy_capacity=250
#central energy contributions per household
central_energy_contributions=[0 for i in range(0,number_of_houses)]


def simulate():
    number_of_days=30
    time_slots_per_day=24

    for t in range(0, number_of_days*time_slots_per_day):
        for house in range(0,number_of_houses):
            usage=get_usage(house, t)

def get_usage(house_number, time):
    hour=time%24
    usage=base_energy_usages[house_number]
    if hour in peak_hours:
        return usage+peak_usage_add_on[house_number]
    return usage


#simulate a house for a particular time period
def house(house_number, production,usage, tokens):
    net_usage=usage-production

    #usage is greater than production for this time period
    if net_usage>0:

        #need to buy energy
        if net_usage>current_household_storage[house_number]:
            tokens-=market_buy(net_usage,house_number)
            current_household_storage[house_number]=0
        
        #house has enough energy
        else:
            current_household_storage[house_number]-=net_usage
    
    #house is net producer for this time period
    else:
        available_central_capacity=central_energy_capacity-sum(central_energy_contributions)
        # there is capacity to add to central storage 
        if available_central_capacity>0:
            contribution_amount=min(-net_usage,available_central_capacity)
        #add contribution amount to central storage
        market_sell(contribution_amount, house_number)
        #add remaining energy to house storage
        current_household_storage[house_number]=min(current_household_storage[house_number]+(-net_usage-contribution_amount),max_storage_per_house[house_number])


#the market buy and sell prices will depend on several factors
#1. where is the energy coming from
#2. current demand(time of day?)/supply(stored energy, etc.)
#3. House_specific discounts/fees

def market_buy(energy_to_buy,house_number):
    #stores the total community storage 
    local_storage_total=sum(central_energy_contributions)
    #the pct of local storage to be bought, initialize to 1 
    pct_to_buy=1
    #the token cost of the energy
    cost=0

    #if the house has existing contributions, receive this quantity for free
    if energy_to_buy>central_energy_contributions[house_number]:
        energy_to_buy-=central_energy_contributions[house_number]
        central_energy_contributions[house_number]=0
    #this means the house has more existing contributions than energy to buy
    # return energy at 0 cost
    else:
        central_energy_contributions[house_number]-=energy_to_buy
        return 0
    #not enough local energy
    # house needs to buy from mains
    if energy_to_buy>local_storage_total:
        #add the cost of buying the additional energy from mains
        cost+=(energy_to_buy-local_storage_total)*energy_price_buy_Mains
        energy_to_buy-=local_storage_total
    else:
        # if enough local energy, update the pct_to_buy
        pct_to_buy=energy_to_buy/local_storage_total
    
    # add the cost of buying local energy
    cost+=energy_to_buy*energy_price_buy_local
    #discount the contributions of each house to local storage
    for i in range(0,number_of_houses):
        central_energy_contributions[i]=central_energy_contributions[i]*(1-pct_to_buy)
    
    return cost

def market_sell(energy_to_sell, house_number):
    #add the energy to the local grid

    central_energy_contributions[house_number]+=(energy_to_sell*(1-efficiency_coeeficient))