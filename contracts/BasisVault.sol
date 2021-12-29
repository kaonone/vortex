pragma solidity 0.8.4;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title  BasisVault
 * @author akropolis.io
 * @notice A vault used as the management system for a basis trading protocol
 */
contract BasisVault is
    ERC20,
    Pausable,
    ReentrancyGuard,
    Ownable
{
    using SafeERC20 for IERC20;

    // token used as the vault's underlying currency
    IERC20 public want;
    // total amount of want that can be deposited in the vault
    uint256 public depositLimit;
    // total amount of want lent out to strategies to perform yielding activities
    uint256 public totalLent;

    constructor(
        address _want,
        uint256 _depositLimit
    ) ERC20("Akro Basis Vault", "akBV") {
        require(_want != address(0), "!_want");
        want = IERC20(_want);
        depositLimit = _depositLimit;
    }

    event UpdateWant(address indexed want);
    event UpdateDepositLimit(uint256 depositLimit);

    event Deposit(
        address indexed user,
        uint256 deposit,
        uint256 shares
    );
    event ProtocolFeeRecipientUpdated(
        address oldRecipient,
        address newRecipient
    );
    event ProtocolFeesIssued(uint256 wantAmount, uint256 sharesIssued);
    event WhitelistStatusChanged(bool _isWhitelistActive);
    event IndividualWhitelistCapChanged(uint256 oldState, uint256 newState);

    /***********
     * SETTERS *
     ***********/

    /**
     * @notice  set the whitelist status
     * @param   _isWhitelistActive bool for the whitelist status
     * @dev     only callable by owner
     */
    function setWhitelistActive(bool _isWhitelistActive) external onlyOwner {
        isWhitelistActive = _isWhitelistActive;
        emit WhitelistStatusChanged(_isWhitelistActive);
    }

    /**
     * @notice  set the size of the individual cap in the whitelist
     * @param   _individualWhitelistCap uint256 for setting the individual cap during the whitelist period
     * @dev     only callable by owner
     */
    function setIndividualWhitelistCap(uint256 _individualWhitelistCap) external onlyOwner {
        emit IndividualWhitelistCapChanged(individualWhitelistCap, _individualWhitelistCap);
        individualWhitelistCap = _individualWhitelistCap;
    }

    /**
     * @notice  set the want for the vault
     * @param   _want address of the token to change to
     * @dev     only callable by owner
     */
    function addToWhitelist(address[] calldata whitelist) external onlyOwner {
        for(uint i=0; i < whitelist.length; i++) {
            isWhitelisted[whitelist[i]] = true;
        }
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
     * @notice  deposit function - where users can join the vault and
     *          receive shares in the vault proportional to their ownership
     *          of the funds.
     * @param  _amount    amount of want to be deposited
     * @param  _recipient recipient of the shares as the recipient may not
     *                    be the sender
     * @return shares the amount of shares being minted to the recipient
     *                for their deposit
     */
    function deposit(
        uint256 _amount,
        address _recipient
    )
        external
        nonReentrant
        whenNotPaused
        returns (
            uint256 shares
        )
    {
        require(_amount > 0, "!_amount");
        require(_recipient != address(0), "!_recipient");
        require(totalAssets() + _amount <= depositLimit, "!depositLimit");
        // if the whitelist is active then run the whitelist logic
        if (isWhitelistActive) {
            // check if theyre whitelisted
            require(isWhitelisted[msg.sender], "!whitelisted");
            // check if they will reach their cap with this deposit
            require(whitelistedDeposit[msg.sender] + _amount <= individualWhitelistCap, "whitelist cap reached");
            // update their deposit amount
            whitelistedDeposit[msg.sender] += _amount;
        }

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
    function withdraw(uint256 _shares, uint256 _maxLoss, address _recipient)
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

    function collectProtocolFees() external {

    }

    function setProtocolFees() external {

    }

    /******************
     INTERNAL FUNCTIONS
     ******************/

    /**
     * @dev     functioning for handling share issuance during a deposit
     * @param  _amount    amount of want to be deposited
     * @param  _recipient recipient of the shares as the recipient may not
     *                    be the sender
     * @return shares the amount of shares being minted to the recipient
     *                for their deposit
     */
    function _issueShares(
        uint256 _amount,
        address _recipient
    )
    internal
    returns (
        uint256 shares
    )
    {
        if (totalSupply() > 0) {
            // if there is supply then mint according to the proportion of the pool
            require(totalAssets() > 0, "totalAssets == 0");
            shares = _amount * totalSupply() / totalAssets();
        } else {
            // if there is no supply mint 1 for 1
            shares = _amount;
        }
        _mint(_recipient, shares);
    }

    /**
     * @dev     function for handling share issuance viewing during a deposit
     * @param  _amount    amount of want to be deposited
     * @return shares the amount of shares being minted to the recipient
     *                for their deposit
     */
    function _calcSharesIssuable(uint256 _amount)
        internal
        view
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

    /**
     * @dev    function for determining the performance and management fee of the vault
     * @param  gain the profits to determine the fees from
     * @return feeAmount the fees taken from the gain
     */
    function _determineProtocolFees(uint256 gain)
        internal
        returns (uint256 feeAmount)
    {
        if (gain == 0) {
            return 0;
        }
        uint256 reward;
        uint256 duration = block.timestamp - lastUpdate;
        require(duration > 0, "!duration");
        uint256 performance = (gain * performanceFee) / MAX_BPS;
        uint256 management = ((totalLent * duration * managementFee) /
            MAX_BPS) / SECS_PER_YEAR;
        feeAmount = performance + management;
        if (feeAmount > gain) {
            feeAmount = gain;
        }
        if (feeAmount > 0) {
            reward = _issueShares(feeAmount, protocolFeeRecipient);
        }
        emit ProtocolFeesIssued(feeAmount, reward);
    }

    /***********
     * GETTERS *
     ***********/

    function expectedLoss(uint256 _shares) public view returns (uint256 loss) {
        uint256 strategyBalance = want.balanceOf(strategy);
        uint256 vaultBalance = want.balanceOf(address(this));
        uint256 amount = _calcShareValue(_shares);
        if (amount > vaultBalance) {
            uint256 needed = amount - vaultBalance;
            if (needed > strategyBalance){
                loss = needed - strategyBalance;
            } else {
                loss = 0;
            }
        }
    }

    /**
     * @notice get the total assets held in the vault including funds lent to the strategy
     * @return total assets in want available in the vault
     */
    function totalAssets() public view returns (uint256) {
        return want.balanceOf(address(this)) + totalLent;
    }

}
