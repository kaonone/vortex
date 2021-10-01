import brownie
import constants
import random


def test_harvest(vault_deposited, users, deployer, test_strategy_deposited):
    print(test_strategy_deposited.getMarginAccount())
    tx = test_strategy_deposited.harvest({"from": deployer})
    print(test_strategy_deposited.getMarginAccount())

