from brownie import *
from config import (
    BADGER_DEV_MULTISIG,
    WANT,
    # LP_COMPONENT,
    REWARD_TOKEN,
    DEFAULT_GOV_PERFORMANCE_FEE,
    DEFAULT_PERFORMANCE_FEE,
    DEFAULT_WITHDRAWAL_FEE,
)
from dotmap import DotMap
from scripts.deploy import deploy
import pytest


@pytest.fixture
def tokens():
    return [WANT, REWARD_TOKEN]  # , LP_COMPONENT


@pytest.fixture
def deployed():
    """
    Deploys, vault, controller and strats and wires them up for you to test
    """
    return deploy()


## Fixtures from deploy, because it's cleaner

## Contracts ##


@pytest.fixture
def vault(deployed):
    return deployed.vault


@pytest.fixture
def sett(deployed):
    return deployed.sett


@pytest.fixture
def controller(deployed):
    return deployed.controller


@pytest.fixture
def strategy(interface, deployed):
    weth_sushi_slp_vault = SettV4.at(deployed.strategy.WETH_SUSHI_SLP_VAULT())
    weth_sushi_slp_vault.approveContractAccess(
        deployed.strategy, {"from": weth_sushi_slp_vault.governance()}
    )
    return deployed.strategy


## Tokens ##


@pytest.fixture
def want(deployed):
    return deployed.want


## Accounts ##


@pytest.fixture
def deployer(deployed):
    return deployed.deployer


@pytest.fixture
def strategist(strategy):
    return accounts.at(strategy.strategist(), force=True)


@pytest.fixture
def settKeeper(vault):
    return accounts.at(vault.keeper(), force=True)


@pytest.fixture
def strategyKeeper(strategy):
    return accounts.at(strategy.keeper(), force=True)


## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
