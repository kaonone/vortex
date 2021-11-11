// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;


interface IMcBstaking {
    function balanceOf(
        address _account
    ) external view returns (uint256);

    function calcUnlockTime(
        address _account,
        uint256 _amount
    ) external view returns (uint256);

    function stake(uint256 _amount) external;

    function restake() external;

    function redeem() external;

    function secondsUntilUnlock(
        address _account
    ) external view returns (uint256);
}