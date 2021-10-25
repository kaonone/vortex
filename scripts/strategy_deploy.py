import os
import scripts.constants
import scripts.constants_bsc
import time
from dotenv import load_dotenv, find_dotenv

from utils.deploy_helpers import (
    deploy_proxy,
    deploy_admin,
    get_proxy_admin,
    upgrade_proxy,
)

from brownie import (
    BasisVault,
    BasicERC20,
    BasisStrategy,
    accounts,
    network,
    Contract,
    interface,
)


def data():
    if network.show_active() == "hardhat-arbitrum-fork":
        constant = scripts.constants
    else:
        constant = scripts.constants_bsc
    return constant


def main():
    constant = data()
    load_dotenv(find_dotenv())
    print(f"You are using the '{network.show_active()}' network")
    if network.show_active() == "development":
        deployer = accounts[0]
        proxy_admin = accounts[1]
    else:
        deployer = accounts.add(os.getenv("DEPLOYER_PRIVATE_KEY"))
        admin_key = os.getenv("ADMIN_PRIVATE_KEY")
        proxy_admin_address = os.getenv("PROXY_ADMIN_ADDRESS")
        admin_key = os.getenv("ADMIN_PRIVATE_KEY")
        proxy_admin_address = os.getenv("PROXY_ADMIN_ADDRESS")
        if admin_key:
            proxy_admin = accounts.add(admin_key)
        elif proxy_admin_address:
            proxy_admin = get_proxy_admin(proxy_admin_address)
        else:
            proxy_admin = deploy_admin(deployer)
        print(f"You are using: 'deployer' [{deployer.address}]")
        print(f"Proxy Admin at {proxy_admin.address}")

    token = interface.IERC20(constant.USDC)
    (
        vault_implementation_proxy,
        vault_proxy_contract,
        vault_contract_impl,
    ) = deploy_proxy(deployer, proxy_admin, BasisVault, token, constant.DEPOSIT_LIMIT)

    print(f"vault implementation proxy at {vault_implementation_proxy}")
    print(f"vault proxy contract at {vault_proxy_contract}")
    print(f"vault implementation contract at {vault_contract_impl}")

    time.sleep(3)

    (
        strategy_implementation_proxy,
        strategy_proxy_contract,
        strategy_contract_impl,
    ) = deploy_proxy(
        deployer,
        proxy_admin,
        BasisStrategy,
        constant.LONG_ASSET,
        constant.UNI_POOL,
        vault_contract_impl,  # constant vault
        constant.MCDEX_ORACLE,
        constant.ROUTER,
        constant.GOVERNANCE,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.isV2,
    )

    print(f"strategy implementation proxy at {strategy_implementation_proxy}")
    print(f"strategy proxy contract at {strategy_proxy_contract}")
    print(f"strategy implementation contract at {strategy_contract_impl}")

    time.sleep(2)
