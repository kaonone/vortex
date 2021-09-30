import pytest
import constants
from brownie import (
    BasisVault,
    BasicERC20, 
    TestStrategy,
    accounts,
    network,
    Contract,
    interface
)


@pytest.fixture(scope="function", autouse=True)
def isolate_func(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="function", autouse=True)
def token(deployer, users, usdc_whale):
    if network.show_active() == 'development':
        toke = BasicERC20.deploy("Test", "TT", {"from": deployer})
        toke.mint(1_000_000_000_000e18, {"from": deployer})
        for user in users:
            toke.mint(1_000_000e18, {"from": user})
    else:
        toke = interface.IERC20(constants.USDC)
        for user in users:
            toke.transfer(
                user,
                constants.DEPOSIT_AMOUNT * 10,
                {"from": usdc_whale}
            )
    # usdc
    yield toke

@pytest.fixture(scope="function")
def usdc_whale():
    yield accounts.at(constants.USDC_WHALE, force=True)


@pytest.fixture
def deployer(accounts):
    if network.show_active() == 'development':
        yield accounts[0]
    else:
        yield accounts.at(constants.USDC_WHALE, force=True)

@pytest.fixture
def governance(accounts):
    yield accounts[1]


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


@pytest.fixture(scope="function")
def vault_deposited(deployer, token, users, vault):
    for user in users:
        token.approve(vault, constants.DEPOSIT_AMOUNT, {"from": user})
        vault.deposit(constants.DEPOSIT_AMOUNT, user, {"from": user})
    yield vault


@pytest.fixture(scope="function")
def test_strategy(vault, deployer, governance):
    strategy = TestStrategy.deploy(
        constants.LONG_ASSET, 
        constants.UNI_POOL, 
        vault, 
        constants.MCDEX_ORACLE,
        constants.ROUTER, 
        governance,
        constants.MCLIQUIDITY, 
        constants.PERP_INDEX, 
        {"from": deployer}
    )
    strategy.setBuffer(constants.BUFFER, {"from": deployer})
    yield strategy
