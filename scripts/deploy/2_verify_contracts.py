from scripts.utils.constants import set_vaults_registry_contract, add_vault_contract
from scripts.utils.prepare_verification_sources import prepare_verification_sources
from brownie import (
    VaultRegistry,
    BasisVault,
    BasisStrategy,
    chain,
)

DEPLOY_TX_HASH = ""


def main():
    tx = chain.get_transaction(DEPLOY_TX_HASH)

    deploy_events = list(filter(lambda event: "newContract" in event, tx.events))
    contracts_len = len(deploy_events)
    shift = 0

    if contracts_len == 3:
        registry_address = deploy_events[0]["newContract"]
        set_vaults_registry_contract(registry_address)
        shift = 1

    vault_address = deploy_events[shift]["newContract"]
    strategy_address = deploy_events[shift + 1]["newContract"]
    add_vault_contract(vault_address, strategy_address)

    try:
        if registry_address:
            registry = VaultRegistry.at(registry_address)
            VaultRegistry.publish_source(registry)

        vault = BasisVault.at(vault_address)
        BasisVault.publish_source(vault)

        strategy = BasisStrategy.at(strategy_address)
        BasisStrategy.publish_source(strategy)
    except:
        print(
            "Unable to verify contracts automatically, try to verify manually using sources from the verification_sources folder"
        )

        if registry_address:
            prepare_verification_sources(VaultRegistry)
            print_verification_info(VaultRegistry, registry_address)

        prepare_verification_sources(BasisVault)
        prepare_verification_sources(BasisStrategy)

        print_verification_info(BasisVault, vault_address)
        print_verification_info(BasisStrategy, strategy_address)


def print_verification_info(contract, address):
    info = contract.get_verification_info()
    print(f"\n***** {info['contract_name']} *****")
    print(f"Address: {address}")
    print(f"Compiler Version: {info['compiler_version']}")
    print(f"License Type: {info['license_identifier']}")
    print(f"Optimizer Enabled: {info['optimizer_enabled']}")
