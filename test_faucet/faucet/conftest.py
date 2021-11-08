import pytest
from brownie import BasicERC20, Faucet, accounts


@pytest.fixture(scope="function", autouse=True)
def isolate_func(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="function", autouse=True)
def token(deployer, users):
    toke = BasicERC20.deploy("Test", "TT", {"from": deployer})
    toke.mint(1_000_000_000_000e18, {"from": deployer})
    yield toke


@pytest.fixture(scope="function")
def faucet(deployer, token):
    faucet_deployed = Faucet.deploy(token, 10_000e18, {"from": deployer})
    yield faucet_deployed


@pytest.fixture
def deployer(accounts):
    yield accounts[0]


@pytest.fixture
def users(accounts):
    yield accounts[1:10]
