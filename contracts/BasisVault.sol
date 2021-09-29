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

        shares = _issueShares(_amount, _recipient);
        // transfer want to the vault
        want.safeTransferFrom(msg.sender, address(this), _amount);

        emit Deposit(_recipient, _amount, shares);
    }

    function withdraw() external {
    }

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

    /*******
     GETTERS
     *******/
    function totalAssets() public view returns (uint256){
        return want.balanceOf(address(this)) + totalLent;
    }

}
