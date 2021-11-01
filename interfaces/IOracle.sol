// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

interface IOracle {
    /**
     * @dev The market is closed if the market is not in its regular trading period.
     */
    function isMarketClosed() external returns (bool);

    /**
     * @dev The oracle service was shutdown and never online again.
     */
    function isTerminated() external returns (bool);

    /**
     * @dev Get collateral symbol.
     */
    function collateral() external view returns (string memory);

    /**
     * @dev Get underlying asset symbol.
     */
    function underlyingAsset() external view returns (string memory);

    /**
     * @dev Mark price.
     */
    function priceTWAPLong()
        external
        returns (int256 newPrice, uint256 newTimestamp);

    /**
     * @dev Index price.
     */
    function priceTWAPShort()
        external
        returns (int256 newPrice, uint256 newTimestamp);
}
