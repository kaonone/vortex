import brownie
import constants
import constants_bsc
import random
from brownie import network
import math


def data():
    if network.show_active() == "hardhat-arbitrum-fork":
        constant = constants
    else:
        constant = constants_bsc
    return constant


def test_open_perp_position(test_strategy, deployer, accounts, governance, token):
    constant = data()
    assert token.balanceOf(test_strategy) == 0
    token.approve(test_strategy, constant.DEPOSIT_AMOUNT, {"from": deployer})
    tx = test_strategy.openPerpPosition(constant.DEPOSIT_AMOUNT, {"from": deployer})
    assert "PerpPositionOpened" in tx.events
    assert tx.events["PerpPositionOpened"]["collateral"] == constant.DEPOSIT_AMOUNT
    assert (
        tx.events["PerpPositionOpened"]["perpPositions"]
        == test_strategy.getMarginPositions()
    )
    assert tx.events["PerpPositionOpened"]["perpetualIndex"] == constant.PERP_INDEX


def test_close_perp_position(test_strategy, deployer, accounts, governance, token):
    constant = data()
    assert token.balanceOf(test_strategy) == 0
    token.approve(test_strategy, constant.DEPOSIT_AMOUNT, {"from": deployer})
    test_strategy.openPerpPosition(constant.DEPOSIT_AMOUNT, {"from": deployer})
    tx = test_strategy.closePerpPosition(constant.DEPOSIT_AMOUNT, {"from": deployer})
    assert "PerpPositionClosed" in tx.events
    assert tx.events["PerpPositionClosed"]["collateral"] == constant.DEPOSIT_AMOUNT
    assert (
        abs(
            tx.events["PerpPositionClosed"]["collateral"]
            - test_strategy.getMarginCash() / 1e12
        )
        <= constant.ACCURACY
    )
    assert tx.events["PerpPositionClosed"]["perpetualIndex"] == constant.PERP_INDEX
    assert test_strategy.getMarginPositions() == 0


def test_calculate_split(test_strategy, deployer, token):
    constant = data()
    token.approve(test_strategy, constant.DEPOSIT_AMOUNT, {"from": deployer})
    with brownie.reverts("_calculateSplit: _amount is 0"):
        test_strategy.calculateSplit(0, {"from": deployer})
    tx = test_strategy.calculateSplit(constant.DEPOSIT_AMOUNT, {"from": deployer})
    short, long_pos, buffer = tx.return_value
    assert buffer == constant.DEPOSIT_AMOUNT * (constant.BUFFER / 1000000)
    assert short == (constant.DEPOSIT_AMOUNT - buffer) / 2
    assert long_pos > 0


def test_deposit_to_margin_account(test_strategy, deployer, token):
    constant = data()
    token.approve(test_strategy, constant.DEPOSIT_AMOUNT, {"from": deployer})
    tx = test_strategy.depositToMarginAccount(constant.DEPOSIT_AMOUNT)
    assert "DepositToMarginAccount" in tx.events
    assert (
        tx.events["DepositToMarginAccount"]["amount"]
        == constant.DEPOSIT_AMOUNT
        == math.ceil(test_strategy.getMarginCash() / constant.DECIMAL_SHIFT)
    )
    assert tx.events["DepositToMarginAccount"]["perpetualIndex"] == constant.PERP_INDEX
    assert token.balanceOf(test_strategy) == 0
    assert test_strategy.getMarginCash() == constant.DEPOSIT_AMOUNT * 1e12
