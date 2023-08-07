
import math
from Utils.paillier import *



def test_system_run(accounts,Paillier, System):
    
    num_time_slots=5
    num_players=3

    # size of encryption field
    n_length=64
    
    player_keys=[]
    for i in range(0,num_players+1):
        # keys have form n, g, lambda, mu
        priv, pub=generate_keypair(n_length)
        player_keys.append(get_Paillier_params(priv,pub))

    auctioneer=accounts[num_players]
    auctioneer_keys=player_keys[num_players]

    # initialize on chain encryption scheme and system
    enc_scheme=auctioneer.deploy(Paillier,auctioneer_keys["n"],auctioneer_keys["g"])
    re_system = auctioneer.deploy(System,auctioneer,enc_scheme)
    
    # add players to the system
    # track the on-chain encryption of tokens
    # these arrays are only viewable by the users with respective decryption keys
    enc_token_randomness=[]
    net_token_amounts=[]

    for i in range(num_players):
        enc_scheme=accounts[i].deploy(Paillier,player_keys[i]["n"],player_keys[i]["g"])
        re_system.addPlayer(accounts[i], enc_scheme, {"from":accounts[i]})
        enc_token_randomness.append(1)
        net_token_amounts.append(0)

    for time_slot in range(0,num_time_slots):
        net_token_amounts,enc_token_randomness=one_system_round(time_slot,
                                                                    num_players,
                                                                    auctioneer_keys,
                     re_system,
                     accounts,
                     player_keys,
                     net_token_amounts,
                     enc_token_randomness)
        print("time slot:",time_slot,", net tokens:",net_token_amounts)
        print("randomness for net token encryption:",enc_token_randomness)


def one_system_round(time_slot,num_players,
                     auctioneer_keys,
                     re_system,
                     accounts,
                     player_keys,
                     net_token_amounts,
                     enc_token_randomness):
    
    usages=[100,5,-200]

    #add encrypted usages for 1 time slot
    for i in range(num_players):
        #ideally, we'd pull these from the blockchain
        n=auctioneer_keys["n"]
        g=auctioneer_keys["g"]
        # convert negative usages to positive numbers
        usage=usages[i]%(n)
        randomness=generateEncryptionRandomness(n)
        encrypted_usage=paillier_encrypt(usage,randomness,n,g)
        enc_randomness=paillier_encrypt(randomness,generateEncryptionRandomness(n),n,g)
        re_system.userRevealUsage(time_slot, encrypted_usage, enc_randomness, {"from":accounts[i]})

    # download encrypted usages for auctioneer to settle
    usages=[]
    randomnesses=[]
    for i in range(num_players):
        enc_usage=re_system.TS_net_usage_encrypted(time_slot,accounts[i])
        enc_randomness=re_system.TS_encryption_randomness(time_slot,accounts[i])
        n=auctioneer_keys["n"]
        l=auctioneer_keys["l"]
        mu=auctioneer_keys["mu"]
        # handle negative usages
        dec=paillier_decrypt(enc_usage,n,l,mu)
        if dec>n/2:
            dec=dec-n
        usages.append(dec)
        randomnesses.append(paillier_decrypt(enc_randomness,n,l,mu))

    # reveal the net usage to the blockchain, without revealing
    # individual values
    randomness_product=1
    for i in range(0,num_players):
        randomness_product=(randomnesses[i]*randomness_product)%(n**2)
    

    net_usage=sum(usages)%n
    settlement_price=0

    # the prices if the community must buy or sell to the PEG
    PEG_buy_price=20
    PEG_sell_price=5
    if net_usage>0:
        settlement_price=PEG_buy_price
    else:
        settlement_price=PEG_sell_price
    re_system.auctioneerRevealNetUsage(time_slot,net_usage,randomness_product,settlement_price)

    # to-do
    # updated the encrypted token amounts on chain

    token_encryptions=[]
    randomness_encryptions=[]
    settlement_randomness=1
    for i in range(0,num_players):
        r=0
        player_n=player_keys[i]["n"]
        player_g=player_keys[i]["g"]
        auctioneer_n=auctioneer_keys["n"]
        auctioneer_g=auctioneer_keys["g"]
        while True:
            r=generateEncryptionRandomness(n)
            if r<player_n:
                break
        
        settlement_randomness=(settlement_randomness*r)%auctioneer_n
        x=paillier_encrypt(r,generateEncryptionRandomness(player_n),player_n,player_g)
        randomness_encryptions.append(x)
        token_encryptions.append(paillier_encrypt((usages[i]*settlement_price)%n,r,auctioneer_n,auctioneer_g))
    
    # update net token usage, and the encrypted sum for each user
    #  
    re_system.auctioneerRevealSettlements(time_slot,settlement_randomness,randomness_encryptions,token_encryptions)


    # users verify token usages
    for i in range(num_players):
        new_enc_tokens=re_system.user_net_tokens_encrypted(accounts[i])
        enc_randomness=re_system.TS_token_randomness_encrypted(time_slot,accounts[i])
       
        # decrypt the randomness used to encrypt new token value
        dec_randomness=paillier_decrypt(enc_randomness,player_keys[i]["n"],player_keys[i]["l"],player_keys[i]["mu"])
        new_randomness=(dec_randomness*enc_token_randomness[i])%auctioneer_keys["n"]
        new_tokens=(net_token_amounts[i]+(usages[i]*settlement_price))%auctioneer_keys["n"]
        enc=paillier_encrypt(new_tokens,new_randomness,auctioneer_keys["n"], auctioneer_keys["g"])
        
        if enc==new_enc_tokens:
            enc_token_randomness[i]=new_randomness
            if(new_tokens>auctioneer_keys["n"]/2):
                net_token_amounts[i]=new_tokens-auctioneer_keys["n"]    
            else:
                net_token_amounts[i]=new_tokens
        else:
            # ideally this would trigger a user to contest the auctioneers on chain
            print("woops")
    return net_token_amounts,enc_token_randomness

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
