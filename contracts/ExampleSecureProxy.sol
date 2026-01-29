// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ExampleSecureProxy
 * @dev Demonstrates a proxy that PASSES all SIS proxy upgrade gate checks
 * This is the pattern that should be used in production.
 */
contract ExampleSecureProxy {
    address private _implementation;
    address private _admin;
    
    // Events for transparency
    event Upgraded(address indexed implementation);
    event AdminChanged(address indexed previousAdmin, address indexed newAdmin);
    
    // Constructor sets initial admin (safe for non-upgradeable)
    constructor(address admin_) {
        _admin = admin_;
    }
    
    // Modifier for admin-only functions
    modifier onlyAdmin() {
        require(msg.sender == _admin, "ExampleSecureProxy: caller is not admin");
        _;
    }
    
    /**
     * @dev Upgrade the implementation address
     * @param newImplementation Address of the new implementation
     */
    function upgradeTo(address newImplementation) external onlyAdmin {
        require(newImplementation != address(0), "ExampleSecureProxy: zero address");
        _implementation = newImplementation;
        emit Upgraded(newImplementation);
    }
    
    /**
     * @dev Change the admin address
     * @param newAdmin Address of the new admin
     */
    function changeAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "ExampleSecureProxy: zero address");
        emit AdminChanged(_admin, newAdmin);
        _admin = newAdmin;
    }
    
    /**
     * @dev Get current implementation address
     */
    function implementation() external view returns (address) {
        return _implementation;
    }
    
    /**
     * @dev Get current admin address
     */
    function admin() external view returns (address) {
        return _admin;
    }
}
