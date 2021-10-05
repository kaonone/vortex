import brownie
import constants
import random


def test_harvest_withdraw(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    print(test_strategy_deposited.getMarginAccount())
    test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    print(margin_account)
    assert token.balanceOf(vault_deposited) == 0
    assert token.balanceOf(test_strategy_deposited) == 0
    assert test_strategy_deposited.getMarginCash() - full_deposit <= constants.ACCURACY
    assert oracle.priceTWAPLong({"from": deployer}).return_value[0] * margin_account[1] - ((full_deposit - (full_deposit * constants.BUFFER/10000))/2) <= constants.ACCURACY
    assert margin_account[1] +  long.balanceOf(test_strategy_deposited) <= constants.ACCURACY_MC    
    for n, user in enumerate(users):
        print(n)
        vault_deposited.withdraw(vault_deposited.balanceOf(user), user, {"from": user})
        print(test_strategy_deposited.getMarginAccount())
        print(vault_deposited.balanceOf(user))


def test_harvest(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    print(test_strategy_deposited.getMarginAccount())
    tx = test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    print(margin_account)
    assert token.balanceOf(vault_deposited) == 0
    assert token.balanceOf(test_strategy_deposited) == 0
    assert test_strategy_deposited.getMarginCash() - full_deposit <= constants.ACCURACY
    assert oracle.priceTWAPLong({"from": deployer}).return_value[0] * margin_account[1] - ((full_deposit - (full_deposit * constants.BUFFER/10000))/2) <= constants.ACCURACY
    assert margin_account[1] +  long.balanceOf(test_strategy_deposited) <= constants.ACCURACY_MC


def test_harvest_unwind(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    print(test_strategy_deposited.getMarginAccount())
    tx = test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    print(margin_account)
    assert token.balanceOf(vault_deposited) == 0
    assert token.balanceOf(test_strategy_deposited) == 0
    assert test_strategy_deposited.getMarginCash() - full_deposit <= constants.ACCURACY
    assert oracle.priceTWAPLong({"from": deployer}).return_value[0] * margin_account[1] - ((full_deposit - (full_deposit * constants.BUFFER/10000))/2) <= constants.ACCURACY
    assert margin_account[1] +  long.balanceOf(test_strategy_deposited) <= constants.ACCURACY_MC
    tx = test_strategy_deposited.unwind({"from": deployer})
    assert "StrategyUnwind" in tx.events
    print(margin_account)
    print(token.balanceOf(test_strategy_deposited))


def test_harvest_emergency_exit(governance, oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    print(test_strategy_deposited.getMarginAccount())
    tx = test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    print(margin_account)
    assert token.balanceOf(vault_deposited) == 0
    assert token.balanceOf(test_strategy_deposited) == 0
    assert test_strategy_deposited.getMarginCash() - full_deposit <= constants.ACCURACY
    assert oracle.priceTWAPLong({"from": deployer}).return_value[0] * margin_account[1] - ((full_deposit - (full_deposit * constants.BUFFER/10000))/2) <= constants.ACCURACY
    assert margin_account[1] +  long.balanceOf(test_strategy_deposited) <= constants.ACCURACY_MC
    tx = test_strategy_deposited.emergencyExit({"from": governance})
    assert "EmergencyExit" in tx.events
    print(margin_account)
    print(token.balanceOf(test_strategy_deposited))


