import pytest
import constants
import brownie
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
    token = Contract.from_explorer(
        "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",
        as_proxy_for="0x1eFB3f88Bc88f03FD1804A5C53b7141bbEf5dED8"
    )
    for user in users:
        token.transfer(
            user,
            constants.DEPOSIT_AMOUNT,
            {"from": usdc_whale}
        )
    # usdc
    yield token


@pytest.fixture(scope="function", autouse=True)
def deployer():
    accounts.default = accounts[0]
    yield accounts[0]


@pytest.fixture
def users(accounts):
    yield accounts[1:5]


@pytest.fixture
def usdc_whale():
    yield accounts.at("0x1f032a27b369299c73b331c9fc1e80978db45b15", force=True)


@pytest.fixture(scope="function", autouse=True)
def vault(token, deployer):
    bv = BasisVault.deploy(
        token.address,
        constants.DEPOSIT_LIMIT,
        {"from": deployer}
        )
    yield bv


@pytest.fixture(scope="function")
def vault_deposited(deployer, token, users, vault):
    for user in users:
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
    yield vault