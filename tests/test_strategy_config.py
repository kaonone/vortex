import brownie
import constants
import constants_bsc
import random
from brownie import network


def data():
    if network.show_active() == "hardhat-arbitrum-fork":
        constant = constants
    else:
        constant = constants_bsc
    return constant


def test_strategy_deployment(BasisStrategy, deployer, vault, governance):
    constant = data()
    strategy = BasisStrategy.deploy(
        {"from": deployer},
    )
    strategy.initialize(
        constant.LONG_ASSET,
        constant.UNI_POOL,
        vault,
        constant.MCDEX_ORACLE,
        constant.ROUTER,
        governance,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.isV2,
        {"from": deployer},
    )
    assert strategy.owner() == deployer
    assert strategy.governance() == governance
    assert strategy.referrer() == brownie.ZERO_ADDRESS
    assert strategy.mcLiquidityPool() == constant.MCLIQUIDITY
    assert strategy.pool() == constant.UNI_POOL
    assert strategy.router() == constant.ROUTER
    assert strategy.vault() == vault
    assert strategy.oracle() == constant.MCDEX_ORACLE
    assert strategy.want() == constant.USDC == vault.want()
    assert strategy.long() == constant.LONG_ASSET

    assert strategy.positions()["perpContracts"] == 0
    assert strategy.positions()["margin"] == 0
    assert strategy.perpetualIndex() == constant.PERP_INDEX
    assert strategy.buffer() == 0
    assert strategy.dust() == 1000
    assert strategy.slippageTolerance() == 0
    assert strategy.isUnwind() == False
    assert strategy.tradeMode() == 0x40000000

    strategy.setBuffer(constant.BUFFER, {"from": deployer})
    strategy.setSlippageTolerance(constant.TRADE_SLIPPAGE, {"from": deployer})

    assert strategy.buffer() == constant.BUFFER
    assert strategy.slippageTolerance() == constant.TRADE_SLIPPAGE


def test_setters(BasisStrategy, deployer, accounts, governance, vault):
    constant = data()
    strategy = BasisStrategy.deploy(
        {"from": deployer},
    )
    strategy.initialize(
        constant.LONG_ASSET,
        constant.UNI_POOL,
        vault,
        constant.MCDEX_ORACLE,
        constant.ROUTER,
        governance,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.isV2,
        {"from": deployer},
    )
    with brownie.reverts():
        strategy.setLiquidityPool(constant.UNI_POOL, {"from": accounts[9]})
    strategy.setLiquidityPool(constant.UNI_POOL, {"from": deployer})
    assert strategy.mcLiquidityPool() == constant.UNI_POOL

    with brownie.reverts():
        strategy.setUniswapPool(constant.UNI_POOL, {"from": accounts[9]})
    strategy.setUniswapPool(constant.UNI_POOL, {"from": deployer})
    assert strategy.pool() == constant.UNI_POOL

    with brownie.reverts():
        strategy.setBasisVault(constant.UNI_POOL, {"from": accounts[9]})
    strategy.setBasisVault(constant.UNI_POOL, {"from": deployer})
    assert strategy.vault() == constant.UNI_POOL

    with brownie.reverts():
        strategy.setBuffer(constant.BUFFER, {"from": accounts[9]})
    with brownie.reverts("!_buffer"):
        strategy.setBuffer(1000001, {"from": deployer})
    strategy.setBuffer(constant.BUFFER, {"from": deployer})
    assert strategy.buffer() == constant.BUFFER

    with brownie.reverts():
        strategy.setPerpetualIndex(0, {"from": accounts[9]})
    strategy.setPerpetualIndex(0, {"from": deployer})
    assert strategy.perpetualIndex() == 0

    with brownie.reverts():
        strategy.setReferrer(constant.UNI_POOL, {"from": accounts[9]})
    strategy.setReferrer(constant.UNI_POOL, {"from": deployer})
    assert strategy.referrer() == constant.UNI_POOL

    with brownie.reverts():
        strategy.setSlippageTolerance(1, {"from": accounts[9]})
    strategy.setSlippageTolerance(1, {"from": deployer})
    assert strategy.slippageTolerance() == 1

    with brownie.reverts():
        strategy.setDust(1, {"from": accounts[9]})
    strategy.setDust(1, {"from": deployer})
    assert strategy.dust() == 1

    with brownie.reverts():
        strategy.setTradeMode(0x00000000, {"from": accounts[9]})
    strategy.setTradeMode(0x00000000, {"from": deployer})
    assert strategy.tradeMode() == 0x00000000

    with brownie.reverts():
        strategy.setGovernance(constant.UNI_POOL, {"from": deployer})
    strategy.setGovernance(constant.UNI_POOL, {"from": governance})
    assert strategy.governance() == constant.UNI_POOL
