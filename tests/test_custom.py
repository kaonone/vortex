import brownie
from brownie import *
from helpers.constants import MaxUint256
from helpers.SnapshotManager import SnapshotManager
from helpers.time import days

"""
  TODO: Put your tests here to prove the strat is good!
  See test_harvest_flow, for the basic tests
  See test_strategy_permissions, for tests at the permissions level
"""


def test_my_custom_test(
    deployer, vault, sett, controller, strategy, want, settKeeper, strategyKeeper
):
    # Setup
    snap = SnapshotManager(vault, strategy, controller, "StrategySnapshot")
    depositAmount = want.balanceOf(deployer)

    # Deposit
    want.approve(sett, MaxUint256, {"from": deployer})
    snap.settDeposit(depositAmount, {"from": deployer})

    assert want.balanceOf(sett) > 0
    assert depositAmount == want.balanceOf(sett)
    assert strategy.isTendable() == False

    # Earn
    snap.settEarn({"from": settKeeper})
    # Earn automatically calls strategy's deposit
    assert strategy.balanceOfWant() == 0
    assert strategy.balanceOf() == strategy.balanceOfPool()
    assert strategy.isTendable() == False

    chain.sleep(days(60))
    chain.mine()

    # Harvest (twice just to see no errors)
    assert strategy.checkPendingReward() > 0
    print(f"Pending sushi reward: {strategy.checkPendingReward() / 1e18}")
    snap.settHarvest({"from": strategyKeeper})
    assert strategy.checkPendingReward() == 0
    assert strategy.balanceOfWant() > 0
    assert strategy.isTendable() == True

    chain.sleep(3600)
    chain.mine()
    snap.settHarvest({"from": strategyKeeper})

    # Tend (twice just to see no errors)
    snap.settTend({"from": strategyKeeper})
    assert strategy.isTendable() == False
    snap.settTend({"from": strategyKeeper})

    chain.sleep(3600)
    chain.mine()

    # Harvest
    assert strategy.checkPendingReward() > 0
    snap.settHarvest({"from": strategyKeeper})
    assert strategy.checkPendingReward() == 0
    assert strategy.balanceOfWant() > 0
    assert strategy.isTendable() == True

    # Withdraw
    snap.settWithdrawAll({"from": deployer})
    assert (
        strategy.balanceOf()
        == strategy.balanceOfPool()
        == strategy.balanceOfWant()
        == 0
    )
    assert strategy.isTendable() == False
    assert want.balanceOf(deployer) > depositAmount
