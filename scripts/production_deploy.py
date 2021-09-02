import time

from brownie import (
    accounts,
    network,
    StrategySushiBadgerWbtcWeth, 
    SettV3, 
    AdminUpgradeabilityProxy,
    Controller,
)

from config import (
  WANT,
  PROTECTED_TOKENS,
  FEES
)

from dotmap import DotMap
import click
from rich.console import Console

console = Console()

sleep_between_tx = 1

def main():
    dev = connect_account()
    proxyadmin = connect_account()
    # Deploy Vaults and Strategies

    controller = deploy_controller(dev, proxyadmin)

    deploy_vaults_and_strategies(
        "0x12097e9755aBf710166D0027c1a2ef7609833D74",# controller.address, 
        dev.address, 
        dev.address, 
        dev.address, 
        dev.address,
        dev,
        proxyadmin
    )

def deploy_controller(dev, proxyadmin):

    controller_logic = Controller.at("0x01d10fdc6b484BE380144dF12EB6C75387EfC49B") # Controller Logic

    args = [
        dev.address,
        dev.address,
        dev.address,
        dev.address,
    ]

    controller_proxy = AdminUpgradeabilityProxy.deploy(
        controller_logic, 
        proxyadmin.address, 
        controller_logic.initialize.encode_input(*args), 
        {'from': dev}
    )
    time.sleep(sleep_between_tx)

    ## We delete from deploy and then fetch again so we can interact
    AdminUpgradeabilityProxy.remove(controller_proxy)
    controller_proxy = Controller.at(controller_proxy.address)

    console.print(
        "[green]Controller was deployed at: [/green]", controller_proxy.address
    )

    return controller_proxy
    

def deploy_vaults_and_strategies(
    controller, 
    governance, 
    strategist, 
    keeper, 
    guardian, 
    dev,
    proxyadmin
):
    # Deploy Vault

    args = [
        WANT,
        controller,
        governance,
        keeper,
        guardian,
        False,
        '',
        '',
    ]

    print("Vault Arguments: ", args)

    vault_logic = SettV3.at("0xAF0B504BD20626d1fd57F8903898168FCE7ecbc8") # SettV3 Logic
    time.sleep(sleep_between_tx)

    vault_proxy = AdminUpgradeabilityProxy.deploy(
        vault_logic, 
        proxyadmin.address, 
        vault_logic.initialize.encode_input(*args), 
        {'from': dev}
    )
    time.sleep(sleep_between_tx)

    ## We delete from deploy and then fetch again so we can interact
    AdminUpgradeabilityProxy.remove(vault_proxy)
    vault_proxy = SettV3.at(vault_proxy.address)

    console.print(
        "[green]Vault was deployed at: [/green]", vault_proxy.address
    )

    assert vault_proxy.paused()

    # Deploy Strategy

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
        proxyadmin.address, 
        strat_logic.initialize.encode_input(*args), 
        {'from': dev}
    )
    time.sleep(sleep_between_tx)

    ## We delete from deploy and then fetch again so we can interact
    AdminUpgradeabilityProxy.remove(strat_proxy)
    strat_proxy = StrategySushiBadgerWbtcWeth.at(strat_proxy.address)

    console.print(
        "[green]Strategy was deployed at: [/green]", strat_proxy.address
    )



def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev