// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// This contract simulates a vulnerable upgradeable proxy
// It would trigger multiple HARD_FAIL violations

contract VulnerableProxy {
    address private _implementation;
    
    // Missing initializer - would trigger INITIALIZER_ABUSE
    constructor() {
        _implementation = msg.sender;
    }
    
    // Missing authorization - would trigger MISSING_AUTH
    function upgradeTo(address newImplementation) external {
        _implementation = newImplementation;
    }
    
    // Contains selfdestruct - would trigger SELFDESTRUCT_PATHS
    function emergencySelfDestruct() external {
        selfdestruct(payable(msg.sender));
    }
    
    // Untrusted delegatecall - would trigger DELEGATECALL_UNTRUSTED
    function executeCall(address target, bytes memory data) external {
        (bool success, ) = target.delegatecall(data);
        require(success, "Delegatecall failed");
    }
}
