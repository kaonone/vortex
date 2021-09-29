import brownie
import constants
import random


def test_setters(test_strategy, deployer, accounts):
    with brownie.reverts():
        test_strategy.setLiquidityPool(constants.UNI_POOL, {"from": accounts[9]})
    test_strategy.setLiquidityPool(constants.UNI_POOL, {"from": deployer})
    assert test_strategy.mcLiquidityPool() == constants.UNI_POOL
    with brownie.reverts():
        test_strategy.setUniswapPool(constants.UNI_POOL, {"from": accounts[9]})
    test_strategy.setUniswapPool(constants.UNI_POOL, {"from": deployer})
    assert test_strategy.pool() == constants.UNI_POOL
    with brownie.reverts():
        test_strategy.setBasisVault(constants.UNI_POOL, {"from": accounts[9]})
    test_strategy.setBasisVault(constants.UNI_POOL, {"from": deployer})
    assert test_strategy.vault() == constants.UNI_POOL
    with brownie.reverts():
        test_strategy.setBuffer(constants.BUFFER, {"from": accounts[9]})
    with brownie.reverts():
        test_strategy.setBuffer(10001, {"from": accounts[9]})
    test_strategy.setBuffer(constants.BUFFER, {"from": deployer})
    assert test_strategy.buffer() == constants.BUFFER


def test_calculate_split(test_strategy, deployer, token):
    token.approve(test_strategy, constants.DEPOSIT_AMOUNT, {"from": deployer})
    tx = test_strategy.calculateSplit(constants.DEPOSIT_AMOUNT, {"from": deployer})
    print(tx.return_value)
