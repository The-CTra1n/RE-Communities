pragma solidity ^0.8.0;

import {Paillier} from "../src/Paillier.sol";

contract System {
    struct Player{
        address _address;
        Paillier _publicKey;
    }

    struct Settlement{
        // these two variables are used by users to verify
        // data that auctioneer publishes

        //using user public Key
        uint256 userEncryptedNetTokens;

        // the randomness used by auctioneer to encrypt the users
        // value in the public ledger, only accessible by the user
        uint256 userEncryptedRandomness; 

        //using auctioneer public Key
        uint256 auctioneerEncryptedNetTokens;
    }
    Player public auctioneer;
    uint num_people;

    // a mapping of time slots to demand and supply
    mapping(uint256 => mapping(address => uint256)) public TS_net_usage_encrypted;
    mapping(uint256 => uint256) public TS_net_usage_decrypted;
    mapping(uint256 => uint256) public settlement_price;
    
    Player[] public users;
    mapping (address => uint256) public user_net_usage_encrypted;
    // can we use an extra array for "greenness"?
    // might not be necessary
    // mapping (uint => uint256) public user_net_green_tokens_encrypted;


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
    }

    function userRevealNetUsage(uint256 time_slot,uint256 encryptedUsage) public {
        require(encryptedUsage>0, "0 values not allowed");
        TS_net_usage_encrypted[time_slot][msg.sender]=encryptedUsage;
    }


    // reveal checks depend on the encrypted ciphertexts being such that
    // the product of ciphertexts being the encryption of the sum of the plaintexts
    function auctioneerRevealNetUsage(uint256 time_slot, uint256 netUsage, uint256 usageRandomness, uint256 price) public {
        uint256 productOfCiphertexts=1;
        require(TS_net_usage_decrypted[time_slot]==0, "This time slot is already finished");
        for (uint i = 0; i < num_people; i++) {
            if (TS_net_usage_encrypted[time_slot][users[i]._address]>0){
                // this is because of the homomorphic property
                productOfCiphertexts=productOfCiphertexts*TS_net_usage_encrypted[time_slot][users[i]._address];
            }
        }

        //may need to add the modulus to netUsage if it is negative
        require(auctioneer._publicKey.encrypt(netUsage, usageRandomness)==productOfCiphertexts, "This is not a valid reveal");
        
        //store the price for later
        settlement_price[time_slot]=price;

    }



    function auctioneerRevealSettlements(uint256 time_slot, uint256 settlementRandomness, Settlement[] memory userSettlements) public {
        uint256 productOfCiphertexts=1;
        require(TS_net_usage_decrypted[time_slot]==0, "This time slot is already finished");
        for (uint i = 0; i < num_people; i++) {
            if (TS_net_usage_encrypted[time_slot][users[i]._address]>0){
                // this is because of the homomorphic property
                productOfCiphertexts=productOfCiphertexts*TS_net_usage_encrypted[time_slot][users[i]._address];
            }
        }
    
    }




}