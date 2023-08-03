// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Paillier {
    uint256 public n;
    uint256 public g;

    constructor(uint256 _n, uint256 _g) {
        n = _n;
        g = _g;
    }

    function encrypt(uint256 plaintext, uint256 randomness) external view returns (uint256) {
        require(plaintext < n, "Plaintext is too large");
        uint256 ciphertext = (modPow(g, plaintext, n ** 2) * modPow(randomness, n, n ** 2)) % (n ** 2);
        return ciphertext;
    }

    function decrypt(uint256 ciphertext, uint256 lambda, uint256 mu) public view returns (uint256) {
        uint256 c = modPow(ciphertext, lambda, n ** 2);
        uint256 L = (c - 1) / n;
        
        return (L * mu) % n;
    }


    function modPow(uint256 base, uint256 exponent, uint256 modulus) internal pure returns (uint256) {
        // Modular exponentiation function
        // Implementing this efficiently in Solidity can be challenging due to gas constraints
        // This is a basic implementation and might not be suitable for production use
        uint256 result = 1;
        for (uint256 i = 0; i < exponent; i++) {
            result = (result * base) % modulus;
        }
        return result;
    }
}