import brownie
import constants
import random


def test_harvest(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    tx = test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    price = oracle.priceTWAPLong({"from": deployer})
    assert token.balanceOf(vault_deposited) == 0
    assert token.balanceOf(test_strategy_deposited) == 0
    assert "Harvest" in tx.events
    assert tx.events["Harvest"]["shortPosition"] == ((full_deposit - (full_deposit * constants.BUFFER / 10000)) /2)/constants.DECIMAL_SHIFT
    assert tx.events["Harvest"]["longPosition"] == long.balanceOf(test_strategy_deposited)
    assert tx.events["Harvest"]["perpContracts"] == test_strategy_deposited.getMarginPositions()
    assert tx.events["Harvest"]["bufferPosition"] == (full_deposit * constants.BUFFER / 10000) / constants.DECIMAL_SHIFT
    assert vault_deposited.totalLent() == full_deposit / constants.DECIMAL_SHIFT
    assert abs(margin_account[1] +  long.balanceOf(test_strategy_deposited)) <= constants.ACCURACY_MC
    assert tx.events["Harvest"]["shortPosition"] == test_strategy_deposited.positions()["shortPosition"]
    assert tx.events["Harvest"]["longPosition"] == test_strategy_deposited.positions()["longPosition"]
    assert tx.events["Harvest"]["perpContracts"] == test_strategy_deposited.positions()["perpContracts"]
    assert tx.events["Harvest"]["bufferPosition"] == test_strategy_deposited.positions()["bufferPosition"]


def test_harvest_withdraw(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    test_strategy_deposited.harvest({"from": deployer})  
    for n, user in enumerate(users):
        vault_deposited.withdraw(vault_deposited.balanceOf(user), user, {"from": user})


def test_yield_harvest(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long, mcLiquidityPool):
    test_strategy_deposited.harvest({"from": deployer})
    print(test_strategy_deposited.getMarginAccount())
    brownie.chain.sleep(10000000)
    mcLiquidityPool.forceToSyncState({"from": deployer})
    print(test_strategy_deposited.getMarginAccount())
    tx = test_strategy_deposited.harvest({"from": deployer})
    print(test_strategy_deposited.getMarginAccount())


def test_double_harvest(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long, mcLiquidityPool):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    print(test_strategy_deposited.getMarginAccount())
    tx = test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    print(margin_account)
    assert token.balanceOf(vault_deposited) == 0
    assert token.balanceOf(test_strategy_deposited) == 0
    assert oracle.priceTWAPLong({"from": deployer}).return_value[0] * margin_account[1] - ((full_deposit - (full_deposit * constants.BUFFER/10000))/2) <= constants.ACCURACY
    assert abs(margin_account[1] +  long.balanceOf(test_strategy_deposited)) <= constants.ACCURACY_MC
    print(vault_deposited.totalLent())
    print(test_strategy_deposited.getMarginAccount())
    tx = test_strategy_deposited.harvest({"from": deployer})
    print(test_strategy_deposited.getMarginAccount())
    print(vault_deposited.totalLent())


def test_harvest_unwind(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    print(test_strategy_deposited.getMarginAccount())
    tx = test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    print(margin_account)
    assert token.balanceOf(vault_deposited) == 0
    assert oracle.priceTWAPLong({"from": deployer}).return_value[0] * margin_account[1] - ((full_deposit - (full_deposit * constants.BUFFER/10000))/2) <= constants.ACCURACY
    assert abs(margin_account[1] +  long.balanceOf(test_strategy_deposited)) <= constants.ACCURACY_MC
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
    assert oracle.priceTWAPLong({"from": deployer}).return_value[0] * margin_account[1] - ((full_deposit - (full_deposit * constants.BUFFER/10000))/2) <= constants.ACCURACY
    assert abs(margin_account[1] +  long.balanceOf(test_strategy_deposited)) <= constants.ACCURACY_MC
    tx = test_strategy_deposited.emergencyExit({"from": governance})
    assert "EmergencyExit" in tx.events
    print(margin_account)
    print(token.balanceOf(test_strategy_deposited))


