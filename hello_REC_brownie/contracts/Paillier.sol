// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Paillier {
    uint256 public n;
    uint256 public g;

    constructor(uint256 _n, uint256 _g) {
        n = _n;
        g = _g;
    }

    function encrypt(uint256 plaintext, uint256 randomness) external view returns (uint256) {
        require(plaintext < n, "Plaintext is too large");
        uint256 ciphertext = (ModPow(g, plaintext, n ** 2) * ModPow(randomness, n, n ** 2)) % (n ** 2);
        return ciphertext;
    }

    function decrypt(uint256 ciphertext, uint256 lambda, uint256 mu) public view returns (uint256) {
        uint256 c = ModPow(ciphertext, lambda, n ** 2);
        uint256 L = (c - 1) / n;
        
        return (L * mu) % n;
    }


    
    
    function ModPow(uint256 base, uint256 exponent, uint256 modulus) internal view returns (uint256 xx) {
        assembly {
            let freemem := mload(0x40)
            // length_of_BASE: 32 bytes
            mstore(freemem, 0x20)
            // length_of_EXPONENT: 32 bytes
            mstore(add(freemem, 0x20), 0x20)
            // length_of_MODULUS: 32 bytes
            mstore(add(freemem, 0x40), 0x20)
            // BASE: The input x
            mstore(add(freemem, 0x60), base)
            // EXPONENT: (N + 1) / 4 = 0xc19139cb84c680a6e14116da060561765e05aa45a1c72a34f082305b61f3f52
            mstore(add(freemem, 0x80), exponent)
            // MODULUS: N = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47
            mstore(add(freemem, 0xA0), modulus)
            let success := staticcall(
                sub(gas(), 2000),
                // call the address 0x00......05
                5,
                // loads the 6 * 32 bytes inputs from <freemem>
                freemem,
                0xC0,
                // stores the 32 bytes return at <freemem>
                freemem,
                0x20
            )
            xx := mload(freemem)
        }
    }
    

}