from brownie import *
from brownie import interface, accounts, Contract, MyStrategy, Controller, SettV3
import time

from config import (
  BADGER_DEV_MULTISIG,
  WANT,
  LP_COMPONENT,
  REWARD_TOKEN,
  PROTECTED_TOKENS,
  FEES
)
from dotmap import DotMap


def main():
  return deploy()

def deploy():
  """
    Deploys, vault, controller and strats and wires them up for you to test
  """
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
    BADGER_DEV_MULTISIG
  )

  sett = SettV3.deploy({"from": deployer})
  sett.initialize(
    WANT,
    controller,
    BADGER_DEV_MULTISIG,
    keeper,
    guardian,
    False,
    "prefix",
    "PREFIX"
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
  strategy = MyStrategy.deploy({"from": deployer})
  strategy.initialize(
    BADGER_DEV_MULTISIG,
    strategist,
    controller,
    keeper,
    guardian,
    PROTECTED_TOKENS,
    FEES
  )

  ## Tool that verifies bytecode (run independetly) <- Webapp for anyone to verify

  ## Set up tokens
  want = interface.IERC20(WANT)
  lpComponent = interface.IERC20(LP_COMPONENT)
  rewardToken = interface.IERC20(REWARD_TOKEN)

  ## Wire up Controller to Strart
  ## In testing will pass, but on live it will fail
  controller.approveStrategy(WANT, strategy, {"from": governance})
  controller.setStrategy(WANT, strategy, {"from": deployer})

  WBTC = strategy.wBTC_TOKEN()
  wbtc = interface.IERC20(WBTC)
  IBBTC = strategy.ibBTC_TOKEN()
  ibBTC = interface.IERC20(IBBTC)

  ## Uniswap some tokens here
  router = Contract.from_explorer(strategy.SUSHISWAP_ROUTER())
  
  wbtc.approve(router.address, 999999999999999999999999999999, {"from": deployer})
  ibBTC.approve(router.address, 999999999999999999999999999999, {"from": deployer})

  # Buy WBTC with path MATIC -> WETH -> WBTC
  router.swapExactETHForTokens(
      0,
      ["0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
          "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619", WBTC],
      deployer,
      9999999999999999,
      {"from": deployer, "value": 5000 * 10**18}
  )

  # Buy WBTC with path MATIC -> WETH -> WBTC -> ibBTC
  router.swapExactETHForTokens(
      0,
      ["0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
          "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619", WBTC, IBBTC],
      deployer,
      9999999999999999,
      {"from": deployer, "value": 5000 * 10**18}
  )

  # Add ibBTC-wBTC liquidity
  router.addLiquidity(
    WBTC,
    IBBTC,
    wbtc.balanceOf(deployer),
    ibBTC.balanceOf(deployer),
    wbtc.balanceOf(deployer) * 0.005,
    ibBTC.balanceOf(deployer) * 0.005,
    deployer,
    int(time.time()),
    {"from": deployer}
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
    lpComponent=lpComponent,
    rewardToken=rewardToken
  )
