// SPDX-License-Identifier: MIT

pragma solidity ^0.6.11;
pragma experimental ABIEncoderV2;

import "../deps/@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";
import "../deps/@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";
import "../deps/@openzeppelin/contracts-upgradeable/math/MathUpgradeable.sol";
import "../deps/@openzeppelin/contracts-upgradeable/utils/AddressUpgradeable.sol";
import "../deps/@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";

import "../interfaces/badger/IController.sol";

import {IMiniChefV2} from "../interfaces/sushiswap/IMinichef.sol";
import {IRewarder} from "../interfaces/sushiswap/IRewarder.sol";
import {ISettV4} from "../interfaces/badger/ISettV4.sol";
import {IUniswapRouterV2} from "../interfaces/uniswap/IUniswapRouterV2.sol";

import {BaseStrategy} from "../deps/BaseStrategy.sol";

contract StrategySushiBadgerWbtcWeth is BaseStrategy {
    using SafeERC20Upgradeable for IERC20Upgradeable;
    using AddressUpgradeable for address;
    using SafeMathUpgradeable for uint256;

    event TreeDistribution(
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );

    // address public want // Inherited from BaseStrategy, the token the strategy wants, swaps into and tries to grow
    address public reward; // Token we farm and swap to want

    address public constant WBTC_TOKEN =
        0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f;
    address public constant WETH_TOKEN =
        0x82aF49447D8a07e3bd95BD0d56f35241523fBab1;

    address public constant CHEF = 0xF4d73326C13a4Fc5FD7A064217e12780e9Bd62c3; // MiniChefV2
    address public constant SUSHISWAP_ROUTER =
        0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506;

    address public constant WETH_SUSHI_SLP =
        0x3221022e37029923aCe4235D812273C5A42C322d;
    address public constant WETH_SUSHI_SLP_VAULT =
        0xe774D1FB3133b037AA17D39165b8F45f444f632d;

    address public constant badgerTree =
        0x635EB2C39C75954bb53Ebc011BDC6AfAAcE115A6;

    // slippage tolerance 0.5% (divide by MAX_BPS) - Changeable by Governance or Strategist
    uint256 public sl;
    uint256 public constant pid = 3; // WBTC_WETH_LP pool ID
    uint256 public constant MAX_BPS = 10000;

    function initialize(
        address _governance,
        address _strategist,
        address _controller,
        address _keeper,
        address _guardian,
        address[2] memory _wantConfig,
        uint256[3] memory _feeConfig
    ) public initializer {
        __BaseStrategy_init(
            _governance,
            _strategist,
            _controller,
            _keeper,
            _guardian
        );

        /// @dev Add config here
        want = _wantConfig[0];
        reward = _wantConfig[1];

        performanceFeeGovernance = _feeConfig[0];
        performanceFeeStrategist = _feeConfig[1];
        withdrawalFee = _feeConfig[2];

        // Set default slippage value
        sl = 50;

        /// @dev do one off approvals here
        IERC20Upgradeable(want).safeApprove(CHEF, type(uint256).max);
        IERC20Upgradeable(reward).safeApprove(
            SUSHISWAP_ROUTER,
            type(uint256).max
        );
        IERC20Upgradeable(WBTC_TOKEN).safeApprove(
            SUSHISWAP_ROUTER,
            type(uint256).max
        );
        IERC20Upgradeable(WETH_TOKEN).safeApprove(
            SUSHISWAP_ROUTER,
            type(uint256).max
        );
        IERC20Upgradeable(WETH_SUSHI_SLP).safeApprove(
            WETH_SUSHI_SLP_VAULT,
            type(uint256).max
        );
    }

    /// ===== View Functions =====

    // @dev Specify the name of the strategy
    function getName() external pure override returns (string memory) {
        return "StrategySushiBadgerWbtcWeth";
    }

    // @dev Specify the version of the Strategy, for upgrades
    function version() external pure returns (string memory) {
        return "1.0";
    }

    /// @dev Balance of want currently held in strategy positions
    function balanceOfPool() public view override returns (uint256) {
        (uint256 amount, ) = IMiniChefV2(CHEF).userInfo(pid, address(this));
        return amount;
    }

    /// @dev Balance of a certain token currently held in strategy positions
    function balanceOfToken(address _token) public view returns (uint256) {
        return IERC20Upgradeable(_token).balanceOf(address(this));
    }

    /// @dev Returns true if this strategy requires tending
    function isTendable() public view override returns (bool) {
        return balanceOfWant() > 0;
    }

    /// @dev These are the tokens that cannot be moved except by the vault
    function getProtectedTokens()
        public
        view
        override
        returns (address[] memory)
    {
        address[] memory protectedTokens = new address[](4);
        protectedTokens[0] = want;
        protectedTokens[1] = reward;
        protectedTokens[2] = WBTC_TOKEN;
        protectedTokens[3] = WETH_TOKEN;
        return protectedTokens;
    }

    /// @notice returns amounts of rewards pending for this Strategy to be Harvest
    function checkPendingReward() public view returns (uint256) {
        return IMiniChefV2(CHEF).pendingSushi(pid, address(this));
    }

    /// @notice sets slippage tolerance for liquidity provision
    function setSlippageTolerance(uint256 _s) external whenNotPaused {
        _onlyGovernanceOrStrategist();
        sl = _s;
    }

    /// ===== Internal Core Implementations =====

    /// @dev security check to avoid moving tokens that would cause a rugpull, edit based on strat
    function _onlyNotProtectedTokens(address _asset) internal override {
        address[] memory protectedTokens = getProtectedTokens();

        for (uint256 x = 0; x < protectedTokens.length; x++) {
            require(
                address(protectedTokens[x]) != _asset,
                "Asset is protected"
            );
        }
    }

    /// @dev invest the amount of want
    /// @notice When this function is called, the controller has already sent want to this
    /// @notice Just get the current balance and then invest accordingly
    function _deposit(uint256 _amount) internal override {
        // Deposit all want in sushi chef
        IMiniChefV2(CHEF).deposit(pid, _amount, address(this));
    }

    /// @dev utility function to withdraw everything for migration
    function _withdrawAll() internal override {
        // Withdraw all want from Chef
        IMiniChefV2(CHEF).withdraw(pid, balanceOfPool(), address(this));

        // Some SUSHI may be returned to the contract and picked up next harvest

        // Note: All want is automatically withdrawn outside this "inner hook" in base strategy function
    }

    /// @dev withdraw the specified amount of want, liquidate from lpComponent to want, paying off any necessary debt for the conversion
    function _withdrawSome(uint256 _amount)
        internal
        override
        returns (uint256)
    {
        // Due to rounding errors on the Controller, the amount may be slightly higher than the available amount in edge cases.
        uint256 wantBalance = balanceOfWant();
        if (wantBalance < _amount) {
            uint256 toWithdraw = _amount.sub(wantBalance);

            uint256 poolBalance = balanceOfPool();
            if (poolBalance < toWithdraw) {
                IMiniChefV2(CHEF).withdraw(pid, poolBalance, address(this));
            } else {
                IMiniChefV2(CHEF).withdraw(pid, toWithdraw, address(this));
            }
        }

        // Some SUSHI may be returned to the contract and picked up next harvest

        // Note: All want is automatically withdrawn outside this "inner hook" in base strategy function

        return MathUpgradeable.min(_amount, balanceOfWant());
    }

    /// @dev Harvest from strategy mechanics, realizing increase in underlying position
    function harvest() external whenNotPaused returns (uint256 harvested) {
        _onlyAuthorizedActors();

        uint256 _before = balanceOfWant();

        // Harvest rewards from MiniChefV2
        IMiniChefV2(CHEF).harvest(pid, address(this));

        // Get total rewards (SUSHI)
        uint256 rewardsAmount = balanceOfToken(reward);

        // If no reward, then nothing happens
        if (rewardsAmount == 0) {
            return 0;
        }

        // Swap 50% rewarded SUSHI for WETH
        uint256 toWeth = rewardsAmount.mul(5000).div(MAX_BPS);
        address[] memory path = new address[](2);
        path[0] = reward;
        path[1] = WETH_TOKEN;
        IUniswapRouterV2(SUSHISWAP_ROUTER).swapExactTokensForTokens(
            toWeth,
            0,
            path,
            address(this),
            now
        );

        // Use 25% rewarded Sushi to add liquidity for WETH-SUSHI pool
        uint256 wethToSushiSlp = balanceOfToken(WETH_TOKEN).mul(5000).div(
            MAX_BPS
        );
        uint256 sushiIn = rewardsAmount.mul(2500).div(MAX_BPS);
        IUniswapRouterV2(SUSHISWAP_ROUTER).addLiquidity(
            WETH_TOKEN,
            reward,
            wethToSushiSlp,
            sushiIn,
            wethToSushiSlp.mul(sl).div(MAX_BPS),
            sushiIn.mul(sl).div(MAX_BPS),
            address(this),
            now
        );

        uint256 wethSushiSlpBalance = balanceOfToken(WETH_SUSHI_SLP);

        if (wethSushiSlpBalance > 0) {
            // Process fees on Sushi Rewards
            _processRewardsFees(wethSushiSlpBalance, WETH_SUSHI_SLP);

            uint256 treeVaultBalanceBefore = ISettV4(WETH_SUSHI_SLP_VAULT)
                .balanceOf(badgerTree);
            ISettV4(WETH_SUSHI_SLP_VAULT).depositFor(
                badgerTree,
                balanceOfToken(WETH_SUSHI_SLP)
            );
            uint256 treeVaultBalanceAfter = ISettV4(WETH_SUSHI_SLP_VAULT)
                .balanceOf(badgerTree);

            emit TreeDistribution(
                WETH_SUSHI_SLP_VAULT,
                treeVaultBalanceAfter.sub(treeVaultBalanceBefore),
                block.number,
                block.timestamp
            );
        }

        // Swap remaining 25% rewarded SUSHI for WBTC through WETH path
        uint256 toWbtc = balanceOfToken(reward);
        path = new address[](3);
        path[0] = reward;
        path[1] = WETH_TOKEN;
        path[2] = WBTC_TOKEN;
        IUniswapRouterV2(SUSHISWAP_ROUTER).swapExactTokensForTokens(
            toWbtc,
            0,
            path,
            address(this),
            now
        );

        // Add liquidity for WBTC-WETH pool
        uint256 wbtcIn = balanceOfToken(WBTC_TOKEN);
        uint256 wethIn = balanceOfToken(WETH_TOKEN);
        IUniswapRouterV2(SUSHISWAP_ROUTER).addLiquidity(
            WBTC_TOKEN,
            WETH_TOKEN,
            wbtcIn,
            wethIn,
            wbtcIn.mul(sl).div(MAX_BPS),
            wethIn.mul(sl).div(MAX_BPS),
            address(this),
            now
        );

        uint256 earned = balanceOfWant().sub(_before);

        /// @notice Keep this in so you get paid!
        _processPerformanceFees(earned);

        /// @dev Harvest event that every strategy MUST have, see BaseStrategy
        emit Harvest(earned, block.number);

        return earned;
    }

    /// @dev Rebalance, Compound or Pay off debt here
    function tend() external whenNotPaused {
        _onlyAuthorizedActors();

        uint256 wantBalance = balanceOfWant();
        if (wantBalance > 0) {
            _deposit(wantBalance);
        }
    }

    /// ===== Internal Helper Functions =====

    /// @dev used to manage the governance and strategist fee on earned want, make sure to use it to get paid!
    function _processPerformanceFees(uint256 _amount)
        internal
        returns (
            uint256 governancePerformanceFee,
            uint256 strategistPerformanceFee
        )
    {
        governancePerformanceFee = _processFee(
            want,
            _amount,
            performanceFeeGovernance,
            IController(controller).rewards()
        );
        strategistPerformanceFee = _processFee(
            want,
            _amount,
            performanceFeeStrategist,
            strategist
        );
    }

    /// @dev used to manage the governance and strategist fee on earned rewards, make sure to use it to get paid!
    function _processRewardsFees(uint256 _amount, address token)
        internal
        returns (uint256 governanceRewardsFee, uint256 strategistRewardsFee)
    {
        governanceRewardsFee = _processFee(
            token,
            _amount,
            performanceFeeGovernance,
            IController(controller).rewards()
        );
        strategistRewardsFee = _processFee(
            token,
            _amount,
            performanceFeeStrategist,
            strategist
        );
    }
}
