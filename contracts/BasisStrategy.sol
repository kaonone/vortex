pragma solidity 0.8.4;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import "@openzeppelin/contracts/access/Ownable.sol";

import "../interfaces/IMCLP.sol";

contract BasisStrategy is
    Pausable,
    Ownable,
    ReentrancyGuard
{
    using SafeERC20 for IERC20;

    IMCLP public mcLiquidityPool;

    function setLiquidityPool(address _newLiquidityPool) external onlyOwner {
        mcLiquidityPool = IMCLP(_newLiquidityPool);
    }

    function harvest() external onlyOwner{
        uint256 bonus = _determineFee();
        _openPerpPosition(bonus);
    }

    function _determineFee() internal returns (uint256){
        return 0;
    }

    function unwind() external {}

    function tend() external {}

    function _openPerpPosition(uint256 _fee) internal {

    }

    function _closePerpPosition() external {}

    function emergencyExit() external onlyOwner {}

    function withdraw() external {}

    function _calculateSplit() internal view returns (uint256, uint256){}
}
