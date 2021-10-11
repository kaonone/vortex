import brownie
import constants
import random


def test_harvest(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    tx = test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    price = oracle.priceTWAPLong({"from": deployer}).return_value
    assert token.balanceOf(vault_deposited) == 0
    assert token.balanceOf(test_strategy_deposited) == 0
    assert "Harvest" in tx.events
    assert tx.events["Harvest"]["longPosition"] == long.balanceOf(test_strategy_deposited)
    assert tx.events["Harvest"]["perpContracts"] == test_strategy_deposited.getMarginPositions()
    assert tx.events["Harvest"]["availableMargin"] == test_strategy_deposited.getAvailableMargin()
    assert vault_deposited.totalLent() == full_deposit / constants.DECIMAL_SHIFT
    assert abs(margin_account[1] +  long.balanceOf(test_strategy_deposited)) <= constants.ACCURACY_MC
    assert tx.events["Harvest"]["perpContracts"] == test_strategy_deposited.positions()["perpContracts"]
    assert test_strategy_deposited.positions()["availableMargin"] == test_strategy_deposited.getAvailableMargin()

def test_yield_harvest(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long, mcLiquidityPool):
    tx = test_strategy_deposited.harvest({"from": deployer})
    brownie.chain.sleep(1000000)
    before_margin = test_strategy_deposited.getAvailableMargin()
    before_lent = vault_deposited.totalLent()
    mcLiquidityPool.forceToSyncState({"from": deployer})
    bal = test_strategy_deposited.getAvailableMargin() - before_margin
    tx = test_strategy_deposited.harvest({"from": deployer})
    assert tx.events["Harvest"]["longPosition"] == long.balanceOf(test_strategy_deposited) 
    assert tx.events["Harvest"]["perpContracts"] == test_strategy_deposited.getMarginPositions()
    assert tx.events["Harvest"]["availableMargin"] == test_strategy_deposited.getAvailableMargin()
    assert abs(vault_deposited.totalLent() - (before_lent + (bal / constants.DECIMAL_SHIFT))) <= constants.ACCURACY_USDC
    assert abs(test_strategy_deposited.getMarginPositions() +  long.balanceOf(test_strategy_deposited)) <= constants.ACCURACY_MC
    assert tx.events["Harvest"]["perpContracts"] == test_strategy_deposited.positions()["perpContracts"]
    assert test_strategy_deposited.positions()["availableMargin"] == test_strategy_deposited.getAvailableMargin() 

def test_harvest_withdraw_all(oracle, vault, users, deployer, test_strategy, token, long):
    user = users[0]
    token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
    vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
    test_strategy.harvest({"from": deployer})  
    bal_before = token.balanceOf(user)
    to_burn = vault.balanceOf(user)
    tx = vault.withdraw(to_burn, user, {"from": user})
    assert token.balanceOf(user)  - bal_before <= constants.DEPOSIT_AMOUNT
    assert vault.totalLent() == 0
    assert long.balanceOf(test_strategy) == 0
    assert "Withdraw" in tx.events
    assert tx.events["Withdraw"]["user"] == user
    assert tx.events["Withdraw"]["withdrawal"] == (token.balanceOf(user) - bal_before)
    assert tx.events["Withdraw"]["shares"] == to_burn   
    assert test_strategy.positions()["perpContracts"] == 0
    assert test_strategy.positions()["availableMargin"] == 0



def test_harvest_withdraw(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    test_strategy_deposited.harvest({"from": deployer})  
    for n, user in enumerate(users):
        bal_before = token.balanceOf(user)
        to_burn = vault_deposited.balanceOf(user)
        tx = vault_deposited.withdraw(to_burn, user, {"from": user})
        assert vault_deposited.balanceOf(user) == 0
        assert abs(token.balanceOf(user) - bal_before - constants.DEPOSIT_AMOUNT) <= 1e8
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == (token.balanceOf(user) - bal_before)
        assert tx.events["Withdraw"]["shares"] == to_burn
        assert test_strategy_deposited.positions()["perpContracts"] == test_strategy_deposited.getMarginPositions() 
        assert test_strategy_deposited.positions()["availableMargin"] == test_strategy_deposited.getAvailableMargin()
    assert vault_deposited.totalLent() == 0
    assert test_strategy_deposited.getMarginPositions() == 0
    assert long.balanceOf(test_strategy_deposited) == 0
    assert test_strategy_deposited.positions()["perpContracts"] == 0
    assert test_strategy_deposited.positions()["availableMargin"] == 0


def test_yield_harvest_withdraw(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long, mcLiquidityPool):
    test_strategy_deposited.harvest({"from": deployer})
    brownie.chain.sleep(1000000)
    mcLiquidityPool.forceToSyncState({"from": deployer})
    test_strategy_deposited.harvest({"from": deployer})
    for n, user in enumerate(users):
        bal_before = token.balanceOf(user)
        to_burn = vault_deposited.balanceOf(user)
        tx = vault_deposited.withdraw(vault_deposited.balanceOf(user), user, {"from": user})
        assert vault_deposited.balanceOf(user) == 0
        assert abs((token.balanceOf(user) - bal_before) - constants.DEPOSIT_AMOUNT) <= 1e7
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == (token.balanceOf(user) - bal_before)
        assert tx.events["Withdraw"]["shares"] == to_burn 
    assert vault_deposited.totalLent() == 0
    assert test_strategy_deposited.getMarginPositions() == 0
    assert long.balanceOf(test_strategy_deposited) == 0


def test_harvest_unwind(oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    tx = test_strategy_deposited.harvest({"from": deployer})
    tx = test_strategy_deposited.unwind({"from": deployer})
    assert "StrategyUnwind" in tx.events
    assert test_strategy_deposited.isUnwind() == True
    assert tx.events["StrategyUnwind"]["positionSize"] == token.balanceOf(test_strategy_deposited)
    assert test_strategy_deposited.positions()["perpContracts"] == 0
    assert test_strategy_deposited.positions()["availableMargin"] == 0


def test_harvest_emergency_exit(governance, oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long):
    tx = test_strategy_deposited.harvest({"from": deployer})
    gov_bal = token.balanceOf(governance)
    tx = test_strategy_deposited.emergencyExit({"from": governance})
    assert "EmergencyExit" in tx.events
    assert test_strategy_deposited.isUnwind() == True
    assert token.balanceOf(governance) == tx.events["EmergencyExit"]["positionSize"] + gov_bal



