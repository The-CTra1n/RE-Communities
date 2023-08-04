
import math
from Utils.paillier import *



def test_token_swap(accounts,Paillier, System):
    initial_supply = 100000000
    n_length=64
    num_players=3
    player_keys=[]
    for i in range(0,num_players+1):
        # keys have form n, g, lambda, mu
        priv, pub=generate_keypair(n_length)
        print(priv, pub)
        player_keys.append(get_Paillier_params(priv,pub))
    print(player_keys)


    auctioneer=accounts[num_players]
    auctioneer_keys=player_keys[num_players]
    print(auctioneer_keys)


    enc_scheme=auctioneer.deploy(Paillier,auctioneer_keys["n"],auctioneer_keys["g"])
    re_system = auctioneer.deploy(System,auctioneer,enc_scheme)
    
    # add players to the system
    for i in range(num_players):
        enc_scheme=accounts[i].deploy(Paillier,player_keys[i]["n"],player_keys[i]["g"])
        re_system.addPlayer(accounts[i], enc_scheme, {"from":accounts[i]})

    #add encrypted usages for 1 time slot
    for i in range(num_players):
        usage=10000+i
        #ideally, we'd pull these from the blockchain
        n=auctioneer_keys["n"]
        g=auctioneer_keys["g"]
        randomness=generateEncryptionRandomness(n)
        encrypted_usage=paillier_encrypt(usage,randomness,n,g)
        enc_randomness=paillier_encrypt(randomness,generateEncryptionRandomness(n),n,g)
        re_system.userRevealNetUsage(0, encrypted_usage, enc_randomness, {"from":accounts[i]})

    # download encrypted usages for auctioneer to settle
    usages=[]
    randomnesses=[]
    for i in range(num_players):
        enc_usage=re_system.TS_net_usage_encrypted(0,accounts[i])
        enc_randomness=re_system.TS_encryption_randomness(0,accounts[i])
        n=auctioneer_keys["n"]
        l=auctioneer_keys["l"]
        mu=auctioneer_keys["mu"]
        usages.append(paillier_decrypt(enc_usage,n,l,mu))
        randomnesses.append(paillier_decrypt(enc_randomness,n,l,mu))
    print(usages,randomnesses)
    
    # reveal the net usage to the blockchain, without revealing
    # individual values
    randomness_product=1
    for i in range(0,num_players):
        randomness_product=(randomnesses[i]*randomness_product)%(n**2)
    price=2
    re_system.auctioneerRevealNetUsage(0,sum(usages),randomness_product,price)


    # updated the encrypted token amounts on chain
    


def get_Paillier_params(priv, pub):
    n=pub.n
    g=pub.g
    l=priv.l
    mu=priv.m
    return {'n':n,'g':g,'l':l,'mu':mu}

def paillier_encrypt(plaintext, randomness, n, g):
    return ((pow(g,plaintext, n**2)*pow(randomness, n, n**2)))%(n**2)

def paillier_decrypt(ciphertext, n, l, mu):
    x=pow(ciphertext,l,n**2)-1
    plain=((x // n) * mu) % n
    return plain

def generateEncryptionRandomness(n):
        r=0
        while True:
            r = primes.generate_prime(round(math.log(n, 2)))
            if r > 0 and r < n:
                break
        return r
