import os
import scripts.constants
import scripts.constants_bsc
import time
from dotenv import load_dotenv, find_dotenv
from brownie import (
    BasisVault,
    BasicERC20,
    TestStrategy,
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
    load_dotenv(find_dotenv())
    constant = data()
    if network.show_active() == "development":
        deployer = accounts[0]
    else:
        deployer = accounts.add(os.getenv("DEPLOYER_PRIVATE_KEY"))
    token = interface.IERC20(constant.USDC)
    
    vault = BasisVault.deploy(token, constant.DEPOSIT_LIMIT, {"from": deployer})

    strategy = TestStrategy.deploy(
        constant.LONG_ASSET,
        constant.UNI_POOL,
        vault,
        constant.MCDEX_ORACLE,
        constant.ROUTER,
        constant.GOVERNANCE,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.isV2,

        {"from": deployer},
    )
    strategy.setBuffer(constant.BUFFER, {"from": deployer})
    vault.setStrategy(strategy, {"from": deployer})
    vault.setProtocolFees(2000, 100, {"from": deployer})

    print(f"vault is deployed to address {vault.address}")
    print(f"strategy is deployed to address {strategy.address}")

    time.sleep(10)

    
