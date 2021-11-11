import brownie
import constants
import constants_bsc
import random
from brownie import network
from brownie import chain
from web3 import Web3

def to_keccak(types, str):
    return Web3.solidityKeccak(types, str)


def prepare_root(users, values):
    h1 = to_keccak(["address", "uint256"], [str(users[0]), values[0]])
    h2 = to_keccak(["address", "uint256"], [str(users[1]), values[1]])
    h3 = to_keccak(["address", "uint256"], [str(users[2]), values[2]])
    h4 = to_keccak(["address", "uint256"], [str(users[3]), values[3]])

    root_1 = ""
    root_2 = ""
    root = ""

    if int(h1.hex(), 16) <= int(h2.hex(), 16):
        root_1 = to_keccak(["bytes32", "bytes32"], [h1, h2])
    else:
        root_1 = to_keccak(["bytes32", "bytes32", [h2, h1]])
    
    if int(h3.hex(), 16) <= int(h4.hex(), 16):
        root_2 = to_keccak(["bytes32", "bytes32"], [h3, h4])
    else:
        root_2 = to_keccak(["bytes32", "bytes32", [h4, h3]])

    if int(root_1.hex(), 16) <= int(root_2.hex(), 16):
        root = to_keccak(["bytes32", "bytes32"], [root_1, root_2])
    else:
        root = to_keccak(["bytes32", "bytes32"], [root_2, root_1])
    
    return (root, [h1, h2, h3, h3, root_1, root_2])
    

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




