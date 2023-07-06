
import pandas as pd
import math
import random
import matplotlib.pyplot as plt

number_of_houses=5
time_slots_per_day=24
#BArcelona latitude
latitiude=41.22
#will be used to calculate strength of sun
max_daylight_hours=0
#tokens per house
tokens=[1000 for i in range(0,number_of_houses)]

#this likely depends on number of batteries
max_storage_per_house=[100 for i in range(0,number_of_houses)]
#track local storage of each house
current_household_storage=[0 for i in range(0,number_of_houses)]
# total annual usages of each house in kWh
annual_energy_usages=[4000,4500,5000,6500,7000]

#hours in which peak usage occurs
peak_usage_hours=[6,7,8,17,18,19]
peak_usage_multiplier=3
base_hourly_energy_usage=[i/(365*(24+(peak_usage_multiplier-1)*len(peak_usage_hours))) for i in annual_energy_usages]
print("base energy usages", base_hourly_energy_usage)

# Solar power variables

# baseline production of each house
sunlight=[0 for i in range(0,time_slots_per_day)]
# the amount of watts produced per solar panel at maximum sun power
kilowatts_per_solar_panel=0.3

solar_panels_per_house=[12,12, 12, 15, 18]
#pct of sun power converted to energy
solar_panel_efficiency=0.9
# sense check, assuming avg of 6hrs sun per day
expected_annual_production=[solar_panel_efficiency*solar_panels_per_house[i]*kilowatts_per_solar_panel*6*365 for i in range(0,number_of_houses)]
print("sense check, annual production assuming avg of 6hrs sun per day",expected_annual_production)
print("annual consumption", annual_energy_usages)
#the prices to buy energy locally and from the grid
energy_price_buy_local=1
energy_price_buy_Mains=10

# ASK PORTUGESE
# ASK PORTUGESE
# ASK PORTUGESE
#the amount of energy lost from storage per time unit
energy_decay=0
#the amount of energy lost transporting energy from house to local storage
efficiency_coeeficient=0

#central energy capacity
central_energy_capacity=250
#central energy contributions per household
central_energy_contributions=[0 for i in range(0,number_of_houses)]


def simulate():
    number_of_days=365
    for t in range(0, number_of_days*time_slots_per_day):
        if t%time_slots_per_day==0:
            get_daylight_hours(1+(int(t/24)%365))
        for house in range(0,number_of_houses):
            usage=get_usage(house, t)
            production=get_production(house,t)
            house_simulation_1_time_unit(house,production,usage)
    return
    

def get_daylight_hours(day):
    y=math.radians(23.44*math.sin(math.radians(360*(day+284)/365)))
    x=-math.tan(math.radians(latitiude))*math.tan(y)
    daylight_hours=abs(2*(1/15)*math.degrees(math.acos(x)))
    #needs to be changed if we stop using hour slots
    for i in range(0,24):
        if i > 12-(daylight_hours/2) and i<12+(daylight_hours/2):
            sunlight[i]=math.sin(math.radians(90+180*(i-12)/daylight_hours))
        else:
            sunlight[i]=0
    #this function weakens the  sun strength
    discount_sun_strength(daylight_hours)
    #print(day, "sunlight hours",sum(sunlight))

def discount_sun_strength(daylight_hours):
    #this discount is based on time of year, are we happy with it?
    discount1=(daylight_hours/max_daylight_hours)
    #this discount is a weather based discount
    # 20% of the time, the production drops by 50%
    discount2=1
    if random.random()<0.2:
        discount2=0.5    
    for i in range(0,time_slots_per_day):
        sunlight[i]=sunlight[i]*discount1*discount2


def get_max_daylight_hours():
    day=172
    y=math.radians(23.44*math.sin(math.radians(360*(day+284)/365)))
    x=-math.tan(math.radians(latitiude))*math.tan(y)
    return abs(2*(1/15)*math.degrees(math.acos(x)))


def get_usage(house_number, time):
    hour=time%24
    usage=base_hourly_energy_usage[house_number]
    if hour in peak_usage_hours:
        return usage*peak_usage_multiplier
    return usage

def get_production(house_number, time):
    hour=time%24
    production=sunlight[hour]*solar_panel_efficiency*solar_panels_per_house[house_number]*kilowatts_per_solar_panel
    return production

#simulate a house for a particular time period
def house_simulation_1_time_unit(house_number,production,usage,):
    net_usage=usage-production
    #usage is greater than production for this time period
    if net_usage>0:
        #need to buy energy
        if net_usage>current_household_storage[house_number]:
            tokens[house_number]=tokens[house_number]-market_buy(net_usage,house_number)
            current_household_storage[house_number]=0
        #house has enough energy
        else:
            current_household_storage[house_number]-=net_usage
    #house is net producer for this time period
    else:
        available_central_capacity=central_energy_capacity-sum(central_energy_contributions)
        contribution_amount=0
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
        central_energy_contributions[house_number]=central_energy_contributions[house_number]-energy_to_buy
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
    cost=cost+energy_to_buy*energy_price_buy_local
    #discount the contributions of each house to local storage
    for i in range(0,number_of_houses):
        #pay houses who contributed to energy being bought
        tokens[house_number]+=central_energy_contributions[i]*pct_to_buy*energy_price_buy_local
        #remove that energy from central supply
        central_energy_contributions[i]=central_energy_contributions[i]*(1-pct_to_buy)
    
    return cost

def market_sell(energy_to_sell, house_number):
    #add the energy to the local grid
    central_energy_contributions[house_number]=central_energy_contributions[house_number]+(energy_to_sell*(1-efficiency_coeeficient))
    return

max_daylight_hours=get_max_daylight_hours()
simulate() 
print("tokens: ",tokens)
print("Current storage:",current_household_storage )
print( "central storage contributions", central_energy_contributions )
