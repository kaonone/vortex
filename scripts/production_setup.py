import time

from brownie import (
    accounts,
    network,
    StrategySushiBadgerWbtcWeth,
    SettV4,
)

from config import (
    WANT,
    #   LP_COMPONENT,
    REWARD_TOKEN,
    FEES,
    CONTROLLER,
    BADGER_DEV_MULTISIG,
    KEEPER,
    GUARDIAN,
)

import click
from rich.console import Console

console = Console()

sleep_between_tx = 1


def main():
    dev = connect_account()

    strategy = StrategySushiBadgerWbtcWeth.at(
        "0xDed61Bd8a8c90596D8A6Cf0e678dA04036146963"
    )
    vault = SettV4.at("0xEa8567d84E3e54B32176418B4e0C736b56378961")

    assert strategy.paused() == False
    assert vault.paused() == False

    console.print("[blue]Strategy: [/blue]", strategy.getName())
    console.print("[blue]Vault: [/blue]", vault.name())

    set_parameters(dev, strategy, vault)

    check_parameters(strategy, vault)


def set_parameters(dev, strategy, vault):
    # Set Controller (deterministic)
    if strategy.controller() != CONTROLLER:
        strategy.setController(CONTROLLER, {"from": dev})
        time.sleep(sleep_between_tx)
    if vault.controller() != CONTROLLER:
        vault.setController(CONTROLLER, {"from": dev})
        time.sleep(sleep_between_tx)

    console.print("[green]Controller existing or set at: [/green]", CONTROLLER)

    # Set Fees
    if strategy.performanceFeeGovernance() != FEES[0]:
        strategy.setPerformanceFeeGovernance(FEES[0], {"from": dev})
        time.sleep(sleep_between_tx)
    if strategy.performanceFeeStrategist() != FEES[1]:
        strategy.setPerformanceFeeStrategist(FEES[1], {"from": dev})
        time.sleep(sleep_between_tx)
    if strategy.withdrawalFee() != FEES[2]:
        strategy.setWithdrawalFee(FEES[2], {"from": dev})
        time.sleep(sleep_between_tx)

    console.print("[green]Fees existing or set at: [/green]", FEES)

    # Set permissioned accounts
    if strategy.keeper() != KEEPER:
        strategy.setKeeper(KEEPER, {"from": dev})
        time.sleep(sleep_between_tx)
    if vault.keeper() != KEEPER:
        vault.setKeeper(KEEPER, {"from": dev})
        time.sleep(sleep_between_tx)

    console.print("[green]Keeper existing or set at: [/green]", KEEPER)

    if strategy.guardian() != GUARDIAN:
        strategy.setGuardian(GUARDIAN, {"from": dev})
        time.sleep(sleep_between_tx)
    if vault.guardian() != GUARDIAN:
        vault.setGuardian(GUARDIAN, {"from": dev})
        time.sleep(sleep_between_tx)

    console.print("[green]Guardian existing or set at: [/green]", GUARDIAN)

    if strategy.strategist() != BADGER_DEV_MULTISIG:
        strategy.setStrategist(BADGER_DEV_MULTISIG, {"from": dev})
        time.sleep(sleep_between_tx)

    console.print("[green]Strategist existing or set at: [/green]", BADGER_DEV_MULTISIG)

    if strategy.governance() != BADGER_DEV_MULTISIG:
        strategy.setGovernance(BADGER_DEV_MULTISIG, {"from": dev})
        time.sleep(sleep_between_tx)
    if vault.governance() != BADGER_DEV_MULTISIG:
        vault.setGovernance(BADGER_DEV_MULTISIG, {"from": dev})
        time.sleep(sleep_between_tx)

    console.print("[green]Governance existing or set at: [/green]", BADGER_DEV_MULTISIG)


def check_parameters(strategy, vault):
    assert strategy.want() == WANT
    assert vault.token() == WANT
    assert strategy.lpComponent() == LP_COMPONENT
    assert strategy.reward() == REWARD_TOKEN

    assert strategy.controller() == CONTROLLER
    assert vault.controller() == CONTROLLER

    assert strategy.performanceFeeGovernance() == FEES[0]
    assert strategy.performanceFeeStrategist() == FEES[1]
    assert strategy.withdrawalFee() == FEES[2]

    assert strategy.keeper() == KEEPER
    assert vault.keeper() == KEEPER
    assert strategy.guardian() == GUARDIAN
    assert vault.guardian() == GUARDIAN
    assert strategy.strategist() == BADGER_DEV_MULTISIG
    assert strategy.governance() == BADGER_DEV_MULTISIG
    assert vault.governance() == BADGER_DEV_MULTISIG

    console.print("[blue]All Parameters checked![/blue]")


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev
