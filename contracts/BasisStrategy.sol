// SPDX-License-Identifier: AGPL V3.0
pragma solidity 0.8.4;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

import "../interfaces/IMCLP.sol";
import "../interfaces/IBasisVault.sol";

/**
 * @title  BasisStrategy
 * @author akropolis.io
 * @notice A strategy used to perform basis trading using funds from a BasisVault
 */
contract BasisStrategy is Pausable, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // MCDEX Liquidity and Perpetual Pool interface address
    IMCLP public mcLiquidityPool;
    // Uniswap v3 pair pool interface address
    IUniswapV3Pool public pool;
    // Uniswap v3 router interface address
    ISwapRouter public immutable router;
    // Basis Vault interface address
    IBasisVault public vault;

    // address of the want (short collateral) of the strategy
    address public want;
    // address of the long asset of the strategy
    address public long;

    // margin buffer of the strategy, between 0 and 10_000
    uint256 public buffer;
    // max bips
    uint256 public MAX_BPS = 10_000;

    /**
     * @param _long            address of the long asset of the strategy
     * @param _pool            Uniswap v3 pair pool address
     * @param _vault           Basis Vault address
     * @param _router          Uniswap v3 router address
     * @param _mcLiquidityPool MCDEX Liquidity and Perpetual Pool address
     */
    constructor(
        address _long,
        address _pool,
        address _vault,
        address _router,
        address _mcLiquidityPool
    ) {
        require(_long != address(0), "!_long");
        require(_pool != address(0), "!_pool");
        require(_vault != address(0), "!_vault");
        require(_router != address(0), "!_router");
        require(_mcLiquidityPool != address(0), "!_mcLiquidityPool");
        long = _long;
        pool = IUniswapV3Pool(_pool);
        vault = IBasisVault(_vault);
        router = ISwapRouter(_router);
        mcLiquidityPool = IMCLP(_mcLiquidityPool);
        want = address(vault.want());
    }

    /***********
     * SETTERS
     ************/

    /**
     * @notice  setter for the mcdex liquidity pool
     * @param   _mcLiquidityPool MCDEX Liquidity and Perpetual Pool address
     * @dev     only callable by owner
     */
    function setLiquidityPool(address _mcLiquidityPool) external onlyOwner {
        mcLiquidityPool = IMCLP(_mcLiquidityPool);
    }

    /**
     * @notice  setter for the uniswap pair pool
     * @param   _pool Uniswap v3 pair pool address
     * @dev     only callable by owner
     */
    function setUniswapPool(address _pool) external onlyOwner {
        pool = IUniswapV3Pool(_pool);
    }

    /**
     * @notice  setter for the basis vault
     * @param   _vault Basis Vault address
     * @dev     only callable by owner
     */
    function setBasisVault(address _vault) external onlyOwner {
        vault = IBasisVault(_vault);
    }

    /**
     * @notice  setter for buffer
     * @param   _buffer Basis strategy margin buffer
     * @dev     only callable by owner
     */
    function setBuffer(uint256 _buffer) external onlyOwner {
        require(_buffer < 10_000, "!_buffer");
        buffer = _buffer;
    }

    /**********************
     * EXTERNAL FUNCTIONS
     ***********************/

    function harvest() external onlyOwner {
        uint256 bonus = _determineFee();
        vault.update(bonus);
        _calculateSplit(bonus);
        _openPerpPosition(bonus);
    }

    function unwind() external onlyOwner {}

    function tend() external {}

    function emergencyExit() external onlyOwner {}

    function withdraw() external {}

    /**********************
     * INTERNAL FUNCTIONS
     ***********************/
    function _openPerpPosition(uint256 _fee) internal {}

    function _determineFee() internal returns (uint256) {
        return 0;
    }

    function _closePerpPosition() external {}

    /**
     * @notice  split an amount of assets into three:
     *          the short position which represents the short perpetual position
     *          the long position which represents the long spot position
     *          the buffer position which represents the funds to be left idle in the margin account
     * @param   _amount the amount to be split in want
     * @return  shortPosition  the size of the short perpetual position in want
     * @return  longPosition   the size of the long spot position in long
     * @return  bufferPosition the size of the buffer position in want
     */
    function _calculateSplit(uint256 _amount)
        internal
        returns (
            uint256 shortPosition,
            uint256 longPosition,
            uint256 bufferPosition
        )
    {
        require(_amount > 0, "_calculateSplit: _amount is 0");
        // remove the buffer from the amount
        bufferPosition = (_amount * buffer) / MAX_BPS;
        _amount -= bufferPosition;
        // determine the longPosition in want then convert it to long
        uint256 longPositionWant = _amount / 2;
        longPosition = _swap(longPositionWant);
        // determine the short position
        shortPosition = _amount - longPositionWant;
    }

    /**
     * @notice  swap function using uniswapv3 to facilitate the swap from want to long
     * @param   _amount the amount to be swapped in want
     * @return  amountOut the amount of long returned in exchange for the amount of want
     */
    function _swap(uint256 _amount) internal returns (uint256 amountOut) {
        // set up swap params
        uint256 deadline = block.timestamp;
        address tokenIn = want;
        address tokenOut = long;
        uint24 fee = pool.fee();
        address recipient = msg.sender;
        uint256 amountIn = _amount;
        uint256 amountOutMinimum = 0;
        uint160 sqrtPriceLimitX96 = 0;
        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter
            .ExactInputSingleParams(
                tokenIn,
                tokenOut,
                fee,
                recipient,
                deadline,
                amountIn,
                amountOutMinimum,
                sqrtPriceLimitX96
            );
        // swap optimistically via the uniswap v3 router
        amountOut = router.exactInputSingle(params);
    }
}
