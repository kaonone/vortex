// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

import "../interfaces/IStrategy.sol";

/**
 * @title  BasisVault
 * @author akropolis.io
 * @notice A vault used as the management system for a basis trading protocol
 */
contract BasisVault is ERC20, Pausable, ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;
    using Math for uint256;

    // token used as the vault's underlying currency
    IERC20 public want;
    // total amount of want that can be deposited in the vault
    uint256 public depositLimit;
    // total amount of want lent out to strategies to perform yielding activities
    uint256 public totalLent;
    // MAX_BPS
    uint256 public constant MAX_BPS = 10_000;
    // strat address
    address public strategy;
    // management fee
    uint256 public managementFee;
    // performance fee
    uint256 public performanceFee;

    // modifier to check that the caller is the strategy
    modifier onlyStrategy() {
        require(msg.sender == strategy, "!strategy");
        _;
    }

    constructor(address _want, uint256 _depositLimit) ERC20("akBV", "akBV") {
        require(_want != address(0), "!_want");
        want = IERC20(_want);
        depositLimit = _depositLimit;
    }

    /**********
     * EVENTS *
     **********/

    event UpdateWant(address indexed want);
    event UpdateStrategy(address indexed want);
    event UpdateDepositLimit(uint256 depositLimit);

    event Deposit(address indexed user, uint256 deposit, uint256 shares);
    event Withdraw(address indexed user, uint256 withdrawal, uint256 shares);
    event StrategyUpdate(uint256 profitOrLoss, bool isLoss, uint256 toDeposit);
    event ProtocolFeesChanged(
        uint256 oldManagementFee,
        uint256 newManagementFee,
        uint256 oldPerformanceFee,
        uint256 newPerformanceFee
    );

    /***********
     * SETTERS *
     ***********/

    /**
     * @notice  set the want for the vault
     * @param   _want address of the token to change to
     * @dev     only callable by owner
     */
    function setWant(address _want) external onlyOwner {
        require(_want != address(0), "!_want");
        want = IERC20(_want);
        emit UpdateWant(_want);
    }

    /**
     * @notice  set the maximum amount that can be deposited in the vault
     * @param   _depositLimit amount of want allowed to be deposited
     * @dev     only callable by owner
     */
    function setDepositLimit(uint256 _depositLimit) external onlyOwner {
        depositLimit = _depositLimit;
        emit UpdateDepositLimit(_depositLimit);
    }

    /**
     * @notice  set the strategy associated with the vault
     * @param   _strategy address of the strategy
     * @dev     only callable by owner
     */
    function setStrategy(address _strategy) external onlyOwner {
        strategy = _strategy;
        emit UpdateStrategy(_strategy);
    }

    /**********************
     * EXTERNAL FUNCTIONS *
     **********************/

    /**
     * @notice  deposit function - where users can join the vault and
     *          receive shares in the vault proportional to their ownership
     *          of the funds.
     * @param  _amount    amount of want to be deposited
     * @param  _recipient recipient of the shares as the recipient may not
     *                    be the sender
     * @return shares the amount of shares being minted to the recipient
     *                for their deposit
     */
    function deposit(uint256 _amount, address _recipient)
        external
        nonReentrant
        whenNotPaused
        returns (uint256 shares)
    {
        require(_amount > 0, "!_amount");
        require(_recipient != address(0), "!_recipient");
        require(totalAssets() + _amount <= depositLimit, "!depositLimit");

        shares = _issueShares(_amount, _recipient);
        // transfer want to the vault
        want.safeTransferFrom(msg.sender, address(this), _amount);

        emit Deposit(_recipient, _amount, shares);
    }

    /**
     * @notice  withdraw function - where users can exit their positions in a vault
     *          users provide an amount of shares that will be returned to a recipient.
     * @param  _shares    amount of shares to be redeemed
     * @param  _recipient recipient of the amount as the recipient may not
     *                    be the sender
     * @return amount the amount being withdrawn for the shares redeemed
     */
    function withdraw(uint256 _shares, address _recipient)
        external
        nonReentrant
        whenNotPaused
        returns (uint256 amount)
    {
        require(_shares > 0, "!_shares");
        require(_shares <= balanceOf(msg.sender), "insufficient balance");
        amount = _calcShareValue(_shares);
        uint256 vaultBalance = want.balanceOf(address(this));
        uint256 loss;

        // if the vault doesnt have free funds then funds should be taken from the strategy
        if (amount > vaultBalance) {
            uint256 needed = amount - vaultBalance;
            needed = Math.min(needed, totalLent);
            uint256 withdrawn;
            (loss, withdrawn) = IStrategy(strategy).withdraw(needed);
            if (loss > 0) {
                amount -= loss;
                totalLent -= loss;
            }
            totalLent -= withdrawn;
        }
        vaultBalance = want.balanceOf(address(this));

        // all assets have been withdrawn so now the vault must deal with the loss in the share calculation
        if (amount > vaultBalance) {
            amount = vaultBalance;
            _shares = _sharesForAmount(amount);
            emit Withdraw(_recipient, amount, _shares);
        }
        _burn(msg.sender, _shares);
        emit Withdraw(_recipient, amount, _shares);
        want.safeTransfer(_recipient, amount);
    }

    /**
     * @notice function to update the state of the strategy in the vault and pull any funds to be redeposited
     * @param  _amount change in the vault amount sent by the strategy
     * @param  _loss   whether the change is negative or not
     *                 be the sender
     * @return toDeposit the amount to be deposited in to the strategy on this update
     */
    function update(uint256 _amount, bool _loss)
        external
        onlyStrategy
        returns (uint256 toDeposit)
    {
        // if a loss was recorded then decrease the totalLent by the amount, otherwise increase the totalLent
        if (_loss) {
            totalLent -= _amount;
        } else {
            totalLent += _amount;
        }
        // increase the totalLent by the amount of deposits that havent yet been sent to the vault
        toDeposit = want.balanceOf(address(this));
        totalLent += toDeposit;
        emit StrategyUpdate(_amount, _loss, toDeposit);
        want.approve(strategy, toDeposit);
        want.safeTransfer(msg.sender, toDeposit);
    }

    /**
     * @notice function to set the protocol management and performance fees
     * @param  _performanceFee the fee applied for the strategies performance
     * @param  _managementFee the fee applied for the strategies management
     * @dev    only callable by the owner
     */
    function setProtocolFees(uint256 _performanceFee, uint256 _managementFee)
        external
        onlyOwner
    {
        emit ProtocolFeesChanged(
            managementFee,
            _managementFee,
            performanceFee,
            _performanceFee
        );
        performanceFee = _performanceFee;
        managementFee = _managementFee;
    }

    /**********************
     * INTERNAL FUNCTIONS *
     **********************/

    /**
     * @dev     function for handling share issuance during a deposit
     * @param  _amount    amount of want to be deposited
     * @param  _recipient recipient of the shares as the recipient may not
     *                    be the sender
     * @return shares the amount of shares being minted to the recipient
     *                for their deposit
     */
    function _issueShares(uint256 _amount, address _recipient)
        internal
        returns (uint256 shares)
    {
        if (totalSupply() > 0) {
            // if there is supply then mint according to the proportion of the pool
            require(totalAssets() > 0, "totalAssets == 0");
            shares = (_amount * totalSupply()) / totalAssets();
        } else {
            // if there is no supply mint 1 for 1
            shares = _amount;
        }
        _mint(_recipient, shares);
    }

    /**
     * @dev     function for determining the value of a share of the vault
     * @param  _shares    amount of shares to convert
     * @return the value of the inputted amount of shares in want
     */
    function _calcShareValue(uint256 _shares) internal view returns (uint256) {
        if (totalSupply() == 0) {
            return _shares;
        }
        return (_shares * totalAssets()) / totalSupply();
    }

    /**
     * @dev    function for determining the amount of shares for a specific amount
     * @param  _amount amount of want to convert to shares
     * @return the value of the inputted amount of shares in want
     */
    function _sharesForAmount(uint256 _amount) internal view returns (uint256) {
        if (totalAssets() > 0) {
            return ((_amount * totalSupply()) / totalAssets());
        } else {
            return 0;
        }
    }

    /***********
     * GETTERS *
     ***********/

    /**
     * @notice get the total assets held in the vault including funds lent to the strategy
     * @return total assets in want available in the vault
     */
    function totalAssets() public view returns (uint256) {
        return want.balanceOf(address(this)) + totalLent;
    }
}
