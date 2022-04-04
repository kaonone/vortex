from ape_safe import ApeSafe
from scripts.utils.constants import (
    get_utils_addresses,
    get_latest_vault_addresses,
    get_deploy_config,
)
from brownie import (
    Contract,
    VaultRegistry,
    BasisVault,
    BasisStrategy,
    KeeperManager,
    accounts,
    interface,
    web3,
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

    if registry.owner() == ZERO_ADDRESS:
        registry.initialize({"from": safe.account})

    registry.registerVault(vault_address, {"from": safe.account})

    want_token = interface.ERC20(deploy_config["want_token"])
    want_token_decimals = want_token.decimals()

    vault.initialize(
        deploy_config["want_token"],
        with_decimals(deploy_config["deposit_limit"], want_token_decimals),
        with_decimals(deploy_config["individual_deposit_limit"], want_token_decimals),
        deploy_config["performance_fee"],
        deploy_config["management_fee"],
        {"from": safe.account},
    )
    vault.setStrategy(strategy_address, {"from": safe.account})
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

    strategy.setKeeper(utils_addresses["keeper_address"], {"from": safe.account})
    # TODO: check and update addresses
    strategy.setReferrer(utils_addresses["gnosis_safe"], {"from": safe.account})
    strategy.setLmClaimerAndMcb(ZERO_ADDRESS, ZERO_ADDRESS, {"from": safe.account})

    if deploy_config["use_alchemy_keeper"]:
        keeper = KeeperManager.at(utils_addresses["keeper_address"])

        if keeper.owner() == ZERO_ADDRESS:
            keeper.initialize(
                deploy_config["keeper_cooldown"],
                utils_addresses["upkeep_registry"],
                {"from": safe.account},
            )

        register_alchemy_upkeep(
            safe.account,
            utils_addresses["keeper_address"],
            strategy_address,
            f"Vortex Keeper {vault.symbol()}",
        )

    safe_tx = safe.multisend_from_receipts()

    # estimated_gas = safe.estimate_gas(safe_tx)
    # print(f"Estimated gas: {estimated_gas}")

    # safe.preview(safe_tx, call_trace=True)

    safe.post_transaction(safe_tx)


def register_alchemy_upkeep(
    safe_account, upkeep_address, strategy_address, upkeep_name
):
    utils_addresses = get_utils_addresses()

    registry = Contract.from_explorer(utils_addresses["upkeep_registry"])
    link_address = registry.LINK()
    registar_address = registry.getRegistrar()

    link = Contract.from_explorer(link_address)
    first_link_funding = with_decimals(10, link.decimals())

    if link.balanceOf(safe_account.address) < first_link_funding:
        raise Exception(
            f"Not enough LINK tokens on Safe account {safe_account.address}"
        )

    registar = Contract.from_explorer(registar_address)

    # encrypted team@akropolis.io
    encrypted_email = "0x53636aa464b01c808a1e950140569f4bb02a76adf5a847fe90af307782d8264248a05f3821f9f18d5b6e2f64e71a225ccc86a632e8e8d40c5921695029c419ca17f6335eff833a426862c411124554c6bb8835f64928d1eddb"
    gas_limit = 2000000
    upkeep_admin = safe_account.address
    check_data = f"0x{web3.eth.codec.encode_abi(['address'], [strategy_address]).hex()}"
    app_id = 97
    register_calldata = registar.register.encode_input(
        upkeep_name,
        encrypted_email,
        upkeep_address,
        gas_limit,
        upkeep_admin,
        check_data,
        first_link_funding,
        app_id,
    )

    link.transferAndCall(
        utils_addresses["upkeep_registration_request"],
        first_link_funding,
        register_calldata,
        {"from": safe_account},
    )


def with_decimals(value, decimals):
    return value * 10**decimals
