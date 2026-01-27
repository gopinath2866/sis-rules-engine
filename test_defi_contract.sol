// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TestDeFiContract {
    address public owner;
    bool public paused = false;
    uint256 public totalSupply;

    constructor() {
        owner = msg.sender;
        totalSupply = 1000000 * 10**18;
    }

    // Irreversible transfer without pause mechanism
    function transfer(address to, uint256 amount) external returns (bool) {
        return true;
    }

    // Owner can mint unlimited tokens
    function mint(uint256 amount) external {
        require(msg.sender == owner, "Not owner");
        totalSupply += amount;
    }

    // No upgrade mechanism - irreversible code
    function emergencyPause() external {
        require(msg.sender == owner, "Not owner");
        paused = true;
    }
}
