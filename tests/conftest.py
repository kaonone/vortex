import pytest
import constants
from brownie import (
    BasisVault,
    BasicERC20
)


@pytest.fixture(scope="function", autouse=True)
def isolate_func(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="function", autouse=True)
def token(deployer, users):
    token = BasicERC20.deploy("Test", "TT", {"from": deployer})
    token.mint(1_000_000_000_000e18, {"from": deployer})
    for user in users:
        token.mint(1_000_000e18, {"from": user})
    yield token


@pytest.fixture
def deployer(accounts):
    yield accounts[0]


@pytest.fixture
def users(accounts):
    yield accounts[1:10]


@pytest.fixture(scope="function")
def vault(deployer, token):
    yield BasisVault.deploy(
        token,
        constants.DEPOSIT_LIMIT,
        {"from": deployer}
    )
