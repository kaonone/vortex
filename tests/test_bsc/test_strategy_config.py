import brownie
import constants
import random


def test_strategy_deployment(BasisStrategy, deployer, vault, governance):
    strategy = BasisStrategy.deploy(
        constants.LONG_ASSET,
        constants.UNI_POOL,
        vault,
        constants.MCDEX_ORACLE,
        constants.ROUTER,
        governance,
        constants.MCLIQUIDITY,
        constants.PERP_INDEX,
        True,
        {"from": deployer},
    )
    assert strategy.owner() == deployer
    assert strategy.governance() == governance
    assert strategy.referrer() == brownie.ZERO_ADDRESS
    assert strategy.mcLiquidityPool() == constants.MCLIQUIDITY
    assert strategy.pool() == constants.UNI_POOL
    assert strategy.router() == constants.ROUTER
    assert strategy.vault() == vault
    assert strategy.oracle() == constants.MCDEX_ORACLE
    assert strategy.want() == constants.BUSD == vault.want()
    assert strategy.long() == constants.LONG_ASSET

    assert strategy.positions()["perpContracts"] == 0
    assert strategy.positions()["margin"] == 0
    assert strategy.perpetualIndex() == constants.PERP_INDEX
    assert strategy.buffer() == 0
    assert strategy.dust() == 1000
    assert strategy.slippageTolerance() == 0
    assert strategy.isUnwind() == False
    assert strategy.tradeMode() == 0x40000000

    strategy.setBuffer(constants.BUFFER, {"from": deployer})
    strategy.setSlippageTolerance(constants.TRADE_SLIPPAGE, {"from": deployer})

    assert strategy.buffer() == constants.BUFFER
    assert strategy.slippageTolerance() == constants.TRADE_SLIPPAGE


def test_setters(BasisStrategy, deployer, accounts, governance, vault):
    strategy = BasisStrategy.deploy(
        constants.LONG_ASSET,
        constants.UNI_POOL,
        vault,
        constants.MCDEX_ORACLE,
        constants.ROUTER,
        governance,
        constants.MCLIQUIDITY,
        constants.PERP_INDEX,
        True,
        {"from": deployer},
    )
    with brownie.reverts():
        strategy.setLiquidityPool(constants.UNI_POOL, {"from": accounts[9]})
    strategy.setLiquidityPool(constants.UNI_POOL, {"from": deployer})
    assert strategy.mcLiquidityPool() == constants.UNI_POOL

    with brownie.reverts():
        strategy.setUniswapPool(constants.UNI_POOL, {"from": accounts[9]})
    strategy.setUniswapPool(constants.UNI_POOL, {"from": deployer})
    assert strategy.pool() == constants.UNI_POOL

    with brownie.reverts():
        strategy.setBasisVault(constants.UNI_POOL, {"from": accounts[9]})
    strategy.setBasisVault(constants.UNI_POOL, {"from": deployer})
    assert strategy.vault() == constants.UNI_POOL

    with brownie.reverts():
        strategy.setBuffer(constants.BUFFER, {"from": accounts[9]})
    with brownie.reverts("!_buffer"):
        strategy.setBuffer(1000001, {"from": deployer})
    strategy.setBuffer(constants.BUFFER, {"from": deployer})
    assert strategy.buffer() == constants.BUFFER

    with brownie.reverts():
        strategy.setPerpetualIndex(0, {"from": accounts[9]})
    strategy.setPerpetualIndex(0, {"from": deployer})
    assert strategy.perpetualIndex() == 0

    with brownie.reverts():
        strategy.setReferrer(constants.UNI_POOL, {"from": accounts[9]})
    strategy.setReferrer(constants.UNI_POOL, {"from": deployer})
    assert strategy.referrer() == constants.UNI_POOL

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
        strategy.setGovernance(constants.UNI_POOL, {"from": deployer})
    strategy.setGovernance(constants.UNI_POOL, {"from": governance})
    assert strategy.governance() == constants.UNI_POOL
