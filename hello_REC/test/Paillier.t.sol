// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console2} from "forge-std/Test.sol";
import {Paillier} from "../src/Paillier.sol";


contract CounterTest is Test {
    Paillier public paillier;
    uint256 p=13;
    uint256 q=17;
    uint256 n=p*q;
    uint256 g=4886; 
    uint256 lambda=48;
    uint256 mu=159;

    function setUp() public {
        paillier= new Paillier(n, g,  lambda, mu);
    }

    function testEncrypt() public{
        uint256 plaintext=123;
        uint256 randomness=paillier.generateRandom();
        uint256 e= paillier.encrypt(plaintext,randomness);
        assert(e==25889);
    }

    function testDecrypt() public{
        uint256 plaintext=123;
        uint256 randomness=paillier.generateRandom();
        uint256 e= paillier.encrypt(plaintext,randomness);
        assert(paillier.decrypt(e)==plaintext);
    }

}
