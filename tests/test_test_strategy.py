import brownie
import constants
import random
import math


def test_open_perp_position(test_strategy, deployer, accounts, governance, token):
    assert token.balanceOf(test_strategy) == 0
    token.approve(test_strategy, constants.DEPOSIT_AMOUNT, {"from": deployer})
    tx = test_strategy.openPerpPosition(constants.DEPOSIT_AMOUNT, {"from": deployer})
    assert "PerpPositionOpened" in tx.events
    assert tx.events["PerpPositionOpened"]["collateral"] == constants.DEPOSIT_AMOUNT
    assert (
        tx.events["PerpPositionOpened"]["perpPositions"]
        == test_strategy.getMarginPositions()
    )
    assert tx.events["PerpPositionOpened"]["perpetualIndex"] == constants.PERP_INDEX


def test_close_perp_position(test_strategy, deployer, accounts, governance, token):
    assert token.balanceOf(test_strategy) == 0
    token.approve(test_strategy, constants.DEPOSIT_AMOUNT, {"from": deployer})
    test_strategy.openPerpPosition(constants.DEPOSIT_AMOUNT, {"from": deployer})
    tx = test_strategy.closePerpPosition(constants.DEPOSIT_AMOUNT, {"from": deployer})
    assert "PerpPositionClosed" in tx.events
    assert tx.events["PerpPositionClosed"]["collateral"] == constants.DEPOSIT_AMOUNT
    assert (
        abs(
            tx.events["PerpPositionClosed"]["collateral"]
            - test_strategy.getMarginCash() / 1e12
        )
        <= constants.ACCURACY
    )
    assert tx.events["PerpPositionClosed"]["perpetualIndex"] == constants.PERP_INDEX
    assert test_strategy.getMarginPositions() == 0


def test_setters(test_strategy, deployer, accounts, governance):
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
    with brownie.reverts("!_buffer"):
        test_strategy.setBuffer(10001, {"from": deployer})
    test_strategy.setBuffer(constants.BUFFER, {"from": deployer})
    assert test_strategy.buffer() == constants.BUFFER

    with brownie.reverts():
        test_strategy.setPerpetualIndex(0, {"from": accounts[9]})
    test_strategy.setPerpetualIndex(0, {"from": deployer})
    assert test_strategy.perpetualIndex() == 0

    with brownie.reverts():
        test_strategy.setReferrer(constants.UNI_POOL, {"from": accounts[9]})
    test_strategy.setReferrer(constants.UNI_POOL, {"from": deployer})
    assert test_strategy.referrer() == constants.UNI_POOL

    with brownie.reverts():
        test_strategy.setSlippageTolerance(1, {"from": accounts[9]})
    test_strategy.setSlippageTolerance(1, {"from": deployer})
    assert test_strategy.slippageTolerance() == 1

    with brownie.reverts():
        test_strategy.setDust(1, {"from": accounts[9]})
    test_strategy.setDust(1, {"from": deployer})
    assert test_strategy.dust() == 1

    with brownie.reverts():
        test_strategy.setGovernance(constants.UNI_POOL, {"from": deployer})
    test_strategy.setGovernance(constants.UNI_POOL, {"from": governance})
    assert test_strategy.governance() == constants.UNI_POOL


def test_calculate_split(test_strategy, deployer, token):
    token.approve(test_strategy, constants.DEPOSIT_AMOUNT, {"from": deployer})
    with brownie.reverts("_calculateSplit: _amount is 0"):
        test_strategy.calculateSplit(0, {"from": deployer})
    tx = test_strategy.calculateSplit(constants.DEPOSIT_AMOUNT, {"from": deployer})
    short, long_pos, buffer = tx.return_value
    assert buffer == constants.DEPOSIT_AMOUNT * (constants.BUFFER / 10000)
    assert short == (constants.DEPOSIT_AMOUNT - buffer) / 2
    assert long_pos > 0


def test_deposit_to_margin_account(test_strategy, deployer, token):
    token.approve(test_strategy, constants.DEPOSIT_AMOUNT, {"from": deployer})
    tx = test_strategy.depositToMarginAccount(constants.DEPOSIT_AMOUNT)
    assert "DepositToMarginAccount" in tx.events
    assert (
        tx.events["DepositToMarginAccount"]["amount"]
        == constants.DEPOSIT_AMOUNT
        == math.ceil(test_strategy.getMarginCash() / constants.DECIMAL_SHIFT)
    )
    assert tx.events["DepositToMarginAccount"]["perpetualIndex"] == constants.PERP_INDEX
    assert token.balanceOf(test_strategy) == 0
    assert test_strategy.getMarginCash() == constants.DEPOSIT_AMOUNT * 1e12
