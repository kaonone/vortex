from ape_safe import ApeSafe
from scripts.utils.constants import get_utils_addresses
from brownie import (
    VaultRegistry,
    BasisVault,
    CreateCall,
    BasisStrategy,
    accounts,
)


def main():
    accounts.clear()
    accounts.load("vortex_deployer")

    utils_addresses = get_utils_addresses()

    safe = ApeSafe(utils_addresses["gnosis_safe"])

    create_call = CreateCall.at(utils_addresses["create_call"])

    if not utils_addresses["vaults_registry"]:
        registry_bytecode = VaultRegistry.deploy.encode_input()
        create_call.performCreate(0, registry_bytecode, {"from": safe.account})

    vault_bytecode = BasisVault.deploy.encode_input()
    strategy_bytecode = BasisStrategy.deploy.encode_input()

    create_call.performCreate(0, vault_bytecode, {"from": safe.account})
    create_call.performCreate(0, strategy_bytecode, {"from": safe.account})

    safe_tx = safe.multisend_from_receipts()

    # estimated_gas = safe.estimate_gas(safe_tx)
    # print(f"Estimated gas: {estimated_gas}")

    # safe.preview(safe_tx, call_trace=True)

    safe.post_transaction(safe_tx)
