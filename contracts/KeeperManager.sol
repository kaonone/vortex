// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "@openzeppelin/contracts/security/Pausable.sol";
import "@ozUpgradesV4/contracts/access/OwnableUpgradeable.sol";

import "@ozUpgradesV4/contracts/security/PausableUpgradeable.sol";
import "../interfaces/IStrategy.sol";

contract KeeperManager is OwnableUpgradeable, PausableUpgradeable {
    address public strategy;
    address public registryContract;
    uint256 public cooldown;
    uint256 public lastTimestamp;

    event CooldownSet(uint256 cooldown);
    event StrategySet(address indexed strategy);
    event RegistryContractSet(address indexed registryContract);

    function initialize(
        address _strategy,
        uint256 _cooldown,
        address _registryContract
    ) public initializer {
        __Ownable_init();
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
        IStrategy(strategy).harvest();
    }
}
