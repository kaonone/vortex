// SPDX-License-Identifier: AGPL V3.0
pragma solidity >=0.8.4;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title VaultRegistry
 * @author akropolis.io
 * @notice Registry contract for storing basis vaults
 */
contract VaultRegistry is Ownable {
    mapping(address => bool) public isVault;

    event VaultRegistered(address indexed vault);
    event VaultDeactivated(address indexed vault);

    function registerVault(address _vault) external onlyOwner {
        require(_vault != address(0), "!_zeroAddress");
        isVault[_vault] = true;
        emit VaultRegistered(_vault);
    }

    function deactivateVault(address _vault) external onlyOwner {
        require(isVault[_vault], "!registered");
        isVault[_vault] = false;
        emit VaultDeactivated(_vault);
    }
}
