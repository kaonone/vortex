import brownie
import constant_fork
import random
import pytest
import os
from brownie import network, interface, BasisStrategy, accounts


proof = [
    "0xfc44b0fab2f8e7eec2842ad87e4907918e648ca0464a1c008ca209092cc19f8f",
    "0x4cf20432b77de636d46caa42946743c1585236dff90d8d2d3870093ffa2e811e",
    "0xd025ded88ec81345a6d3f1c694391122cc1f55362fabe372c16eca038930d33e",
    "0x871028e60cdd92d2df2bdb66541a0da82f10fab5616f21798d446f212c8a4020",
    "0x8f3444cca5dd3f4fe13f10975954a14cf46ef75b0f204c41b1718dfda8cc9e6d",
    "0x09f2b0f5f5a10925214c9c3bb4eca249dee507eb3a72fe5290d020454c086b4c",
    "0xe05a15541dc8cbe076fd75d12eb19ef8a714b9e0e772adfb44d842a8b205aa5f",
    "0x26b1013e940e59ef17eda9878c8edd9802d1a4977ad68b8ca70560c4db269023",
    "0xa7305de20497b4b62576688851e02717f3a7e5cdb12c5f6835b488b2027cec66",
]


@pytest.fixture
def owner(accounts):
    owner = accounts.at(constant_fork.DEPLOYER, force=True)
    yield owner


@pytest.fixture
def strategy(owner):
    strategy = BasisStrategy.at(constant_fork.STRATEGY)
    strategy.initialize(
        constant_fork.LONG_ASSET,
        constant_fork.UNI_POOL,
        constant_fork.VAULT,
        constant_fork.ROUTER,
        constant_fork.WETH,
        owner,
        constant_fork.MCLIQUIDITY,
        constant_fork.PERP_INDEX,
        constant_fork.BUFFER,
        constant_fork.isV2,
        {"from": owner},
    )
    strategy.setLmClaimerAndMcb(
        constant_fork.CLAIMER_CONTRACT, constant_fork.MCB, {"from": owner}
    )
    yield strategy


def test_claim(strategy, owner):
    mcb = interface.IERC20(constant_fork.MCB)
    assert mcb.balanceOf(strategy.address) == 0
    assert mcb.balanceOf(owner) == 0
    with brownie.reverts():
        strategy.gatherLMrewards(3, 19672585927448070489, proof, {"from": accounts[0]})
    strategy.gatherLMrewards(3, 19672585927448070489, proof, {"from": owner})
    assert mcb.balanceOf(strategy) == 0
    assert mcb.balanceOf(owner) > 0
