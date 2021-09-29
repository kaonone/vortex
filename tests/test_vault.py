import brownie
import constants
import random

#TODO Test withdraws with plugged in strategy and model loss scenarios


def test_withdraw(vault_deposited, users, token):
    for user in users:
        v_t_bal_before = token.balanceOf(vault_deposited)
        u_v_bal_before = vault_deposited.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault_deposited.withdraw(u_v_bal_before, user, {"from": user})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == constants.DEPOSIT_AMOUNT
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert token.balanceOf(vault_deposited) + constants.DEPOSIT_AMOUNT == v_t_bal_before
        assert vault_deposited.balanceOf(user) == 0
        assert token.balanceOf(user) == int(constants.DEPOSIT_AMOUNT) + u_t_bal_before


def test_withdraw_yield(vault_deposited, users, token, deployer):
    token.transfer(vault_deposited, constants.YIELD_AMOUNT, {"from": deployer})
    expected_withdrawal = int(constants.DEPOSIT_AMOUNT + constants.YIELD_AMOUNT / len(users))
    for user in users:
        v_t_bal_before = token.balanceOf(vault_deposited)
        u_v_bal_before = vault_deposited.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault_deposited.withdraw(u_v_bal_before, user, {"from": user})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert abs(tx.events["Withdraw"]["withdrawal"] - expected_withdrawal) < constants.ACCURACY
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert abs(token.balanceOf(vault_deposited) + expected_withdrawal - v_t_bal_before) < constants.ACCURACY
        assert vault_deposited.balanceOf(user) == 0
        assert abs(token.balanceOf(user) - expected_withdrawal - u_t_bal_before) < constants.ACCURACY


def test_withdraw_diff_recipient(vault_deposited, users, token, deployer):
    token.approve(vault_deposited, constants.DEPOSIT_AMOUNT * len(users), {"from": deployer})
    vault_deposited.deposit(constants.DEPOSIT_AMOUNT * len(users), deployer, {"from": deployer})
    for user in users:
        v_t_bal_before = token.balanceOf(vault_deposited)
        u_v_bal_before = vault_deposited.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault_deposited.withdraw(u_v_bal_before, user, {"from": deployer})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == constants.DEPOSIT_AMOUNT
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert token.balanceOf(vault_deposited) + constants.DEPOSIT_AMOUNT == v_t_bal_before
        assert token.balanceOf(user) == int(constants.DEPOSIT_AMOUNT) + u_t_bal_before
    assert vault_deposited.balanceOf(deployer) == 0


def test_withdraw_empty(vault_deposited, users, token, deployer):
    token.transfer(deployer, token.balanceOf(vault_deposited), {"from": vault_deposited})
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
    user = users[0]
    with brownie.reverts("!_shares"):
        vault_deposited.withdraw(0, user, {"from": user})
    with brownie.reverts("insufficient balance"):
        vault_deposited.withdraw(constants.DEPOSIT_LIMIT - 1, user, {"from": user})


def test_deposit(vault, users, token):
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        tx = vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constants.DEPOSIT_AMOUNT
        assert tx.events["Deposit"]["shares"] == (vault.balanceOf(user)) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constants.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before - constants.DEPOSIT_AMOUNT == token.balanceOf(user)
    assert vault.totalAssets() == constants.DEPOSIT_AMOUNT * len(users)


def test_deposit_yield(vault, users, deployer, token):
    token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": deployer})
    vault.deposit(constants.DEPOSIT_AMOUNT, deployer, {"from": deployer})
    token.transfer(vault, constants.YIELD_AMOUNT, {"from": deployer})
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        tx = vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constants.DEPOSIT_AMOUNT
        assert tx.events["Deposit"]["shares"] == vault.balanceOf(user) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constants.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before - constants.DEPOSIT_AMOUNT == token.balanceOf(user)


def test_deposit_randomiser(vault, users, token):
    deposit_total = 0
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        rand = random.randint(1,5)
        deposit = constants.DEPOSIT_AMOUNT * rand
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
    assert abs(vault.totalAssets() - int(deposit_total)) < constants.ACCURACY


def test_deposit_diff_recipient(vault, users, token, deployer):
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": deployer})
        tx = vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": deployer})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constants.DEPOSIT_AMOUNT
        assert tx.events["Deposit"]["shares"] == vault.balanceOf(user) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constants.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before == token.balanceOf(user)
    assert vault.totalAssets() == constants.DEPOSIT_AMOUNT * len(users)


def test_deposit_failures(vault, users, token, deployer):
    user = users[0]
    with brownie.reverts("!_amount"):
        vault.deposit(0, user, {"from": user})
    with brownie.reverts("!_recipient"):
        vault.deposit(constants.DEPOSIT_AMOUNT, "0x0000000000000000000000000000000000000000", {"from": user})
    with brownie.reverts("!depositLimit"):
        token.approve(vault, constants.DEPOSIT_LIMIT + 1, {"from": deployer})
        vault.deposit(constants.DEPOSIT_LIMIT + 1e18, deployer, {"from": deployer})
    token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
    vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
    token.transfer(deployer, token.balanceOf(vault), {"from": vault})
    with brownie.reverts("totalAssets == 0"):
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
