// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "@oz-upgradeable/contracts/access/OwnableUpgradeable.sol";
import "@oz-upgradeable/contracts/security/PausableUpgradeable.sol";

import "../interfaces/IStrategy.sol";

contract KeeperManager is OwnableUpgradeable, PausableUpgradeable {
    address public registryContract;
    uint256 public cooldown;
    uint256 public lastTimestamp;

    event CooldownSet(uint256 cooldown);
    event RegistryContractSet(address indexed registryContract);

    function initialize(uint256 _cooldown, address _registryContract)
        public
        initializer
    {
        __Ownable_init();
        __Pausable_init();
        cooldown = _cooldown;
        registryContract = _registryContract;
    }

    function setCoolDown(uint256 _cooldown) public onlyOwner {
        cooldown = _cooldown;
        emit CooldownSet(_cooldown);
    }

    function setRegistryContract(address _registryContract) public onlyOwner {
        registryContract = _registryContract;
        emit RegistryContractSet(_registryContract);
    }

    /**
     * @param  checkData  encoded strategy address: abi.encode(strategy, (address))
     */
    function checkUpkeep(bytes calldata checkData)
        external
        returns (bool upkeepNeeded, bytes memory performData)
    {
        address strategy = abi.decode(checkData, (address));

        bool harvestNeeded = IStrategy(strategy).getFundingRate() > 0;
        bool unwindNeeded = !harvestNeeded && !IStrategy(strategy).isUnwind();

        upkeepNeeded =
            (harvestNeeded || unwindNeeded) &&
            (block.timestamp - lastTimestamp) > cooldown;
        performData = checkData;
    }

    function performUpkeep(bytes calldata performData) external {
        require(msg.sender == registryContract, "!chainLinkRegistry");

        address strategy = abi.decode(performData, (address));
        lastTimestamp = block.timestamp;

        if (IStrategy(strategy).getFundingRate() > 0) {
            IStrategy(strategy).harvest();
        } else if (!IStrategy(strategy).isUnwind()) {
            IStrategy(strategy).unwind();
        }
    }
}
