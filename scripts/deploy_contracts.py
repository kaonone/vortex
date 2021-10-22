import pytest
import constants_bsc
import constants_arb
from brownie import (
    BasisVault,
    BasicERC20,
    TestStrategy,
    accounts,
    network,
    Contract,
    interface,
)

from tests.test_arbitrum.conftest import mcLiquidityPool


def main():
    if network.show_active() == "hardhat-arbitrum-fork":
        constants = constants_arb
    else:
        constants = constants_bsc
    
    mcLiquidityPool = interface.IMLCP(constants.MCLIQUIDITY)