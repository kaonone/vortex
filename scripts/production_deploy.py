import time

from brownie import (
    accounts,
    network,
    StrategySushiBadgerWbtcWeth,
    SettV4,
    AdminUpgradeabilityProxy,
    Controller,
    BadgerRegistry,
)

from config import WANT, PROTECTED_TOKENS, FEES, REGISTRY

from helpers.constants import AddressZero

import click
from rich.console import Console

console = Console()

sleep_between_tx = 1


def main():
    """
    FOR STRATEGISTS AND GOVERNANCE
    Deploys a Controller, a SettV4 and your strategy under upgradable proxies and wires them up.
    Note that it sets your deployer account as the governance for the three contracts so that
    the setup and production tests are simpler and more efficient. The rest of the permissioned actors
    are set based on the latest entries from the Badger Registry.
    """

    # Get deployer account from local keystore
    # dev = connect_account()
    dev = accounts.at("0xeE8b29AA52dD5fF2559da2C50b1887ADee257556", force=True)

    # Get actors from registry
    registry = BadgerRegistry.at(REGISTRY)

    strategist = dev.address  # registry.get("governance")
    guardian = registry.get("guardian")
    keeper = registry.get("keeper")
    proxyAdmin = registry.get("proxyAdminDev")
    controller = registry.get("controller")

    assert strategist != AddressZero
    assert guardian != AddressZero
    assert keeper != AddressZero
    assert proxyAdmin != AddressZero
    assert controller != AddressZero

    # Deploy controller
    # controller = deploy_controller(dev, proxyAdmin)

    # Deploy Vault
    vault = deploy_vault(
        controller,
        dev.address,  # Deployer will be set as governance for testing stage
        keeper,
        guardian,
        dev,
        proxyAdmin,
    )

    # Deploy Strategy
    strategy = deploy_strategy(
        controller,
        dev.address,  # Deployer will be set as governance for testing stage
        strategist,
        keeper,
        guardian,
        dev,
        proxyAdmin,
    )

    controllerContract = Controller.at(controller)

    # Wire up vault and strategy to test controller
    wire_up_test_controller(controllerContract, vault, strategy, dev)


def deploy_controller(dev, proxyAdmin):

    controller_logic = Controller.at(
        "0x01d10fdc6b484BE380144dF12EB6C75387EfC49B"
    )  # Controller Logic

    # Deployer address will be used for all actors as controller will only be used for testing
    args = [
        dev.address,
        dev.address,
        dev.address,
        dev.address,
    ]

    controller_proxy = AdminUpgradeabilityProxy.deploy(
        controller_logic,
        proxyAdmin,
        controller_logic.initialize.encode_input(*args),
        {"from": dev},
    )
    time.sleep(sleep_between_tx)

    ## We delete from deploy and then fetch again so we can interact
    AdminUpgradeabilityProxy.remove(controller_proxy)
    controller_proxy = Controller.at(controller_proxy.address)

    console.print(
        "[green]Controller was deployed at: [/green]", controller_proxy.address
    )

    return controller_proxy


def deploy_vault(controller, governance, keeper, guardian, dev, proxyAdmin):

    args = [
        WANT,
        controller,
        governance,
        keeper,
        guardian,
        False,
        "",
        "",
    ]

    print("Vault Arguments: ", args)

    vault_logic = SettV4.at(
        "0x20Dce41Acca85E8222D6861Aa6D23B6C941777bF"
    )  # SettV4 Logic

    vault_proxy = AdminUpgradeabilityProxy.deploy(
        vault_logic,
        proxyAdmin,
        "0x",
        {"from": dev},
    )
    time.sleep(sleep_between_tx)

    ## We delete from deploy and then fetch again so we can interact
    AdminUpgradeabilityProxy.remove(vault_proxy)
    vault_proxy = SettV4.at(vault_proxy.address)

    vault_proxy.initialize(*args, {"from": dev})

    console.print("[green]Vault was deployed at: [/green]", vault_proxy.address)

    assert vault_proxy.paused()

    vault_proxy.unpause({"from": dev})

    assert vault_proxy.paused() == False

    return vault_proxy


def deploy_strategy(
    controller, governance, strategist, keeper, guardian, dev, proxyAdmin
):

    args = [
        governance,
        strategist,
        controller,
        keeper,
        guardian,
        PROTECTED_TOKENS,
        FEES,
    ]

    print("Strategy Arguments: ", args)

    strat_logic = StrategySushiBadgerWbtcWeth.deploy({"from": dev})
    time.sleep(sleep_between_tx)

    strat_proxy = AdminUpgradeabilityProxy.deploy(
        strat_logic,
        proxyAdmin,
        "0x",
        {"from": dev},
    )
    time.sleep(sleep_between_tx)

    ## We delete from deploy and then fetch again so we can interact
    AdminUpgradeabilityProxy.remove(strat_proxy)
    strat_proxy = StrategySushiBadgerWbtcWeth.at(strat_proxy.address)

    strat_proxy.initialize(*args, {"from": dev})

    console.print("[green]Strategy was deployed at: [/green]", strat_proxy.address)

    return strat_proxy


def wire_up_test_controller(controller, vault, strategy, dev):
    controller.approveStrategy(WANT, strategy.address, {"from": dev})
    time.sleep(sleep_between_tx)
    assert controller.approvedStrategies(WANT, strategy.address) == True

    controller.setStrategy(WANT, strategy.address, {"from": dev})
    time.sleep(sleep_between_tx)
    assert controller.strategies(WANT) == strategy.address

    controller.setVault(WANT, vault.address, {"from": dev})
    time.sleep(sleep_between_tx)
    assert controller.vaults(WANT) == vault.address

    console.print("[blue]Controller wired up![/blue]")


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev
