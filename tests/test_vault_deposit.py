import brownie
import constants
import constants_bsc
import random
from brownie import network
from conftest import data


def test_deposit(vault, users, token):
    constant = data()
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constant.DEPOSIT_AMOUNT, {"from": user})
        vt = vault.calcSharesIssuable(constant.DEPOSIT_AMOUNT)
        tx = vault.deposit(constant.DEPOSIT_AMOUNT, user, {"from": user})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constant.DEPOSIT_AMOUNT
        assert (
            tx.events["Deposit"]["shares"]
            == (vault.balanceOf(user)) - u_v_bal_before
            == vt
        )
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constant.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before - constant.DEPOSIT_AMOUNT == token.balanceOf(user)
    assert vault.totalAssets() == constant.DEPOSIT_AMOUNT * len(users)


def test_deposit_with_mal_funds(vault, users, token, randy, deployer):
    constant = data()
    user = users[0]
    assert token.balanceOf(randy) == 0
    token.approve(vault, 2 ** 256 - 1, {"from": randy})
    with brownie.reverts():
        vault.deposit(constant.DEPOSIT_AMOUNT, randy, {"from": randy})

    balance = token.balanceOf(user) + 1
    token.approve(vault, 2 ** 256 - 1, {"from": user})
    with brownie.reverts():
        vault.deposit(balance, user, {"from": user})

    with brownie.reverts("!_amount"):
        vault.deposit(0, user, {"from": user})

    with brownie.reverts("!_recipient"):
        vault.deposit(
            constant.DEPOSIT_AMOUNT,
            "0x0000000000000000000000000000000000000000",
            {"from": user},
        )

    with brownie.reverts("!depositLimit"):
        token.approve(
            vault, constant.DEPOSIT_LIMIT + constant.ADD_VALUE, {"from": deployer}
        )
        vault.deposit(
            constant.DEPOSIT_LIMIT + constant.ADD_VALUE, deployer, {"from": deployer}
        )


def test_deposit_paused(vault, users, token, deployer):
    constant = data()
    vault.pause({"from": deployer})
    with brownie.reverts():
        vault.deposit(constant.DEPOSIT_AMOUNT, users[0], {"from": users[0]})


def test_deposit_yield(vault, users, deployer, token):
    constant = data()
    token.approve(vault, constant.DEPOSIT_AMOUNT, {"from": deployer})
    vault.deposit(constant.DEPOSIT_AMOUNT, deployer, {"from": deployer})
    token.transfer(vault, constant.YIELD_AMOUNT, {"from": deployer})
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constant.DEPOSIT_AMOUNT, {"from": user})
        tx = vault.deposit(constant.DEPOSIT_AMOUNT, user, {"from": user})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constant.DEPOSIT_AMOUNT
        assert tx.events["Deposit"]["shares"] == vault.balanceOf(user) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constant.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before - constant.DEPOSIT_AMOUNT == token.balanceOf(user)


def test_deposit_randomiser(vault, users, token):
    constant = data()
    deposit_total = 0
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        rand = random.randint(1, 5)
        deposit = constant.DEPOSIT_AMOUNT * rand
        token.approve(vault, deposit, {"from": user})
        tx = vault.deposit(deposit, user, {"from": user})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == deposit
        assert tx.events["Deposit"]["shares"] == vault.balanceOf(user) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + deposit == token.balanceOf(vault)
        assert u_t_bal_before - deposit == token.balanceOf(user)
        deposit_total += deposit
    assert abs(vault.totalAssets() - int(deposit_total)) < constant.ACCURACY


def test_deposit_diff_recipient(vault, users, token, deployer):
    constant = data()
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constant.DEPOSIT_AMOUNT, {"from": deployer})
        tx = vault.deposit(constant.DEPOSIT_AMOUNT, user, {"from": deployer})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constant.DEPOSIT_AMOUNT
        assert tx.events["Deposit"]["shares"] == vault.balanceOf(user) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constant.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before == token.balanceOf(user)
    assert vault.totalAssets() == constant.DEPOSIT_AMOUNT * len(users)


def test_deposit_all_withdraw_all(vault, users, token, deployer):
    constant = data()
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constant.DEPOSIT_AMOUNT, {"from": user})
        tx = vault.deposit(constant.DEPOSIT_AMOUNT, user, {"from": user})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constant.DEPOSIT_AMOUNT
        assert (
            tx.events["Deposit"]["shares"] == (vault.balanceOf(user)) - u_v_bal_before
        )
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constant.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before - constant.DEPOSIT_AMOUNT == token.balanceOf(user)
    assert vault.totalAssets() == constant.DEPOSIT_AMOUNT * len(users)
    assert vault.pricePerShare() == constant.DECIMAL
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_v_bal_before = vault.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault.withdraw(u_v_bal_before, 0, user, {"from": user})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == constant.DEPOSIT_AMOUNT
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert token.balanceOf(vault) + constant.DEPOSIT_AMOUNT == v_t_bal_before
        assert vault.balanceOf(user) == 0
        assert token.balanceOf(user) == int(constant.DEPOSIT_AMOUNT) + u_t_bal_before
    assert vault.totalAssets() == 0
    assert vault.pricePerShare() == constant.DECIMAL


def test_not_issue_zero_shares(vault, deployer, users, token):
    constant = data()
    token.approve(vault, constant.DEPOSIT_AMOUNT, {"from": deployer})
    vault.deposit(constant.DEPOSIT_AMOUNT, deployer, {"from": deployer})
    token.transfer(vault, constant.DEPOSIT_AMOUNT, {"from": deployer})
    assert vault.pricePerShare() == 2 * constant.DECIMAL
    with brownie.reverts():
        vault.deposit(1, deployer, {"from": deployer})
