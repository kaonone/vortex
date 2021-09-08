import pytest
import constants
from brownie import (
    BasisVault,
    BasicERC20,
    Contract,
    accounts
)


@pytest.fixture(scope="function", autouse=True)
def isolate_func(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="function", autouse=True)
def token(deployer, users, usdc_whale):
    # usdc
    token = Contract.from_explorer("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    for user in users:
        token.transfer(user, 100_000e18, {"from": usdc_whale})
    yield token


@pytest.fixture
def deployer(accounts):
    yield accounts[0]


@pytest.fixture
def users(accounts):
    yield accounts[1:10]


@pytest.fixture
def usdc_whale():
    yield accounts.at("0xAe2D4617c862309A3d75A0fFB358c7a5009c673F", force=True)


@pytest.fixture(scope="function")
def vault(deployer, token):
    yield BasisVault.deploy(
        token,
        constants.DEPOSIT_LIMIT,
        {"from": deployer}
    )


@pytest.fixture(scope="function")
def vault_deposited(deployer, token, users, vault):
    for user in users:
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
    yield vault