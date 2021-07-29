// SPDX-License-Identifier: MIT

pragma solidity ^0.6.11;
pragma experimental ABIEncoderV2;

import "../deps/@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";
import "../deps/@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";
import "../deps/@openzeppelin/contracts-upgradeable/math/MathUpgradeable.sol";
import "../deps/@openzeppelin/contracts-upgradeable/utils/AddressUpgradeable.sol";
import "../deps/@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";

import "../interfaces/badger/IController.sol";


import {
    BaseStrategy
} from "../deps/BaseStrategy.sol";

contract MyStrategy is BaseStrategy {
    using SafeERC20Upgradeable for IERC20Upgradeable;
    using AddressUpgradeable for address;
    using SafeMathUpgradeable for uint256;

    // address public want // Inherited from BaseStrategy, the token the strategy wants, swaps into and tries to grow
    address public lpComponent; // Token we provide liquidity with
    address public reward; // Token we farm and swap to want / lpComponent

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
        // IERC20Upgradeable(want).safeApprove(gauge, type(uint256).max);
    }

    /// ===== View Functions =====

    // @dev Specify the name of the strategy
    function getName() external override pure returns (string memory) {
        return "StrategyName";
    }

    // @dev Specify the version of the Strategy, for upgrades
    function version() external pure returns (string memory) {
        return "1.0";
    }

    /// @dev Balance of want currently held in strategy positions
    function balanceOfPool() public override view returns (uint256) {
        return 0;
    }
    
    /// @dev Returns true if this strategy requires tending
    function isTendable() public override view returns (bool) {
        return true;
    }

    // @dev These are the tokens that cannot be moved except by the vault
    function getProtectedTokens() public override view returns (address[] memory) {
        address[] memory protectedTokens = new address[](3);
        protectedTokens[0] = want;
        protectedTokens[1] = lpComponent;
        protectedTokens[2] = reward;
        return protectedTokens;
    }

    /// ===== Permissioned Actions: Governance =====
    /// @notice Delete if you don't need!
    function setKeepReward(uint256 _setKeepReward) external {
        _onlyGovernance();
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
    }

    /// @dev utility function to withdraw everything for migration
    function _withdrawAll() internal override {
    }
    /// @dev withdraw the specified amount of want, liquidate from lpComponent to want, paying off any necessary debt for the conversion
    function _withdrawSome(uint256 _amount) internal override returns (uint256) {

        return _amount;
    }

    /// @dev Harvest from strategy mechanics, realizing increase in underlying position
    function harvest() external whenNotPaused returns (uint256 harvested) {
        _onlyAuthorizedActors();


        uint256 _before = IERC20Upgradeable(want).balanceOf(address(this));

        // Write your code here 


        uint256 earned = IERC20Upgradeable(want).balanceOf(address(this)).sub(_before);

        /// @notice Keep this in so you get paid!
        (uint256 governancePerformanceFee, uint256 strategistPerformanceFee) = _processPerformanceFees(earned);

        /// @dev Harvest event that every strategy MUST have, see BaseStrategy
        emit Harvest(earned, block.number);

        return earned;
    }

    // Alternative Harvest with Price received from harvester, used to avoid exessive front-running
    function harvest(uint256 price) external whenNotPaused returns (uint256 harvested) {

    }

    /// @dev Rebalance, Compound or Pay off debt here
    function tend() external whenNotPaused {
        _onlyAuthorizedActors();
    }


    /// ===== Internal Helper Functions =====
    
    /// @dev used to manage the governance and strategist fee, make sure to use it to get paid!
    function _processPerformanceFees(uint256 _amount) internal returns (uint256 governancePerformanceFee, uint256 strategistPerformanceFee) {
        governancePerformanceFee = _processFee(want, _amount, performanceFeeGovernance, IController(controller).rewards());

        strategistPerformanceFee = _processFee(want, _amount, performanceFeeStrategist, strategist);
    }
}
