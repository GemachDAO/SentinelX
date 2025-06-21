// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint256) public balances;
    address public owner;
    bool private locked;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Reentrancy vulnerability
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable to reentrancy - external call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;
    }
    
    // Integer overflow vulnerability (pre-0.8.0 style)
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    // Access control vulnerability
    function emergencyWithdraw() public {
        // Missing onlyOwner modifier
        payable(msg.sender).transfer(address(this).balance);
    }
    
    // Unchecked external call
    function callExternal(address target, bytes memory data) public {
        // No return value check
        target.call(data);
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }
    
    modifier noReentrancy() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
}
