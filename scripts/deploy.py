from brownie import *
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

  ## Uniswap some tokens here
  router = Contract.from_explorer("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
  router.swapExactETHForTokens(
    0, ## Mint out
    ["0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", WANT],
    deployer,
    9999999999999999,
    {"from": deployer, "value": 5000000000000000000}
  )

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
