import os
import scripts.constants_testnet
import time
from dotenv import load_dotenv, find_dotenv
from brownie import (
    BasisVault,
    BasicERC20,
    BasisStrategy,
    accounts,
    network,
    Contract,
    interface,
)


def main():
    constant = scripts.constants_testnet
    load_dotenv(find_dotenv())
    print(f"You are using the '{network.show_active()}' network")
    if network.show_active() == "development":
        deployer = accounts[0]
        proxy_admin = accounts[1]
    else:
        deployer = accounts.add(os.getenv("DEPLOYER_PRIVATE_KEY"))

    # deploy the strat
    strategy = BasisStrategy.deploy({"from": deployer})
    print(f"strategy address {strategy.address}")
    # initialize the strategy
    strategy.initialize(
        constant.LONG_ASSET,
        constant.UNI_POOL,
        constant.VAULT_DEPLOYED,
        constant.ROUTER,
        constant.WETH,
        constant.GOVERNANCE,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.BUFFER,
        constant.isV2,
        {"from": deployer},
    )
    # strategy = interface.IStrategy(constant.ADDRESS_STRATEGY)
    strategy.setKeeper(deployer, {"from": deployer})
    print(f"keeper set to {deployer}")
