// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "../BasisStrategy.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract TestStrategy is BasisStrategy {
    using SafeERC20 for IERC20;

    function init(
        address _long,
        address _pool,
        address _vault,
        address _router,
        address _weth,
        address _governance,
        address _mcLiquidityPool,
        uint256 _perpetualIndex,
        uint256 _buffer,
        bool _isV2
    ) public {
        BasisStrategy.initialize(
            _long,
            _pool,
            _vault,
            _router,
            _weth,
            _governance,
            _mcLiquidityPool,
            _perpetualIndex,
            _buffer,
            _isV2
        );
    }

    function calculateSplit(uint256 _amount)
        external
        returns (
            uint256 shortPosition,
            uint256 longPosition,
            uint256 bufferPosition
        )
    {
        IERC20(want).safeTransferFrom(msg.sender, address(this), _amount);
        (shortPosition, longPosition, bufferPosition) = _calculateSplit(
            _amount
        );
    }
}
