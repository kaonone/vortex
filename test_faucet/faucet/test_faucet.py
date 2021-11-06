import brownie
from brownie import chain


def test_faucet(faucet, deployer, users, token):
    token.transfer(faucet, 100_000_000e18, {"from": deployer})
    for user in users:
        faucet.distribute(user, {"from": deployer})
    assert token.balanceOf(users[1]) == 10_000e18
    with brownie.reverts("wait cooldown"):
        faucet.distribute(users[1], {"from": deployer})
    chain.sleep(100000)
    tx = faucet.distribute(users[1], {"from": deployer})
    assert "Distributed" in tx.events
    assert tx.events["Distributed"]["user"] == users[1]
    assert [tx.events["Distributed"]["block"], 2] == faucet.getUserDetail(users[1])
    chain.sleep(100000)
    with brownie.reverts():
        faucet.distribute(users[2], {"from": users[3]})


def test_faucet_management(faucet, deployer, users, token):
    with brownie.reverts("invalid address"):
        faucet.setToken(brownie.ZERO_ADDRESS, {"from": deployer})
    with brownie.reverts():
        faucet.setToken(
            "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", {"from": users[1]}
        )
    faucet.setToken("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", {"from": deployer})
    assert faucet.token() == "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
    with brownie.reverts("invalid amount"):
        faucet.setAmount(0, {"from": deployer})
    with brownie.reverts():
        faucet.setAmount(1000e18, {"from": users[1]})
    faucet.setAmount(100_000e18, {"from": deployer})
    assert faucet.amount() == 100_000e18
    with brownie.reverts("invalid period"):
        faucet.setCoolDown(0, {"from": deployer})
    with brownie.reverts():
        faucet.setCoolDown(3, {"from": users[1]})
    faucet.setCoolDown(3, {"from": deployer})
    assert faucet.cooldown() == (86400 * 3)
    # check pause and unpaus
    faucet.pause({"from": deployer})

    faucet.setToken(token, {"from": deployer})
    token.transfer(faucet, 100_000_000e18, {"from": deployer})

    with brownie.reverts():
        faucet.distribute(users[1], {"from": deployer})

    faucet.unpause({"from": deployer})
    faucet.distribute(users[1], {"from": deployer})
