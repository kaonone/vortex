import brownie
import constants
import constants_bsc
import random
from brownie import network
from conftest import data


def test_deposit_harvest_deposit_harvest_withdraw(
    oracle,
    vault,
    users,
    deployer,
    test_strategy,
    token,
    long,
    mcLiquidityPool,
):
    constant = data()
    # users
    user_1 = users[0]
    user_2 = users[1]
    user_l = [user_1, user_2]
    # amounts
    amount_1 = token.balanceOf(user_1)
    amount_2 = constant.DEPOSIT_AMOUNT
    amounts = [amount_1, amount_2]
    price = oracle.priceTWAPLong.call()[0]
    whale_buy_long(deployer, token, mcLiquidityPool, price)
    for n, user in enumerate(user_l):
        token.approve(vault, token.balanceOf(user), {"from": user})
        vault.deposit(amounts[n], user, {"from": user})

    test_strategy.harvest({"from": deployer})

    for n in range(100):
        brownie.chain.sleep(28801)
        test_strategy.harvest({"from": deployer})

    vault.deposit(token.balanceOf(user_2), user_2, {"from": user_2})

    for n in range(100):
        brownie.chain.sleep(28801)
        test_strategy.remargin({"from": deployer})
        print(test_strategy.getMarginAccount())

    lossExpected = [vault.expectedLoss(amount_1), vault.expectedLoss(amount_2)]

    for n, user in enumerate(user_l):
        vault.withdraw(amounts[n], lossExpected[n], user, {"from": user})

    for n in range(100):
        brownie.chain.sleep(28801)
        test_strategy.harvest({"from": deployer})
        print("Margin account: " + str(test_strategy.getMarginAccount()))
        print("Long strategy balance: " + str(long.balanceOf(test_strategy)))
        print("Total lent: " + str(vault.totalLent()))
        print("Total supply: " + str(vault.totalSupply()))
        print("Strategy want balance: " + str(token.balanceOf(test_strategy)))
        print("Vault want balance: " + str(token.balanceOf(vault)))
        print("Price per share: " + str(vault.pricePerShare()))
    bal_bef = token.balanceOf(user_2)
    print(vault.balanceOf(user_2))
    lossExpected2 = vault.expectedLoss(vault.balanceOf(user_2))
    vault.withdraw(vault.balanceOf(user_2), lossExpected2, user_2, {"from": user_2})
    test_strategy.harvest({"from": deployer})
    print(token.balanceOf(user_2) - bal_bef)
    print("Margin account: " + str(test_strategy.getMarginAccount()))
    print("Long strategy balance: " + str(long.balanceOf(test_strategy)))
    print("Total lent: " + str(vault.totalLent()))
    print("Total supply: " + str(vault.totalSupply()))
    print("Strategy want balance: " + str(token.balanceOf(test_strategy)))
    print("Vault want balance: " + str(token.balanceOf(vault)))
    print("Price per share: " + str(vault.pricePerShare()))
    lossExpected3 = vault.expectedLoss(vault.balanceOf(deployer))
    vault.withdraw(
        vault.balanceOf(deployer), lossExpected3, deployer, {"from": deployer}
    )
    print(test_strategy.getMarginAccount())
    print(vault.totalSupply())
    print("Price per share: " + str(vault.pricePerShare()))
    assert vault.totalSupply() == 0
    assert vault.totalLent() == 0
    assert long.balanceOf(test_strategy) == 0
    assert token.balanceOf(vault) == 0
    assert token.balanceOf(test_strategy) == 0
    assert vault.pricePerShare() == constant.DECIMAL


def whale_buy_long(deployer, token, mcLiquidityPool, price):
    constant = data()
    if mcLiquidityPool.getMarginAccount(constant.PERP_INDEX, deployer)[0] == 0:
        token.approve(mcLiquidityPool, token.balanceOf(deployer), {"from": deployer})
        mcLiquidityPool.setTargetLeverage(
            constant.PERP_INDEX, deployer, 1e18, {"from": deployer}
        )
        mcLiquidityPool.deposit(
            constant.PERP_INDEX,
            deployer,
            (token.balanceOf(deployer) * constant.DECIMAL_SHIFT - 1),
            {"from": deployer},
        )
    if network.show_active() == "arbitrum-main-fork":

        mcLiquidityPool.trade(
            constant.PERP_INDEX,
            deployer,
            (
                (
                    mcLiquidityPool.getMarginAccount(constant.PERP_INDEX, deployer)[3]
                    / 100
                )
                * 1e18
            )
            / price,
            price,
            brownie.chain.time() + 10000,
            deployer,
            0x40000000,
            {"from": deployer},
        )
    else:
        mcLiquidityPool.trade(
            constant.PERP_INDEX,
            deployer,
            (1_200_000e18 * 1e18) / price,
            price,
            brownie.chain.time() + 10000,
            deployer,
            0x40000000,
            {"from": deployer},
        )
