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
import {IUniswapRouterV2} from "../interfaces/uniswap/IUniswapRouterV2.sol";


import {
    BaseStrategy
} from "../deps/BaseStrategy.sol";

contract MyStrategy is BaseStrategy {
    using SafeERC20Upgradeable for IERC20Upgradeable;
    using AddressUpgradeable for address;
    using SafeMathUpgradeable for uint256;

    event TreeDistribution(address indexed token, uint256 amount, uint256 indexed blockNumber, uint256 timestamp);

    // address public want // Inherited from BaseStrategy, the token the strategy wants, swaps into and tries to grow
    address public lpComponent; // Token we provide liquidity with
    address public reward; // Token we farm and swap to want / lpComponent

    address public constant wETH_TOKEN = 0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619;
    address public constant wBTC_TOKEN = 0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6;
    address public constant ibBTC_TOKEN = 0x4EaC4c4e9050464067D673102F8E24b2FccEB350;
    address public constant SUSHI_TOKEN = 0x0b3F868E0BE5597D5DB7fEB59E1CADBb0fdDa50a; // Reward to be distributed

    address public constant CHEF = 0x0769fd68dFb93167989C6f7254cd0D766Fb2841F; // MiniChefV2
    address public constant SUSHISWAP_ROUTER = 0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506;
    address public constant ibBTC_WBTC_LP = 0x8F8e95Ff4B4c5E354ccB005c6B0278492D7B5907; // want

    address public constant badgerTree = 0x2C798FaFd37C7DCdcAc2498e19432898Bc51376b;

    // slippage tolerance 0.5% (divide by MAX_BPS)
    uint256 public sl = 50;
    uint256 public pid = 24; // ibBTC_WBTC_LP pool ID
    uint256 public constant MAX_BPS = 10000;

    function initialize(
        address _governance,
        address _strategist,
        address _controller,
        address _keeper,
        address _guardian,
        address[3] memory _wantConfig,
        uint256[3] memory _feeConfig
    ) public initializer {
        __BaseStrategy_init(_governance, _strategist, _controller, _keeper, _guardian);

        /// @dev Add config here
        want = _wantConfig[0];
        lpComponent = _wantConfig[1];
        reward = _wantConfig[2];

        performanceFeeGovernance = _feeConfig[0];
        performanceFeeStrategist = _feeConfig[1];
        withdrawalFee = _feeConfig[2];

        /// @dev do one off approvals here
        IERC20Upgradeable(want).safeApprove(CHEF, type(uint256).max);
        IERC20Upgradeable(reward).safeApprove(SUSHISWAP_ROUTER, type(uint256).max);
        IERC20Upgradeable(wBTC_TOKEN).safeApprove(SUSHISWAP_ROUTER, type(uint256).max);
        IERC20Upgradeable(wETH_TOKEN).safeApprove(SUSHISWAP_ROUTER, type(uint256).max);

        IERC20Upgradeable(wBTC_TOKEN).safeApprove(ibBTC_WBTC_LP, type(uint256).max);
        IERC20Upgradeable(ibBTC_TOKEN).safeApprove(ibBTC_WBTC_LP, type(uint256).max);
    }

    /// ===== View Functions =====

    // @dev Specify the name of the strategy
    function getName() external override pure returns (string memory) {
        return "ibBTC-wBTC-SLP-Rewards-Badger-Strategy";
    }

    // @dev Specify the version of the Strategy, for upgrades
    function version() external pure returns (string memory) {
        return "1.0";
    }

    /// @dev Balance of want currently held in strategy positions
    function balanceOfPool() public override view returns (uint256) {
        (uint256 amount, ) = IMiniChefV2(CHEF).userInfo(pid, address(this));
        return amount;
    }

    /// @dev Balance of a certain token currently held in strategy positions
    function balanceOfToken(address _token) public view returns (uint256) {
        return IERC20Upgradeable(_token).balanceOf(address(this));
    }

    /// @dev Returns true if this strategy requires tending
    function isTendable() public override view returns (bool) {
        return true;
    }

    /// @dev These are the tokens that cannot be moved except by the vault
    function getProtectedTokens() public override view returns (address[] memory) {
        address[] memory protectedTokens = new address[](3);
        protectedTokens[0] = want;
        protectedTokens[1] = lpComponent;
        protectedTokens[2] = reward;
        return protectedTokens;
    }

    /// @notice returns amounts of rewards pending for this Strategy to be Harvest
    function checkPendingReward() public view returns (uint256, uint256) {
        uint256 _pendingSushi = IMiniChefV2(CHEF).pendingSushi(
            pid,
            address(this)
        );
        IRewarder rewarder = IMiniChefV2(CHEF).rewarder(pid);
        (, uint256[] memory _rewardAmounts) = rewarder.pendingTokens(
            pid,
            address(this),
            0
        );

        uint256 _pendingMatic;
        if (_rewardAmounts.length > 0) {
            _pendingMatic = _rewardAmounts[0];
        }
        return (_pendingSushi, _pendingMatic);
    }

    /// ===== Internal Core Implementations =====

    /// @dev security check to avoid moving tokens that would cause a rugpull, edit based on strat
    function _onlyNotProtectedTokens(address _asset) internal override {
        address[] memory protectedTokens = getProtectedTokens();

        for(uint256 x = 0; x < protectedTokens.length; x++){
            require(address(protectedTokens[x]) != _asset, "Asset is protected");
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
        (uint256 staked, ) = IMiniChefV2(CHEF).userInfo(pid, address(this));

        // Withdraw all want from Chef
        IMiniChefV2(CHEF).withdraw(pid, staked, address(this));

        // Some sushi may be returned to the contract and picked up next harvest

        // Note: All want is automatically withdrawn outside this "inner hook" in base strategy function
    }
    /// @dev withdraw the specified amount of want, liquidate from lpComponent to want, paying off any necessary debt for the conversion
    function _withdrawSome(uint256 _amount) internal override returns (uint256) {
        // Withdraw all want from Chef
        IMiniChefV2(CHEF).withdraw(pid, _amount, address(this));

        // Some sushi may be returned to the contract and picked up next harvest

        // Note: All want is automatically withdrawn outside this "inner hook" in base strategy function

        return _amount;
    }

    /// @dev Harvest from strategy mechanics, realizing increase in underlying position
    function harvest() external whenNotPaused returns (uint256 harvested) {
        _onlyAuthorizedActors();

        uint256 _before = IERC20Upgradeable(want).balanceOf(address(this));

        // Note: Deposit of zero harvests rewards balance, but go ahead and deposit idle want if we have it
        IMiniChefV2(CHEF).deposit(pid, _before, address(this));

        // Harvest rewards from MiniChefV2
        IMiniChefV2(CHEF).harvest(pid, address(this));

        // Get total rewards (WMATIC & SUSHI)
        uint256 rewardsAmount = IERC20Upgradeable(reward).balanceOf(address(this));
        uint256 sushiAmount = IERC20Upgradeable(SUSHI_TOKEN).balanceOf(address(this));

        // If no reward, then nothing happens
        if (rewardsAmount == 0 && sushiAmount == 0) {
            return 0;
        }

        // Send CRV rewards to BadgerTree
        if (sushiAmount > 0) {
            IERC20Upgradeable(SUSHI_TOKEN).safeTransfer(badgerTree, sushiAmount);
            emit TreeDistribution(SUSHI_TOKEN, sushiAmount, block.number, block.timestamp);
        }

        if (rewardsAmount > 0) {
            uint256 _half = rewardsAmount.mul(5000).div(MAX_BPS);

            // Swap rewarded wMATIC for wBTC through wETH path
            address[] memory path = new address[](3);
            path[0] = reward;
            path[1] = wETH_TOKEN;
            path[2] = wBTC_TOKEN;
            IUniswapRouterV2(SUSHISWAP_ROUTER).swapExactTokensForTokens(_half, 0, path, address(this), now);

            // Swap rewarded wMATIC for ibBTC through wETH -> wBTC path
            path = new address[](4);
            path[0] = reward;
            path[1] = wETH_TOKEN;
            path[2] = wBTC_TOKEN;
            path[3] = ibBTC_TOKEN;
            IUniswapRouterV2(SUSHISWAP_ROUTER).swapExactTokensForTokens(rewardsAmount.sub(_half), 0, path, address(this), now);

            // Add liquidity for ibBTC-wBTC pool
            uint256 _wbtcIn = balanceOfToken(wBTC_TOKEN);
            uint256 _ibbtcIn = balanceOfToken(ibBTC_TOKEN);
            IUniswapRouterV2(SUSHISWAP_ROUTER).addLiquidity(
                wBTC_TOKEN,
                ibBTC_TOKEN,
                _wbtcIn,
                _ibbtcIn,
                _wbtcIn.mul(sl).div(MAX_BPS),
                _ibbtcIn.mul(sl).div(MAX_BPS),
                address(this),
                now
            );
        }

        uint256 earned = IERC20Upgradeable(want).balanceOf(address(this)).sub(_before);

        /// @notice Keep this in so you get paid!
        (uint256 governancePerformanceFee, uint256 strategistPerformanceFee) = _processPerformanceFees(earned);

        /// @dev Harvest event that every strategy MUST have, see BaseStrategy
        emit Harvest(earned, block.number);

        return earned;
    }

    /// @dev Rebalance, Compound or Pay off debt here
    function tend() external whenNotPaused {
        _onlyAuthorizedActors();

        if(balanceOfWant() > 0) {
            _deposit(balanceOfWant());
        }
    }


    /// ===== Internal Helper Functions =====

    /// @dev used to manage the governance and strategist fee, make sure to use it to get paid!
    function _processPerformanceFees(uint256 _amount) internal returns (uint256 governancePerformanceFee, uint256 strategistPerformanceFee) {
        governancePerformanceFee = _processFee(want, _amount, performanceFeeGovernance, IController(controller).rewards());

        strategistPerformanceFee = _processFee(want, _amount, performanceFeeStrategist, strategist);
    }

    function setSlippageTolerance(uint256 _s) external whenNotPaused {
        _onlyGovernanceOrStrategist();
        sl = _s;
    }
}
