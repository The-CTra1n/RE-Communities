pragma solidity ^0.8.13;

import {Test, console2} from "forge-std/Test.sol";
import {Paillier} from "../src/Paillier.sol";
import {System} from "../src/RE_System.sol";


// if netUsage is negative, be careful 
// (encrypt only positive values¿¿??)

contract SystemTest is Test {

    System RE_System;
    uint256 p=13;
    uint256 q=17;
    uint256 n=p*q;
    uint256 g=4886; 
    uint256 lambda=48;
    uint256 mu=159;
    
    address auctioneer=0xE0f5206BBD039e7b0592d8918820024e2a7437b9;
    Paillier public paillier;

    address[] users;
    uint256 num_users=5;

    function setUp() public {
        paillier= new Paillier(n, g,  lambda, mu);
        RE_System=new System(auctioneer,paillier);
        users=createUsers(num_users);
    }

    function testAddingPlayer() public{
        RE_System.addPlayer(users[0], paillier);
    }



















    function createUsers(uint256 userNum) public returns (address[] memory){
        address[] memory _users = new address[](userNum);
        for (uint256 i = 0; i < userNum; i++) {
            // This will create a new address using `keccak256(i)` as the private key
            address _user = vm.addr(uint256(keccak256(abi.encodePacked(i))));
            vm.deal(_user, 100 ether);
            _users[i] = _user;
        }
        return _users;
    }
}