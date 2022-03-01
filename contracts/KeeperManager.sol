// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IStrategy.sol";

contract KeeperManager is Ownable, Pausable {
    address public strategy;
    address public registryContract;
    uint256 public cooldown;
    uint256 public lastTimestamp;
    bool public harvested = true;

    event CooldownSet(uint256 cooldown);
    event StrategySet(address indexed strategy);
    event RegistryContractSet(address indexed registryContract);

    constructor(
        address _strategy,
        uint256 _cooldown,
        address _registryContract
    ) {
        strategy = _strategy;
        cooldown = _cooldown;
        registryContract = _registryContract;
    }

    function setStrategy(address _strategy) public onlyOwner {
        strategy = _strategy;
        emit StrategySet(_strategy);
    }

    function setCoolDown(uint256 _cooldown) public onlyOwner {
        cooldown = _cooldown;
        emit CooldownSet(_cooldown);
    }

    function setRegistryContract(address _registryContract) public onlyOwner {
        registryContract = _registryContract;
        emit RegistryContractSet(_registryContract);
    }

    function checkUpkeep(
        bytes calldata /* checkData */
    )
        external
        returns (
            bool upkeepNeeded,
            bytes memory /* performData */
        )
    {
        upkeepNeeded = (block.timestamp - lastTimestamp) > cooldown;
    }

    function performUpkeep(
        bytes calldata /* performData */
    ) external {
        require(msg.sender == registryContract, "!keeper");
        require(
            (block.timestamp - lastTimestamp) > cooldown,
            "harvest not needed"
        );
        lastTimestamp = block.timestamp;

        if (IStrategy(strategy).getFundingRate() > 0) {
            IStrategy(strategy).harvest();
        } else if (IStrategy(strategy).isUnwind() == false) {
            IStrategy(strategy).unwind();
        } else {
            harvested = false;
        }
    }
}
