import random
import math


#return the profit or loss of the group for this simulation
def simulate_1_round(number_of_players,
                   number_of_groups,
                   group_size,
                   house_mean,
                   house_variance,
                   buy_price,
                   sell_price):
    usages=[random.normalvariate(house_mean,house_variance) for i in range(number_of_players)]
    coordinated_usage=sum(usages)
    groups_usage=[]
    coordinated_profit=0
    groups_profit=0
    if coordinated_usage>0:
        coordinated_profit=-coordinated_usage*buy_price
    else:
        coordinated_profit=coordinated_usage*sell_price

    for i in range(number_of_groups):
        groups_usage.append(sum(usages[i*group_size:(i+1)*group_size]))
        if groups_usage[i]>0:
            groups_profit=groups_profit-(groups_usage[i]*buy_price)
        else:
            groups_profit=groups_profit+(groups_usage[i]*sell_price)
    return coordinated_profit, groups_profit

PEG_buy_price=20
PEG_sell_price=5
num_players=100
number_sims_per_group=25
number_of_rounds=365
groups=[2,4,10,20,50]

# simulate each house's net usage as a normally
# distributed random variable 
net_usage_mean=0 
net_usage_variance=5

total_coordinated_profit=0
total_groups_profit=0
print(num_players," players")
for i in groups:
    total_coordinated_profit=0
    total_groups_profit=0
    group_sizes=int(num_players/i)
    for j in range(number_sims_per_group):
        for k in range(number_of_rounds):
            temp_coord_profit, temp_groups_profit=simulate_1_round(num_players, i,group_sizes, net_usage_mean,net_usage_variance,PEG_buy_price, PEG_sell_price)
            total_coordinated_profit=total_coordinated_profit+temp_coord_profit
            total_groups_profit=total_groups_profit+temp_groups_profit
    print("All coordinated:", total_coordinated_profit/number_sims_per_group," ",i ," groups:", total_groups_profit/number_sims_per_group)
