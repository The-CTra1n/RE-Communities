import pytest
from brownie import Wei, reverts, chain, accounts

def test_token_swap(accounts,Paillier, System):
    initial_supply = 100000000
    p=13
    q=17
    n=p*q
    g=4886
    l=48
    mu=159

    auctioneer=accounts[0]

    accounts[0].transfer(accounts[1], "10 ether", gas_price=0)
    # deploy the auction contract
    enc_scheme=auctioneer.deploy(Paillier,n,g,l,mu)
    re_system = auctioneer.deploy(System,auctioneer,enc_scheme)

    re_system.addPlayer(accounts[1], enc_scheme, {"from":accounts[1]})
    print(re_system.num_people())