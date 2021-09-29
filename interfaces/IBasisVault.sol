// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IBasisVault {
    function deposit(uint256, address) external returns (uint256);

    function update(uint256) external returns (uint256);

    function want() external returns (IERC20);
}
