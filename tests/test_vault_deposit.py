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
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constants.DEPOSIT_AMOUNT
        assert (
            tx.events["Deposit"]["shares"] == (vault.balanceOf(user)) - u_v_bal_before
        )
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constants.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before - constants.DEPOSIT_AMOUNT == token.balanceOf(user)
    assert vault.totalAssets() == constants.DEPOSIT_AMOUNT * len(users)


def test_deposit_with_mal_funds(vault, users, token, randy, deployer):
    user = users[0]
    assert token.balanceOf(randy) == 0
    token.approve(vault, 2 ** 256 - 1, {"from": randy})
    with brownie.reverts():
        vault.deposit(constants.DEPOSIT_AMOUNT, randy, {"from": randy})

    balance = token.balanceOf(user) + 1
    token.approve(vault, 2 ** 256 - 1, {"from": user})
    with brownie.reverts():
        vault.deposit(balance, user, {"from": user})

    with brownie.reverts("!_amount"):
        vault.deposit(0, user, {"from": user})

    with brownie.reverts("!_recipient"):
        vault.deposit(
            constants.DEPOSIT_AMOUNT,
            "0x0000000000000000000000000000000000000000",
            {"from": user},
        )

    with brownie.reverts("!depositLimit"):
        vault.deposit(constants.DEPOSIT_LIMIT + 1e6, deployer, {"from": deployer})


def test_deposit_paused(vault, users, token, deployer):
    vault.pause({"from": deployer})
    with brownie.reverts():
        vault.deposit(constants.DEPOSIT_AMOUNT, users[0], {"from": users[0]})


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
        rand = random.randint(1, 5)
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


def test_deposit_all_withdraw_all(vault, users, token, deployer):
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_t_bal_before = token.balanceOf(user)
        u_v_bal_before = vault.balanceOf(user)
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        tx = vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
        assert "Deposit" in tx.events
        assert tx.events["Deposit"]["user"] == user
        assert tx.events["Deposit"]["deposit"] == constants.DEPOSIT_AMOUNT
        assert (
            tx.events["Deposit"]["shares"] == (vault.balanceOf(user)) - u_v_bal_before
        )
        assert vault.balanceOf(user) > u_v_bal_before
        assert v_t_bal_before + constants.DEPOSIT_AMOUNT == token.balanceOf(vault)
        assert u_t_bal_before - constants.DEPOSIT_AMOUNT == token.balanceOf(user)
    assert vault.totalAssets() == constants.DEPOSIT_AMOUNT * len(users)
    assert vault.pricePerShare() == 1
    for user in users:
        v_t_bal_before = token.balanceOf(vault)
        u_v_bal_before = vault.balanceOf(user)
        u_t_bal_before = token.balanceOf(user)
        tx = vault.withdraw(u_v_bal_before, user, {"from": user})
        assert "Withdraw" in tx.events
        assert tx.events["Withdraw"]["user"] == user
        assert tx.events["Withdraw"]["withdrawal"] == constants.DEPOSIT_AMOUNT
        assert tx.events["Withdraw"]["shares"] == u_v_bal_before
        assert token.balanceOf(vault) + constants.DEPOSIT_AMOUNT == v_t_bal_before
        assert vault.balanceOf(user) == 0
        assert token.balanceOf(user) == int(constants.DEPOSIT_AMOUNT) + u_t_bal_before
    assert vault.totalAssets() == 0
    assert vault.pricePerShare() == 1


def test_not_issue_zero_shares(vault, deployer, users, token):
    token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": deployer})
    vault.deposit(constants.DEPOSIT_AMOUNT, deployer, {"from": deployer})
    token.transfer(vault, constants.DEPOSIT_AMOUNT, {"from": deployer})
    assert vault.pricePerShare() == 2
    with brownie.reverts():
        vault.deposit(1, deployer, {"from": deployer})
