from scripts.utils.constants import (
    get_deploy_config,
    get_utils_addresses,
    set_vaults_registry_contract,
    set_keeper_address,
    add_vault_contract,
)
from scripts.utils.prepare_verification_sources import prepare_verification_sources
from brownie import (
    VaultRegistry,
    BasisVault,
    BasisStrategy,
    KeeperManager,
    chain,
)

DEPLOY_TX_HASH = ""


def main():
    tx = chain.get_transaction(DEPLOY_TX_HASH)
    utils_addresses = get_utils_addresses()
    deploy_config = get_deploy_config()

    deploy_events = list(filter(lambda event: "newContract" in event, tx.events))
    shift = 0

    if not utils_addresses["vaults_registry"]:
        registry_address = deploy_events[shift]["newContract"]
        set_vaults_registry_contract(registry_address)
        shift += 1

    if deploy_config["use_alchemy_keeper"] and not utils_addresses["keeper_address"]:
        keeper_address = deploy_events[shift]["newContract"]
        set_keeper_address(keeper_address)
        shift += 1

    vault_address = deploy_events[shift]["newContract"]
    strategy_address = deploy_events[shift + 1]["newContract"]
    add_vault_contract(vault_address, strategy_address)

    if registry_address:
        publish_sources(VaultRegistry, registry_address)

    if keeper_address:
        publish_sources(KeeperManager, keeper_address)

    publish_sources(BasisVault, vault_address)
    publish_sources(BasisStrategy, strategy_address)


def publish_sources(contract, address):
    info = contract.get_verification_info()

    try:
        contract.publish_source(contract.at(address))
    except:
        print(
            f"\nUnable to verify {info['contract_name']}! Use the 'verification_sources/{info['contract_name']}' folder to verify manually"
        )

        prepare_verification_sources(contract)
        print_verification_info(contract, address)


def print_verification_info(contract, address):
    info = contract.get_verification_info()
    print(f"\n***** {info['contract_name']} *****")
    print(f"Address: {address}")
    print(f"Compiler Version: {info['compiler_version']}")
    print(f"License Type: {info['license_identifier']}")
    print(f"Optimizer Enabled: {info['optimizer_enabled']}")
