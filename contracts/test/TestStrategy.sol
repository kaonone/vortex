// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "../BasisStrategy.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract TestStrategy is BasisStrategy {
    using SafeERC20 for IERC20;

    constructor(
        address _long,
        address _pool,
        address _vault,
        address _oracle,
        address _router,
        address _governance,
        address _mcLiquidityPool,
        uint256 _perpetualIndex
    )
        BasisStrategy(
            _long,
            _pool,
            _vault,
            _oracle,
            _router,
            _governance,
            _mcLiquidityPool,
            _perpetualIndex
        )
    {}

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

    function depositToMarginAccount(uint256 _amount) external {
        IERC20(want).safeTransferFrom(msg.sender, address(this), _amount);
        _depositToMarginAccount(_amount);
    }

    function openPerpPosition(uint256 _amount) external {
        IERC20(want).safeTransferFrom(msg.sender, address(this), _amount);
        // deposit funds to the margin account to enable trading
        _depositToMarginAccount(_amount);
        // get the long asset mark price from the MCDEX oracle
        (int256 price, ) = oracle.priceTWAPLong();
        // calculate the number of contracts (*1e12 because USDC is 6 decimals)
        int256 contracts = ((int256(_amount) * DECIMAL_SHIFT) * 1e18) / price;
        // open short position
        int256 tradeAmount = mcLiquidityPool.trade(
            perpetualIndex,
            address(this),
            -contracts,
            price - slippageTolerance,
            block.timestamp,
            referrer,
            0x40000000
        );
        emit PerpPositionOpened(tradeAmount, perpetualIndex, _amount);
    }

    function closePerpPosition(uint256 _amount) external {
        // get the long asset mark price from the MCDEX oracle
        (int256 price, ) = oracle.priceTWAPLong();
        int256 tradeAmount;
        // calculate the number of contracts (*1e12 because USDC is 6 decimals)
        int256 contracts = ((int256(_amount) * DECIMAL_SHIFT) * 1e18) / price;
        if (contracts + getMarginPositions() < -dust) {
            // close short position
            tradeAmount = mcLiquidityPool.trade(
                perpetualIndex,
                address(this),
                contracts,
                price + slippageTolerance,
                block.timestamp,
                referrer,
                0x40000000
            );
        } else {
            // close all remaining short positions
            tradeAmount = mcLiquidityPool.trade(
                perpetualIndex,
                address(this),
                -getMarginPositions(),
                price + slippageTolerance,
                block.timestamp,
                referrer,
                0x40000000
            );
        }
        emit PerpPositionClosed(tradeAmount, perpetualIndex, _amount);
    }

    function closeAllPerpPositions(uint256 _amount) external {
        _closeAllPerpPositions();
    }
}
