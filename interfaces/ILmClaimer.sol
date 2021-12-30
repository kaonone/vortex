// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

interface ILmClaimer {
    function claimEpoch(
        uint256 epoch,
        uint256 amount,
        bytes32[] memory merkleProof
    ) external;
}
