import brownie
import constants
import constants_bsc
import random
from brownie import network
from brownie import chain


def data():
    if network.show_active() == "hardhat-arbitrum-fork":
        constant = constants
    else:
        constant = constants_bsc
    return constant

def test_staking_mcb(deployer, mcbStaking, stakingOwner, mcb, test_strategy):
    constant = data()
    mcb_before = mcb.balanceOf(test_strategy)
    assert mcb_before ==0
    test_strategy.setMcbStaking(mcbStaking, {"from": deployer})
    test_strategy.setLmClaimerAndMcb(constant.CLAIMER_CONTRACT, mcb)
    mcb.transfer(test_strategy, 5000e18, {"from": deployer})
    test_strategy.stake({"from": deployer})
    assert mcb.balanceOf(test_strategy) == 0
    assert mcbStaking.balanceOf(test_strategy) == 5000e18
    chain.sleep(8_640_000)
    chain.mine(1)
    test_strategy.withdrawMCB({"from": deployer})
    assert mcb.balanceOf(test_strategy) == 5000e18
    assert mcbStaking.balanceOf(test_strategy) == 0




