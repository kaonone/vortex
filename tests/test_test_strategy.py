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


def test_calculate_split(test_strategy, deployer, token):
    token.approve(test_strategy, constants.DEPOSIT_AMOUNT, {"from": deployer})
    with brownie.reverts("_calculateSplit: _amount is 0"):
        test_strategy.calculateSplit(0, {"from": deployer})
    tx = test_strategy.calculateSplit(constants.DEPOSIT_AMOUNT, {"from": deployer})
    short, long_pos, buffer = tx.return_value
    assert buffer == constants.DEPOSIT_AMOUNT * (constants.BUFFER / 1000000)
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
