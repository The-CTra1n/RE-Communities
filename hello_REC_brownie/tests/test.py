import pytest
from brownie import Wei, reverts, chain, accounts

import math
from Utils.paillier import *



def test_token_swap(accounts,Paillier, System):
    initial_supply = 100000000
    n_length=128
    priv, pub = generate_keypair(n_length)
    n,g,l,mu=get_Paillier_params(priv,pub)
    print(n,g,l,mu)
    while True:
        r = primes.generate_prime(round(math.log(n, 2)))
        if r > 0 and r < n:
            break
    print(paillier_decrypt(paillier_encrypt(12345,r,n,g),n,l,mu))
    
    print(decrypt(priv,pub,encrypt(pub,12345)))
    auctioneer=accounts[0]

    accounts[0].transfer(accounts[1], "10 ether", gas_price=0)

    

    enc_scheme=auctioneer.deploy(Paillier,n,g)
    
    re_system = auctioneer.deploy(System,auctioneer,enc_scheme)

    re_system.addPlayer(accounts[1], enc_scheme, {"from":accounts[1]})

def get_Paillier_params(priv, pub):
    n=pub.n
    g=pub.g
    l=priv.l
    mu=priv.m
    return n,g,l,mu

def paillier_encrypt(plaintext, randomness, n, g):
    return ((pow(g,plaintext, n**2)*pow(randomness, n, n**2)))%(n**2)

def paillier_decrypt(ciphertext, n, l, mu):
    x=pow(ciphertext,l,n**2)-1
    plain=((x // n) * mu) % n
    return plain
