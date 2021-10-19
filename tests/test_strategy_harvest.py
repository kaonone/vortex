import brownie
import constants
import random

def test_harvest_unwind(
    oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long, mcLiquidityPool
):
    test_strategy_deposited.harvest({"from": deployer})
    test_strategy_deposited.unwind({"from": deployer})
    # assert "StrategyUnwind" in tx.events
    # assert test_strategy_deposited.isUnwind() == True
    # assert tx.events["StrategyUnwind"]["positionSize"] == token.balanceOf(
    #     test_strategy_deposited
    # )
    # assert test_strategy_deposited.positions()["perpContracts"] == 0
    # assert test_strategy_deposited.positions()["margin"] == 0
    tx = test_strategy_deposited.harvest({"from": deployer})
    brownie.chain.sleep(1000000)
    mcLiquidityPool.forceToSyncState({"from": deployer})
    tx = test_strategy_deposited.harvest({"from": deployer})

    
def test_harvest_increase_buffer(
    deployer,
    test_strategy_deposited,
    long,
):
    new_buffer = 500000
    test_strategy_deposited.harvest({"from": deployer})
    margin_before = test_strategy_deposited.getMargin()
    perps_before = test_strategy_deposited.getMarginPositions()
    long_before = long.balanceOf(test_strategy_deposited)
    tx = test_strategy_deposited.adjustBuffer(new_buffer, {"from": deployer})
    print(test_strategy_deposited.getMarginAccount())
    print(long.balanceOf(test_strategy_deposited))
    assert test_strategy_deposited.buffer() == new_buffer
    assert "BufferAdjusted" in tx.events
    assert tx.events["BufferAdjusted"]["oldMargin"] == margin_before
    assert (
        tx.events["BufferAdjusted"]["newMargin"]
        == test_strategy_deposited.getMargin()
        == test_strategy_deposited.positions()["margin"]
    )
    assert tx.events["BufferAdjusted"]["oldPerpContracts"] == perps_before
    assert (
        tx.events["BufferAdjusted"]["newPerpContracts"]
        == test_strategy_deposited.getMarginPositions()
        == test_strategy_deposited.positions()["perpContracts"]
    )
    assert tx.events["BufferAdjusted"]["oldLong"] == long_before
    assert tx.events["BufferAdjusted"]["newLong"] == long.balanceOf(
        test_strategy_deposited
    )


def test_harvest_decrease_buffer(
    deployer,
    test_strategy_deposited,
    long,
):
    new_buffer = 100000
    test_strategy_deposited.harvest({"from": deployer})
    margin_before = test_strategy_deposited.getMargin()
    perps_before = test_strategy_deposited.getMarginPositions()
    long_before = long.balanceOf(test_strategy_deposited)

    tx = test_strategy_deposited.adjustBuffer(new_buffer, {"from": deployer})
    print(test_strategy_deposited.getMarginAccount())
    print(long.balanceOf(test_strategy_deposited))
    assert test_strategy_deposited.buffer() == new_buffer
    assert "BufferAdjusted" in tx.events
    assert tx.events["BufferAdjusted"]["oldMargin"] == margin_before
    assert (
        tx.events["BufferAdjusted"]["newMargin"]
        == test_strategy_deposited.getMargin()
        == test_strategy_deposited.positions()["margin"]
    )
    assert tx.events["BufferAdjusted"]["oldPerpContracts"] == perps_before
    assert (
        tx.events["BufferAdjusted"]["newPerpContracts"]
        == test_strategy_deposited.getMarginPositions()
        == test_strategy_deposited.positions()["perpContracts"]
    )
    assert tx.events["BufferAdjusted"]["oldLong"] == long_before
    assert tx.events["BufferAdjusted"]["newLong"] == long.balanceOf(
        test_strategy_deposited
    )


def test_harvest(
    oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long
):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    tx = test_strategy_deposited.harvest({"from": deployer})
    margin_account = test_strategy_deposited.getMarginAccount()
    price = oracle.priceTWAPLong({"from": deployer}).return_value[0]
    assert token.balanceOf(vault_deposited) == 0
    assert token.balanceOf(test_strategy_deposited) == 0
    assert "Harvest" in tx.events
    assert tx.events["Harvest"]["longPosition"] == long.balanceOf(
        test_strategy_deposited
    )
    assert (
        tx.events["Harvest"]["perpContracts"]
        == test_strategy_deposited.getMarginPositions()
    )
    assert tx.events["Harvest"]["margin"] == test_strategy_deposited.getMargin()
    assert vault_deposited.totalLent() == full_deposit / constants.DECIMAL_SHIFT
    assert (
        abs(margin_account[1] / price + long.balanceOf(test_strategy_deposited) / price)
        <= constants.ACCURACY_USDC
    )
    assert (
        tx.events["Harvest"]["perpContracts"]
        == test_strategy_deposited.positions()["perpContracts"]
    )
    assert (
        test_strategy_deposited.positions()["margin"]
        == test_strategy_deposited.getMargin()
    )


def test_harvest_deposit_withdraw(
    oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long
):
    full_deposit = constants.DEPOSIT_AMOUNT * len(users) * constants.DECIMAL_SHIFT
    tx = test_strategy_deposited.harvest({"from": deployer})
    token.approve(vault_deposited, constants.DEPOSIT_AMOUNT, {"from": users[-1]})
    vault_deposited.deposit(constants.DEPOSIT_AMOUNT, users[-1], {"from": users[-1]})
    for n, user in enumerate(users):
        bal_before = token.balanceOf(user)
        to_burn = vault_deposited.balanceOf(user)
        tx = vault_deposited.withdraw(to_burn, user, {"from": user})
        assert vault_deposited.balanceOf(user) == 0
        assert token.balanceOf(user) > bal_before
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == (
            token.balanceOf(user) - bal_before
        )
        assert tx.events["Withdraw"]["shares"] == to_burn
        assert (
            test_strategy_deposited.positions()["perpContracts"]
            == test_strategy_deposited.getMarginPositions()
        )
        assert (
            test_strategy_deposited.positions()["margin"]
            == test_strategy_deposited.getMargin()
        )

def whale_buy_long(deployer, token, mcLiquidityPool, price):
    if mcLiquidityPool.getMarginAccount(0, deployer)[0] == 0:
        token.approve(mcLiquidityPool, token.balanceOf(deployer), {"from": deployer})
        mcLiquidityPool.setTargetLeverage(0, deployer, 1e18, {"from": deployer})
        mcLiquidityPool.deposit(
            0, deployer, (token.balanceOf(deployer) * 1e12 - 1), {"from": deployer}
        )
    mcLiquidityPool.trade(
        0,
        deployer,
        ((mcLiquidityPool.getMarginAccount(0, deployer)[3] / 100) * 1e18) / price,
        price,
        brownie.chain.time() + 10000,
        deployer,
        0x40000000,
        {"from": deployer},
    )


def whale_buy_short(deployer, token, mcLiquidityPool, price):
    if mcLiquidityPool.getMarginAccount(0, deployer)[0] == 0:
        token.approve(mcLiquidityPool, token.balanceOf(deployer), {"from": deployer})
        mcLiquidityPool.setTargetLeverage(0, deployer, 1e18, {"from": deployer})
        mcLiquidityPool.deposit(
            0, deployer, (token.balanceOf(deployer) * 1e12 - 1), {"from": deployer}
        )
    mcLiquidityPool.trade(
        0,
        deployer,
        -((mcLiquidityPool.getMarginAccount(0, deployer)[3] / 100) * 1e18) / price,
        price,
        brownie.chain.time() + 10000,
        deployer,
        0x40000000,
        {"from": deployer},
    )

def test_yield_harvest(
    oracle,
    vault_deposited,
    users,
    deployer,
    test_strategy_deposited,
    token,
    long,
    mcLiquidityPool,
):

    test_strategy_deposited.harvest({"from": deployer})
    price = oracle.priceTWAPLong({"from": deployer}).return_value[0]
    whale_buy_long(
        deployer, 
        token, 
        mcLiquidityPool, 
        price
    )
    
    for n in range(100):

        brownie.chain.sleep(28801)
        before_margin = test_strategy_deposited.getMargin()
        before_lent = vault_deposited.totalLent()
        mcLiquidityPool.forceToSyncState({"from": deployer})
        bal = test_strategy_deposited.getMargin() - before_margin
        pps_before = vault_deposited.pricePerShare()
        dep_bal_before = vault_deposited.balanceOf(deployer)
        tx = test_strategy_deposited.harvest({"from": deployer})
        print(test_strategy_deposited.getMarginAccount())
        assert tx.events["Harvest"]["longPosition"] == long.balanceOf(
            test_strategy_deposited
        )
        assert (
            tx.events["Harvest"]["perpContracts"]
            == test_strategy_deposited.getMarginPositions()
        )
        assert tx.events["Harvest"]["margin"] == test_strategy_deposited.getMargin()
        assert vault_deposited.totalLent() > before_lent
        assert (
            abs(
                test_strategy_deposited.getMarginPositions()
                + long.balanceOf(test_strategy_deposited)
            )
            <= constants.ACCURACY_MC
        )
        assert (
            tx.events["Harvest"]["perpContracts"]
            == test_strategy_deposited.positions()["perpContracts"]
        )
        assert (
            test_strategy_deposited.positions()["margin"]
            == test_strategy_deposited.getMargin()
        )
        print(vault_deposited.totalLent())
        print(vault_deposited.balanceOf(deployer))
        assert vault_deposited.balanceOf(deployer) > dep_bal_before
        assert vault_deposited.pricePerShare() > pps_before


def test_loss_harvest(
    oracle,
    vault_deposited,
    users,
    deployer,
    test_strategy_deposited,
    token,
    long,
    mcLiquidityPool,
):

    test_strategy_deposited.harvest({"from": deployer})
    price = oracle.priceTWAPLong({"from": deployer}).return_value[0]
    whale_buy_short(
        deployer, 
        token, 
        mcLiquidityPool, 
        price
    )
    
    for n in range(100):

        brownie.chain.sleep(28801)
        before_margin = test_strategy_deposited.getMargin()
        before_lent = vault_deposited.totalLent()
        mcLiquidityPool.forceToSyncState({"from": deployer})
        bal = test_strategy_deposited.getMargin() - before_margin
        pps_before = vault_deposited.pricePerShare()
        dep_bal_before = vault_deposited.balanceOf(deployer)
        tx = test_strategy_deposited.harvest({"from": deployer})
        print(test_strategy_deposited.getMarginAccount())
        assert tx.events["Harvest"]["longPosition"] == long.balanceOf(
            test_strategy_deposited
        )
        assert (
            tx.events["Harvest"]["perpContracts"]
            == test_strategy_deposited.getMarginPositions()
        )
        assert tx.events["Harvest"]["margin"] == test_strategy_deposited.getMargin()
        assert vault_deposited.totalLent() <= before_lent
        assert (
            abs(
                test_strategy_deposited.getMarginPositions()
                + long.balanceOf(test_strategy_deposited)
            )
            <= constants.ACCURACY_MC
        )
        assert (
            tx.events["Harvest"]["perpContracts"]
            == test_strategy_deposited.positions()["perpContracts"]
        )
        assert (
            test_strategy_deposited.positions()["margin"]
            == test_strategy_deposited.getMargin()
        )
        print(vault_deposited.totalLent())
        print(vault_deposited.balanceOf(deployer))
        assert vault_deposited.balanceOf(deployer) == dep_bal_before
        assert vault_deposited.pricePerShare() <= pps_before
    

def test_harvest_withdraw_all(
    oracle, vault, users, deployer, test_strategy, token, long
):
    user = users[0]
    token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
    vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
    test_strategy.harvest({"from": deployer})
    bal_before = token.balanceOf(user)
    to_burn = vault.balanceOf(user)
    tx = vault.withdraw(to_burn, user, {"from": user})
    assert token.balanceOf(user) - bal_before <= constants.DEPOSIT_AMOUNT
    assert vault.totalLent() == 0
    assert long.balanceOf(test_strategy) == 0
    assert "Withdraw" in tx.events
    assert tx.events["Withdraw"]["user"] == user
    assert tx.events["Withdraw"]["withdrawal"] == (token.balanceOf(user) - bal_before)
    assert tx.events["Withdraw"]["shares"] == to_burn
    assert test_strategy.positions()["perpContracts"] == 0
    assert test_strategy.positions()["margin"] == 0


def test_harvest_withdraw(
    oracle, vault_deposited, users, deployer, test_strategy_deposited, token, long
):
    test_strategy_deposited.harvest({"from": deployer})
    for n, user in enumerate(users):
        bal_before = token.balanceOf(user)
        to_burn = vault_deposited.balanceOf(user)
        tx = vault_deposited.withdraw(to_burn, user, {"from": user})
        assert vault_deposited.balanceOf(user) == 0
        assert token.balanceOf(user) > bal_before
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == (
            token.balanceOf(user) - bal_before
        )
        assert tx.events["Withdraw"]["shares"] == to_burn
        assert (
            test_strategy_deposited.positions()["perpContracts"]
            == test_strategy_deposited.getMarginPositions()
        )
        assert (
            test_strategy_deposited.positions()["margin"]
            == test_strategy_deposited.getMargin()
        )
    assert vault_deposited.totalLent() == 0
    assert test_strategy_deposited.getMarginPositions() == 0
    assert long.balanceOf(test_strategy_deposited) == 0
    assert test_strategy_deposited.positions()["perpContracts"] == 0
    assert test_strategy_deposited.positions()["margin"] == 0


def test_yield_harvest_withdraw(
    oracle,
    vault_deposited,
    users,
    deployer,
    test_strategy_deposited,
    token,
    long,
    mcLiquidityPool,
):
    test_strategy_deposited.harvest({"from": deployer})
    price = oracle.priceTWAPLong({"from": deployer}).return_value[0]
    whale_buy_long(
        deployer, 
        token, 
        mcLiquidityPool, 
        price
    )
    brownie.chain.sleep(1000000)
    mcLiquidityPool.forceToSyncState({"from": deployer})
    test_strategy_deposited.harvest({"from": deployer})
    for n, user in enumerate(users):

        bal_before = token.balanceOf(user)
        to_burn = vault_deposited.balanceOf(user)
        
        vault_deposited.withdraw(
            vault_deposited.balanceOf(user), user, {"from": user}
        )
        # assert vault_deposited.balanceOf(user) == 0
        # assert token.balanceOf(user) > bal_before
        # assert "Withdraw" in tx.events
        # assert tx.events["Withdraw"]["user"] == user
        # assert tx.events["Withdraw"]["withdrawal"] == (
        #     token.balanceOf(user) - bal_before
        # )
        # assert tx.events["Withdraw"]["shares"] == to_burn
    tx = vault_deposited.withdraw(vault_deposited.balanceOf(deployer), deployer, {"from": deployer})    





def test_harvest_emergency_exit(
    governance,
    oracle,
    vault_deposited,
    users,
    deployer,
    test_strategy_deposited,
    token,
    long,
):
    tx = test_strategy_deposited.harvest({"from": deployer})
    gov_bal = token.balanceOf(governance)
    tx = test_strategy_deposited.emergencyExit({"from": governance})
    assert "EmergencyExit" in tx.events
    assert test_strategy_deposited.isUnwind() == True
    assert (
        token.balanceOf(governance)
        == tx.events["EmergencyExit"]["positionSize"] + gov_bal
    )
