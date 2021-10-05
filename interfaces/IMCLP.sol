// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

interface IMCLP {
    function deposit(
        uint256 perpetualIndex,
        address trader,
        int256 amount
    ) external;

    function withdraw(
        uint256 perpetualIndex,
        address trader,
        int256 amount
    ) external;

    function trade(
        uint256 perpetualIndex,
        address trader,
        int256 amount,
        int256 limitPrice,
        uint256 deadline,
        address referrer,
        uint32 flags
    ) external returns (int256 tradeAmount);

    function settle(uint256 perpetualIndex, address trader) external;

    /**
     * @notice Get the account info of the trader. Need to update the funding state and the oracle price
     *         of each perpetual before and update the funding rate of each perpetual after
     * @param perpetualIndex The index of the perpetual in the liquidity pool
     * @param trader The address of the trader
     * @return cash The cash(collateral) of the account
     * @return position The position of the account
     * @return availableMargin The available margin of the account
     * @return margin The margin of the account
     * @return settleableMargin The settleable margin of the account
     * @return isInitialMarginSafe True if the account is initial margin safe
     * @return isMaintenanceMarginSafe True if the account is maintenance margin safe
     * @return isMarginSafe True if the total value of margin account is beyond 0
     * @return targetLeverage   The target leverage for openning position.
     */
    function getMarginAccount(uint256 perpetualIndex, address trader)
        external
        view
        returns (
            int256 cash,
            int256 position,
            int256 availableMargin,
            int256 margin,
            int256 settleableMargin,
            bool isInitialMarginSafe,
            bool isMaintenanceMarginSafe,
            bool isMarginSafe, // bankrupt
            int256 targetLeverage
        );

    function setTargetLeverage(
        uint256,
        address,
        int256
    ) external;

    /**
     * @notice  Query the price, fees and cost when trade agaist amm.
     *          The trading price is determined by the AMM based on the index price of the perpetual.
     *          This method should returns the same result as a 'read-only' trade.
     *          WARN: the result of this function is base on current storage of liquidityPool, not the latest.
     *          To get the latest status, call `syncState` first.
     *
     *          Flags is a 32 bit uint value which indicates: (from highest bit)
     *            - close only      only close position during trading;
     *            - market order    do not check limit price during trading;
     *            - stop loss       only available in brokerTrade mode;
     *            - take profit     only available in brokerTrade mode;
     *          For stop loss and take profit, see `validateTriggerPrice` in OrderModule.sol for details.
     *
     * @param   perpetualIndex  The index of the perpetual in liquidity pool.
     * @param   trader          The address of trader.
     * @param   amount          The amount of position to trader, positive for buying and negative for selling. The amount always use decimals 18.
     * @param   referrer        The address of referrer who will get rebate from the deal.
     * @param   flags           The flags of the trade.
     * @return  tradePrice      The average fill price.
     * @return  totalFee        The total fee collected from the trader after the trade.
     * @return  cost            Deposit or withdraw to let effective leverage == targetLeverage if flags contain USE_TARGET_LEVERAGE. > 0 if deposit, < 0 if withdraw.
     */
    function queryTrade(
        uint256 perpetualIndex,
        address trader,
        int256 amount,
        address referrer,
        uint32 flags
    )
        external
        returns (
            int256 tradePrice,
            int256 totalFee,
            int256 cost
        );
}
