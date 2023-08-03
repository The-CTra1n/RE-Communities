import pytest
from brownie import Wei, reverts, chain, accounts

from Crypto.Util import number
import math
from Utils.paillier import *



def test_token_swap(accounts,Paillier, System):
    initial_supply = 100000000
    n_length=16
    n,g,l,mu=get_Paillier_params(n_length)

    auctioneer=accounts[0]

    accounts[0].transfer(accounts[1], "10 ether", gas_price=0)

    

    enc_scheme=auctioneer.deploy(Paillier,n,g)
    
    re_system = auctioneer.deploy(System,auctioneer,enc_scheme)

    re_system.addPlayer(accounts[1], enc_scheme, {"from":accounts[1]})


def get_Paillier_params(n_length):
    priv, pub = generate_keypair(n_length)
    n=pub.n
    g=pub.g
    l=priv.l
    mu=priv.m
    return n,g,l,mu

def paillier_encrypt(plaintext, randomness, n, g):
    return ((pow(g,plaintext, n**2)*pow(randomness, n, n**2)))%(n**2)

def paillier_decrypt(ciphertext, n, l, mu):
    c=pow(ciphertext,l,n**2)
    L=((c-1)/n)-((c-1)%n)
    return((L*mu)%n)
