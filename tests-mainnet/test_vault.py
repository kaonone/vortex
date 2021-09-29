import brownie
import constants
import random


def test_deposit(vault, users, token):
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        tx = vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
        assert("Deposit" in tx.events)
        assert(tx.events["Deposit"]["user"] == user)
        assert(tx.events["Deposit"]["deposit"] == constants.DEPOSIT_AMOUNT)
        assert(tx.events["Deposit"]["shares"] == vault.balanceOf(user)) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert(v_t_bal_before + constants.DEPOSIT_AMOUNT == token.balanceOf(vault))
        assert(u_t_bal_before - constants.DEPOSIT_AMOUNT == token.balanceOf(user))
    assert(vault.totalAssets() == constants.DEPOSIT_AMOUNT * len(users))


def test_deposit_yield(vault, users, deployer, token):
    token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": deployer})
    vault.deposit(constants.DEPOSIT_AMOUNT, deployer, {"from": deployer})
    token.transfer(vault, 20000e18, {"from": deployer})
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        tx = vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
        assert("Deposit" in tx.events)
        assert(tx.events["Deposit"]["user"] == user)
        assert(tx.events["Deposit"]["deposit"] == constants.DEPOSIT_AMOUNT)
        assert(tx.events["Deposit"]["shares"] == vault.balanceOf(user)) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert(v_t_bal_before + constants.DEPOSIT_AMOUNT == token.balanceOf(vault))
        assert(u_t_bal_before - constants.DEPOSIT_AMOUNT == token.balanceOf(user))


def test_deposit_randomiser(vault, users, token):
    deposit_total = 0
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        rand = random.randrange(1e18, constants.DEPOSIT_AMOUNT)
        deposit = constants.DEPOSIT_AMOUNT + rand
        token.approve(vault, deposit, {"from": user})
        tx = vault.deposit(deposit, user, {"from": user})
        assert("Deposit" in tx.events)
        assert(tx.events["Deposit"]["user"] == user)
        assert(tx.events["Deposit"]["deposit"] == deposit)
        assert(tx.events["Deposit"]["shares"] == vault.balanceOf(user)) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert(v_t_bal_before + deposit == token.balanceOf(vault))
        assert(u_t_bal_before - deposit == token.balanceOf(user))
        deposit_total += deposit
    assert(abs(vault.totalAssets() - int(deposit_total)) < constants.ACCURACY)


def test_deposit_diff_recipient(vault, users, token, deployer):
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": deployer})
        tx = vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": deployer})
        assert("Deposit" in tx.events)
        assert(tx.events["Deposit"]["user"] == user)
        assert(tx.events["Deposit"]["deposit"] == constants.DEPOSIT_AMOUNT)
        assert(tx.events["Deposit"]["shares"] == vault.balanceOf(user)) - u_v_bal_before
        assert vault.balanceOf(user) > u_v_bal_before
        assert(v_t_bal_before + constants.DEPOSIT_AMOUNT == token.balanceOf(vault))
        assert(u_t_bal_before == token.balanceOf(user))
    assert(vault.totalAssets() == constants.DEPOSIT_AMOUNT * len(users))


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