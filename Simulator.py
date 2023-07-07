import pandas as pd
import math
import random
import matplotlib.pyplot as plt

number_of_simulations=10

number_of_houses=5
number_of_days=365
time_slots_per_day=24
#BArcelona latitude
latitiude=41.22
#will be used to calculate strength of sun
max_daylight_hours=0

#hours in which peak usage occurs
peak_usage_hours=[6,7,8,17,18,19]
peak_usage_multiplier=3

# Solar power variables
# baseline production of each house
sunlight=[0 for i in range(0,time_slots_per_day)]
# the amount of watts produced per solar panel at maximum sun power
kilowatts_per_solar_panel=0.3

def simulate(cartel_of_neighbours,big_producers,big_producer_multiplier,big_consumers,big_consumer_multiplier, low_producers, low_producer_multiplier):
    #tokens per house
    tokens=[0 for i in range(0,number_of_houses+1)]

    #central energy contributions per household and central energy production, stored in the final slot
    central_energy_contributions=[0 for i in range(0,number_of_houses+1)]
    central_energy_capacity=250
    # ASK PORTUGESE
    # ASK PORTUGESE
    # ASK PORTUGESE
    #the amount of energy lost transporting energy from house to local storage
    # efficiency_coeeficient=0
    #the amount of energy lost from storage per time unit
    energy_decay_multiplier=0.01

    #pct of sun power converted to energy
    solar_panel_efficiency=0.9

    # in kWhs
    # #this depends on number of batteries
    # # set abritrarily, ask PORTUGESE
    house_max_storage=20
    current_household_storage=[0 for i in range(0,number_of_houses)]

    average_energy_usage_per_house=4000
    average_solar_panels_per_house=24
    #number of central solar panels, double the total solar panels in the system
    effective_central_solar_panels=average_solar_panels_per_house*number_of_houses*solar_panel_efficiency

    # wind turbine variables 
    # # rooftop turbines have an output of 400W to 1kW  
    # # $100,000 produces approx 14kW, according to link in shared doc
    # expected annual wind production matches expected usage of normal houses
    annual_central_wind_energy_production=number_of_houses*average_energy_usage_per_house
    average_hourly_central_wind_production=annual_central_wind_energy_production/(365*time_slots_per_day)

    #the prices to buy energy locally and from the grid
    energy_price_local=1
    energy_price_external_grid=5

    base_hourly_energy_usage, effective_solar_panels_per_house,max_storage_per_house=generate_houses_for_simulation(average_energy_usage_per_house, 
                                                                                                                    average_solar_panels_per_house,
                                                                                                                    solar_panel_efficiency,
                                                                                                                    house_max_storage,
                                                                                                                    big_producers,
                                                                                                                    big_producer_multiplier,
                                                                                                                    big_consumers,
                                                                                                                    big_consumer_multiplier, 
                                                                                                                    low_producers, 
                                                                                                                    low_producer_multiplier)
    print(effective_solar_panels_per_house)
    current_household_storage=[0 for i in range(0,number_of_houses)]
    #needed to ensure fair access to local storage
    priority_modifier=0
    for t in range(0, number_of_days*time_slots_per_day):
        priority_modifier=priority_modifier+1
        if t%time_slots_per_day==0:
            get_daylight_hours(1+(int(t/24)%365))
        central_energy_contributions=simulate_central_production(t,central_energy_capacity,central_energy_contributions,effective_central_solar_panels,average_hourly_central_wind_production)
        for house in range(0,number_of_houses):
            # rotate priority based on priority modifier
            adjusted_house=(house+priority_modifier)%number_of_houses
            usage=get_usage(adjusted_house, t,base_hourly_energy_usage)
            production=get_house_production(adjusted_house,t,effective_solar_panels_per_house)
            current_household_storage, tokens, central_energy_contributions,energy_price_local=house_simulation_1_time_unit(adjusted_house,production,usage,tokens,current_household_storage,central_energy_capacity,central_energy_contributions,energy_price_local,energy_price_external_grid,max_storage_per_house,cartel_of_neighbours)
        central_energy_contributions,current_household_storage=decay_storage(central_energy_contributions,current_household_storage,max_storage_per_house,energy_decay_multiplier,central_energy_capacity)

        
    print("tokens: ",tokens)
    print("Current storage:",current_household_storage )
    print("central storage contributions", central_energy_contributions )

    return

def generate_houses_for_simulation(average_energy_usage_per_house, 
                                    average_solar_panels_per_house,
                                    solar_panel_efficiency,
                                    house_max_storage,
                                    big_producers,
                                    big_producer_multiplier,
                                    big_consumers,
                                    big_consumer_multiplier, 
                                    low_producers, 
                                    low_producer_multiplier): 
    annual_energy_usages=[average_energy_usage_per_house for i in range(0,number_of_houses)]
    #off-peak hourly usages
    base_hourly_energy_usage=[i/(365*(24+(peak_usage_multiplier-1)*len(peak_usage_hours))) for i in annual_energy_usages]
    print(base_hourly_energy_usage)
    # number of panels times efficiency
    effective_solar_panels_per_house=[average_solar_panels_per_house*solar_panel_efficiency for i in range(0,number_of_houses)]
    max_storage_per_house=[house_max_storage for i in range(0,number_of_houses)]

    for i in big_producers:
        effective_solar_panels_per_house[i]=effective_solar_panels_per_house[i]*big_producer_multiplier
    #greedy houses are first in the list
    for i in big_consumers:
        annual_energy_usages[i]=annual_energy_usages[i]*big_consumer_multiplier
    #lazy houses are last in the list
    for i in low_producers:
        effective_solar_panels_per_house[number_of_houses-i]=low_producers[number_of_houses-i]*low_producer_multiplier
    return base_hourly_energy_usage, effective_solar_panels_per_house, max_storage_per_house

def decay_storage(central_energy_contributions,current_household_storage,max_storage_per_house,energy_decay_multiplier,central_energy_capacity):
    if sum(central_energy_contributions)>(central_energy_capacity*energy_decay_multiplier):
        pct_to_delete=(central_energy_capacity*energy_decay_multiplier)/sum(central_energy_contributions)
        for i in range(0,number_of_houses+1):
            central_energy_contributions[i]=central_energy_contributions[i]*(1-pct_to_delete)
    else:
        central_energy_contributions=[0 for i in range(0,number_of_houses+1)]

    current_household_storage=[max(current_household_storage[i]-(max_storage_per_house[i]*energy_decay_multiplier),0) for i in range(0,number_of_houses)]
    return central_energy_contributions, current_household_storage

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

def get_usage(house_number, time, base_hourly_energy_usage):
    hour=time%24
    usage=base_hourly_energy_usage[house_number]
    if hour in peak_usage_hours:
        return usage*peak_usage_multiplier
    return usage

def get_house_production(house_number, time, effective_solar_panels_per_house):
    hour=time%24
    production=0
    # add sunlight production
    production=sunlight[hour]*effective_solar_panels_per_house[house_number]*kilowatts_per_solar_panel
    return production

def simulate_central_production(time, central_energy_capacity,central_energy_contributions, effective_number_of_central_solar_panels, average_hourly_central_wind_production):
    hour=time%24
    production=0
    # add sunlight production
    production=production+sunlight[hour]*effective_number_of_central_solar_panels*kilowatts_per_solar_panel
    # add wind production
    production=production+average_hourly_central_wind_production
    available_central_capacity=central_energy_capacity-sum(central_energy_contributions)
    if available_central_capacity >0:
        central_energy_contributions[number_of_houses]=central_energy_contributions[number_of_houses]+min(production,available_central_capacity)
    # print(central_energy_contributions)
    return central_energy_contributions

#simulate a house for a particular time period
def house_simulation_1_time_unit(house_number,production,usage,tokens,current_household_storage,central_energy_capacity,central_energy_contributions,energy_price_local,energy_price_external_grid,max_storage_per_house,cartel_of_neighbours):
    net_usage=usage-production
    #usage is greater than production for this time period
    if net_usage>0:
        #need to buy energy
        if net_usage>current_household_storage[house_number]:
            net_usage=net_usage-current_household_storage[house_number]
            current_household_storage[house_number]=0
            if house_number in cartel_of_neighbours:
                for seller in cartel_of_neighbours:
                    if current_household_storage[seller]>0:
                        net_usage, tokens, current_household_storage=neighbour_buy(net_usage,house_number,i,tokens,energy_price_local,current_household_storage)
            

            tokens, central_energy_contributions, energy_price_local=market_buy(net_usage-current_household_storage[house_number],house_number,tokens, central_energy_contributions,energy_price_local,energy_price_external_grid)
            
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
            central_energy_contributions,energy_price_local=market_sell(contribution_amount, house_number, central_energy_contributions,energy_price_local)
        #add remaining energy to house storage
        current_household_storage[house_number]=min(current_household_storage[house_number]+(-net_usage-contribution_amount),max_storage_per_house[house_number])
    return current_household_storage, tokens, central_energy_contributions,energy_price_local

#the market buy and sell prices will depend on several factors
#1. where is the energy coming from
#2. current demand(time of day?)/supply(stored energy, etc.)
#3. House_specific discounts/fees

def market_buy(energy_to_buy,house_number,tokens, central_energy_contributions,energy_price_local,energy_price_external_grid):
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
    #not enough local energy
    # house needs to buy from mains
    if energy_to_buy>local_storage_total:
        #add the cost of buying the additional energy from mains
        cost+=(energy_to_buy-local_storage_total)*energy_price_external_grid
        energy_to_buy-=local_storage_total
    else:
        # if enough local energy, update the pct_to_buy
        pct_to_buy=energy_to_buy/local_storage_total
    
    # add the cost of buying local energy
    cost=cost+energy_to_buy*energy_price_local
    tokens[house_number]=tokens[house_number]-cost
    #discount the contributions of each house to local storage
    for i in range(0,number_of_houses+1):
        #pay houses who contributed to energy being bought
        tokens[house_number]+=central_energy_contributions[i]*pct_to_buy*energy_price_local
        #remove that energy from central supply
        central_energy_contributions[i]=central_energy_contributions[i]*(1-pct_to_buy)
    
    return tokens, central_energy_contributions, energy_price_local


#allows neighbours to buy from each other directly
def neighbour_buy(energy_to_buy,house_buying, house_selling,tokens, energy_price_local,current_household_storage):
    # buyer has more tokens than seller has in storage
    if energy_to_buy>current_household_storage[house_selling]:
        energy_to_buy=energy_to_buy-current_household_storage[house_selling]
        tokens[house_buying]=tokens[house_buying]-(current_household_storage[house_selling]*energy_price_local)
        tokens[house_selling]=tokens[house_selling]+(current_household_storage[house_selling]*energy_price_local)
        current_household_storage[house_selling]=0
        
    #seller has sufficient tokens
    else:
        current_household_storage[house_selling]=current_household_storage[house_selling]-energy_to_buy
        tokens[house_buying]=tokens[house_buying]-(energy_to_buy*energy_price_local)
        tokens[house_selling]=tokens[house_selling]+(energy_to_buy*energy_price_local)
        energy_to_buy=0
    return energy_to_buy, tokens, current_household_storage
    
def market_sell(energy_to_sell, house_number,central_energy_contributions,energy_price_local):
    #add the energy to the local grid
    #checks for contribution amount are done in house_simulation_1_time_unit() function
    central_energy_contributions[house_number]=central_energy_contributions[house_number]+(energy_to_sell)
    return central_energy_contributions, energy_price_local

max_daylight_hours=get_max_daylight_hours()

#specify a set of houses who agree to swap energy between them before selling to market
cartel_of_neighbours=[0,1]

# big producign houses
big_producers=[1]
big_producer_multiplier=2

# greedy houses
big_consumers=[]
big_consumer_multiplier=2

# lazy houses
low_producers=[]
low_producer_multiplier=1

for i in range(0,1):
    simulate(cartel_of_neighbours,big_producers,big_producer_multiplier,big_consumers,big_consumer_multiplier, low_producers, low_producer_multiplier) 

