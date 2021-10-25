import brownie
import constants
import constants_bsc
import random
from brownie import network


def data():
    if network.show_active() == "hardhat-arbitrum-fork":
        constant = constants
    else:
        constant = constants_bsc
    return constant


def test_withdraw(vault_deposited, users, token):
    constant = data()
    for user in users:
        v_t_bal_before = token.balanceOf(vault_deposited)
        u_v_bal_before = vault_deposited.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault_deposited.withdraw(u_v_bal_before, user, {"from": user})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == constant.DEPOSIT_AMOUNT
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert (
            token.balanceOf(vault_deposited) + constant.DEPOSIT_AMOUNT == v_t_bal_before
        )
        assert vault_deposited.balanceOf(user) == 0
        assert token.balanceOf(user) == int(constant.DEPOSIT_AMOUNT) + u_t_bal_before


def test_withdraw_yield(vault_deposited, users, token, deployer):
    constant = data()
    token.transfer(vault_deposited, constant.YIELD_AMOUNT, {"from": deployer})
    expected_withdrawal = int(
        constant.DEPOSIT_AMOUNT + constant.YIELD_AMOUNT / len(users)
    )
    for user in users:
        v_t_bal_before = token.balanceOf(vault_deposited)
        u_v_bal_before = vault_deposited.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault_deposited.withdraw(u_v_bal_before, user, {"from": user})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert (
            abs(tx.events["Withdraw"]["withdrawal"] - expected_withdrawal)
            < constant.ACCURACY
        )
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert (
            abs(token.balanceOf(vault_deposited) + expected_withdrawal - v_t_bal_before)
            < constant.ACCURACY
        )
        assert vault_deposited.balanceOf(user) == 0
        assert (
            abs(token.balanceOf(user) - expected_withdrawal - u_t_bal_before)
            < constant.ACCURACY
        )


def test_withdraw_diff_recipient(vault_deposited, users, token, deployer):
    constant = data()
    token.approve(
        vault_deposited, constant.DEPOSIT_AMOUNT * len(users), {"from": deployer}
    )
    vault_deposited.deposit(
        constant.DEPOSIT_AMOUNT * len(users), deployer, {"from": deployer}
    )
    for user in users:
        v_t_bal_before = token.balanceOf(vault_deposited)
        u_v_bal_before = vault_deposited.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault_deposited.withdraw(u_v_bal_before, user, {"from": deployer})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == constant.DEPOSIT_AMOUNT
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert (
            token.balanceOf(vault_deposited) + constant.DEPOSIT_AMOUNT == v_t_bal_before
        )
        assert token.balanceOf(user) == int(constant.DEPOSIT_AMOUNT) + u_t_bal_before
    assert vault_deposited.balanceOf(deployer) == 0


def test_withdraw_empty(vault_deposited, users, token, deployer):
    constant = data()
    token.transfer(
        deployer, token.balanceOf(vault_deposited), {"from": vault_deposited}
    )
    for user in users:
        v_t_bal_before = token.balanceOf(vault_deposited)
        u_v_bal_before = vault_deposited.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault_deposited.withdraw(u_v_bal_before, user, {"from": user})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == 0
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert token.balanceOf(vault_deposited) == v_t_bal_before
        assert token.balanceOf(user) == u_t_bal_before


def test_withdraw_failures(vault_deposited, users, token, deployer):
    constant = data()
    user = users[0]
    with brownie.reverts("!_shares"):
        vault_deposited.withdraw(0, user, {"from": user})
    with brownie.reverts("insufficient balance"):
        vault_deposited.withdraw(constant.DEPOSIT_LIMIT - 1, user, {"from": user})
