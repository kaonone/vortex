from brownie import *
from brownie import (
    interface,
    accounts,
    Contract,
    StrategySushiBadgerWbtcWeth,
    Controller,
    SettV4,
)
import time
from helpers.time import days

from config import (
    BADGER_DEV_MULTISIG,
    WANT,
    # LP_COMPONENT,
    REWARD_TOKEN,
    PROTECTED_TOKENS,
    FEES,
)
from dotmap import DotMap


def main():
    return deploy()


def deploy():
    """
    Deploys, vault, controller and strats and wires them up for you to test
    """
    # Hack to fix Ganache v7 call bug
    accounts.default = accounts[0]
    deployer = accounts[0]

    strategist = deployer
    keeper = deployer
    guardian = deployer

    governance = accounts.at(BADGER_DEV_MULTISIG, force=True)

    controller = Controller.deploy({"from": deployer})

    controller.initialize(
        BADGER_DEV_MULTISIG,
        strategist,
        keeper,
        BADGER_DEV_MULTISIG,
    )

    sett = SettV4.deploy({"from": deployer})
    sett.initialize(
        WANT,
        controller,
        BADGER_DEV_MULTISIG,
        keeper,
        guardian,
        False,
        "prefix",
        "PREFIX",
    )

    sett.unpause({"from": governance})
    controller.setVault(WANT, sett)

    ## TODO: Add guest list once we find compatible, tested, contract
    # guestList = VipCappedGuestListWrapperUpgradeable.deploy({"from": deployer})
    # guestList.initialize(sett, {"from": deployer})
    # guestList.setGuests([deployer], [True])
    # guestList.setUserDepositCap(100000000)
    # sett.setGuestList(guestList, {"from": governance})

    ## Start up Strategy
    strategy = StrategySushiBadgerWbtcWeth.deploy({"from": deployer})
    strategy.initialize(
        BADGER_DEV_MULTISIG,
        strategist,
        controller,
        keeper,
        guardian,
        PROTECTED_TOKENS,
        FEES,
    )

    ## Tool that verifies bytecode (run independetly) <- Webapp for anyone to verify

    ## Set up tokens
    want = interface.IERC20(WANT)
    # lpComponent = interface.IERC20(LP_COMPONENT)
    rewardToken = interface.IERC20(REWARD_TOKEN)

    ## Wire up Controller to Strart
    ## In testing will pass, but on live it will fail
    controller.approveStrategy(WANT, strategy, {"from": governance})
    controller.setStrategy(WANT, strategy, {"from": deployer})

    WBTC = strategy.WBTC_TOKEN()
    WETH = strategy.WETH_TOKEN()
    wbtc = interface.IERC20(WBTC)
    weth = interface.IERC20(WETH)

    ## Uniswap some tokens here
    router = interface.IUniswapRouterV2(strategy.SUSHISWAP_ROUTER())

    wbtc.approve(router.address, 999999999999999999999999999999, {"from": deployer})
    weth.approve(router.address, 999999999999999999999999999999, {"from": deployer})

    deposit_amount = 50 * 10 ** 18

    # Convert ETH -> WETH
    interface.IWETH(WETH).deposit({"value": deposit_amount, "from": deployer})

    # Buy WBTC with path ETH -> WETH -> WBTC
    router.swapExactETHForTokens(
        0,
        [WETH, WBTC],
        deployer,
        9999999999999999,
        {"value": deposit_amount, "from": deployer},
    )

    # Add WBTC-WETH liquidity
    router.addLiquidity(
        WBTC,
        WETH,
        wbtc.balanceOf(deployer),
        weth.balanceOf(deployer),
        wbtc.balanceOf(deployer) * 0.005,
        weth.balanceOf(deployer) * 0.005,
        deployer,
        int(time.time()) + 1200,  # Now + 20mins
        {"from": deployer},
    )

    assert want.balanceOf(deployer) > 0
    print("Initial Want Balance: ", want.balanceOf(deployer.address))

    return DotMap(
        deployer=deployer,
        controller=controller,
        vault=sett,
        sett=sett,
        strategy=strategy,
        # guestList=guestList,
        want=want,
        # lpComponent=lpComponent,
        rewardToken=rewardToken,
    )
