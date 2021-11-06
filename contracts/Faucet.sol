// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Faucet is Ownable, Pausable {
    IERC20 public token;
    uint256 public amount;
    uint256 public cooldown = 1 days;

    struct Recipient {
        uint256 lastClaimed;
        uint256 claimedCount;
    }

    mapping(address => Recipient) private receiver;

    event Distributed(address indexed user, uint256 block);

    constructor(address _token, uint256 _amount) {
        token = IERC20(_token);
        amount = _amount;
    }

    function setToken(address _token) public onlyOwner {
        require(_token != address(0), "invalid address");
        token = IERC20(_token);
    }

    function setCoolDown(uint256 _cooldown) public onlyOwner {
        require(_cooldown > 0, "invalid period");
        cooldown = _cooldown * 1 days;
    }

    function setAmount(uint256 _amount) public onlyOwner {
        require(_amount > 0, "invalid amount");
        amount = _amount;
    }

    function lastUpdate(address _account) public returns (bool) {
        return receiver[_account].lastClaimed + cooldown < block.timestamp;
    }

    function distribute(address _account) external onlyOwner whenNotPaused {
        require(lastUpdate(_account) == true, "wait cooldown");
        token.transfer(_account, amount);
        receiver[_account].lastClaimed = block.timestamp;
        receiver[_account].claimedCount += 1;
        emit Distributed(_account, block.timestamp);
    }

    function pause() public onlyOwner {
        _pause();
    }

    function unpause() public onlyOwner {
        _unpause();
    }

    function getUserDetail(address _account)
        public
        view
        returns (uint256, uint256)
    {
        uint256 lastClaim = receiver[_account].lastClaimed;
        uint256 totalClaim = receiver[_account].claimedCount;
        return (lastClaim, totalClaim);
    }
}
