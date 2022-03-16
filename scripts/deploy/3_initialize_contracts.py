from ape_safe import ApeSafe
from scripts.utils.constants import (
    get_utils_addresses,
    get_latest_vault_addresses,
    get_deploy_config,
)
from brownie import (
    VaultRegistry,
    BasisVault,
    BasisStrategy,
    accounts,
    interface,
)

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def main():
    accounts.clear()
    deployer = accounts.load("vortex_deployer")

    utils_addresses = get_utils_addresses()
    vault_addresses = get_latest_vault_addresses()
    deploy_config = get_deploy_config()

    vault_address = vault_addresses["vault"]
    strategy_address = vault_addresses["strategy"]

    safe = ApeSafe(utils_addresses["gnosis_safe"])

    registry = VaultRegistry.at(utils_addresses["vaults_registry"])
    vault = BasisVault.at(vault_address)
    strategy = BasisStrategy.at(strategy_address)

    registry_owner = registry.owner()

    if registry_owner == ZERO_ADDRESS:
        registry.initialize({"from": safe.account})

    registry.registerVault(vault_address, {"from": safe.account})

    want_token = interface.ERC20(deploy_config["want_token"])
    want_token_decimals = want_token.decimals()

    vault.initialize(
        deploy_config["want_token"],
        with_decimals(deploy_config["deposit_limit"], want_token_decimals),
        with_decimals(deploy_config["individual_deposit_limit"], want_token_decimals),
        {"from": safe.account},
    )
    vault.setStrategy(strategy_address, {"from": safe.account})
    # TODO: move fee params to initialize
    vault.setProtocolFees(
        deploy_config["performance_fee"],
        deploy_config["management_fee"],
        {"from": safe.account},
    )
    vault.setProtocolFeeRecipient(
        utils_addresses["gnosis_safe"], {"from": safe.account}
    )

    strategy.initialize(
        deploy_config["long_asset"],
        deploy_config["uniswap_pool"],
        vault_address,
        deploy_config["uniswap_router"],
        deploy_config["WETH"],
        utils_addresses["gnosis_safe"],
        deploy_config["mc_liquidity_pool"],
        deploy_config["perpetual_index"],
        deploy_config["buffer"],
        deploy_config["is_v2_router"],
        {"from": safe.account},
    )

    # TODO: check and update addresses
    strategy.setReferrer(utils_addresses["gnosis_safe"], {"from": safe.account})
    strategy.setKeeper(deployer.address, {"from": safe.account})
    strategy.setLmClaimerAndMcb(ZERO_ADDRESS, ZERO_ADDRESS, {"from": safe.account})

    safe_tx = safe.multisend_from_receipts()

    # estimated_gas = safe.estimate_gas(safe_tx)
    # print(f"Estimated gas: {estimated_gas}")

    # safe.preview(safe_tx, call_trace=True)

    safe.post_transaction(safe_tx)


def with_decimals(value, decimals):
    return value * 10**decimals
