pragma solidity ^0.8.0;

import {Paillier} from "contracts/Paillier.sol";

contract System {
    struct Player{
        address _address;
        Paillier _publicKey;
    }

    Player public auctioneer;
    uint public num_people;

    // a mapping of time slots to net usage for each user
    mapping(uint256 => mapping(address => uint256)) public TS_net_usage_encrypted;
    // these encryptions are of the randomness used in the net usage encryptions
    // are used to prove the auctioneer is well behaved
    // can probably be done with inverses 
    mapping(uint256 => mapping(address => uint256)) public TS_encryption_randomness;
    
    mapping(uint256 => uint256) public TS_net_usage_decrypted;
    mapping(uint256 => uint256) public settlement_price;
    
    Player[] public users;
    mapping (address => uint256) public user_net_tokens_encrypted;
    mapping (uint256 => mapping(address => uint256)) public TS_token_randomness_encrypted;

    // can we use an extra array for "greenness"?
    // might not be necessary


    constructor(address _auctioneer, Paillier _paillier) {
        auctioneer._address=_auctioneer;
        auctioneer._publicKey=_paillier;
        num_people=0;
    }

    function addPlayer(address _who, Paillier _key) public {
        Player memory newPlayer;
        newPlayer._address=_who;
        newPlayer._publicKey=_key;
        users.push(newPlayer);
        num_people++;
        user_net_tokens_encrypted[_who]=1;
    }

    function userRevealUsage(uint256 time_slot,uint256 encryptedUsage, uint256 encryptedRandomness) public {
        require(encryptedUsage>0, "0 values not allowed");
        TS_net_usage_encrypted[time_slot][msg.sender]=encryptedUsage;
        TS_encryption_randomness[time_slot][msg.sender]=encryptedRandomness;
    }


    // reveal checks depend on the encrypted ciphertexts being such that
    // the product of ciphertexts being the encryption of the sum of the plaintexts
    function auctioneerRevealNetUsage(uint256 time_slot, uint256 netUsage, uint256 usageRandomness, uint256 price) public {
        uint256 productOfCiphertexts=1;
        uint256 modulus=auctioneer._publicKey.n();
        for (uint i = 0; i < num_people; i++) {
            if (TS_net_usage_encrypted[time_slot][users[i]._address]>0){
                // this is because of the homomorphic property
                productOfCiphertexts=(productOfCiphertexts*TS_net_usage_encrypted[time_slot][users[i]._address])%(modulus**2);
            }
        }
        //may need to add the modulus to netUsage if it is negative
        require(auctioneer._publicKey.encrypt(netUsage, usageRandomness)==productOfCiphertexts, "This is not a valid reveal");
        TS_net_usage_decrypted[time_slot]=netUsage;
        //store the price for later
        settlement_price[time_slot]=price;
    }

    function auctioneerRevealSettlements(uint256 time_slot, 
                                        uint256 settlementRandomness, 
                                        uint256[] memory enc_token_randomness,
                                        uint256[] memory tokens_encryptions) public {
        uint256 productOfCiphertexts=1;
        uint256 modulus=auctioneer._publicKey.n();
        require(settlement_price[time_slot]>0, "This time slot has not been settled");
        for (uint i = 0; i < num_people; i++) {
            // this is because of the homomorphic property
            productOfCiphertexts=(productOfCiphertexts*tokens_encryptions[i])%(modulus**2);
            user_net_tokens_encrypted[users[i]._address]=(user_net_tokens_encrypted[users[i]._address]*tokens_encryptions[i])%(modulus**2);
            TS_token_randomness_encrypted[time_slot][users[i]._address]=(enc_token_randomness[i]*1);
        }
        require(auctioneer._publicKey.encrypt((TS_net_usage_decrypted[time_slot]*settlement_price[time_slot])%modulus, settlementRandomness)==productOfCiphertexts,"ciphertexts don't match net usage");
    }


}
