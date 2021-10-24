import pytest
import constants
import constants_bsc
from brownie import (
    BasisVault,
    BasicERC20,
    TestStrategy,
    accounts,
    network,
    Contract,
    interface,
)


@pytest.fixture(scope="function", autouse=True)
def isolate_func(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="function", autouse=True)
def token(deployer, users, usdc_whale):
    constant = data()
    if network.show_active() == "development":
        toke = BasicERC20.deploy("Test", "TT", {"from": deployer})
        toke.mint(1_000_000_000_000e18, {"from": deployer})
        for user in users:
            toke.mint(1_000_000e18, {"from": user})
    else:
        toke = interface.IERC20(constant.USDC)
        for user in users:
            toke.transfer(user, constant.DEPOSIT_AMOUNT * 10, {"from": usdc_whale})
    # usdc
    yield toke

def data():
    if network.show_active() == "hardhat-arbitrum-fork":
        constant = constants
    else:
        constant = constants_bsc
    return constant

@pytest.fixture(scope="function", autouse=True)
def long():
    constant = data()
    toke = interface.IERC20(constant.LONG_ASSET)
    yield toke


@pytest.fixture(scope="function", autouse=True)
def oracle():
    constant = data()
    oracle = interface.IOracle(constant.MCDEX_ORACLE)
    yield oracle


@pytest.fixture(scope="function", autouse=True)
def mcLiquidityPool():
    constant = data()
    mc = interface.IMCLP(constant.MCLIQUIDITY)
    yield mc


@pytest.fixture(scope="function")
def usdc_whale():
    constant = data()
    yield accounts.at(constant.USDC_WHALE, force=True)


@pytest.fixture
def deployer(accounts):
    constant = data()
    if network.show_active() == "development":
        yield accounts[0]
    else:
        yield accounts.at(constant.USDC_WHALE, force=True)


@pytest.fixture
def governance(accounts):
    yield accounts[1]


@pytest.fixture
def users(accounts):
    yield accounts[1:10]


@pytest.fixture(scope="function")
def randy():
    yield accounts.at(constants.RANDOM, force=True)


@pytest.fixture(scope="function")
def vault(deployer, token):
    constant = data()
    vaulty = BasisVault.deploy({"from": deployer})
    vaulty.initialize(token, constant.DEPOSIT_LIMIT, {"from": deployer})
    yield vaulty


@pytest.fixture(scope="function")
def vault_deposited(deployer, token, users, vault):
    constant = data()
    for user in users:
        token.approve(vault, constant.DEPOSIT_AMOUNT, {"from": user})
        vault.deposit(constant.DEPOSIT_AMOUNT, user, {"from": user})
    yield vault


@pytest.fixture(scope="function")
def test_strategy(vault, deployer, governance):
    constant = data()
    strategy = TestStrategy.deploy(
        {"from": deployer},
    )
    strategy.init(
        constant.LONG_ASSET,
        constant.UNI_POOL,
        vault,
        constant.MCDEX_ORACLE,
        constant.ROUTER,
        governance,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.isV2,
        {"from": deployer} 
    )
    strategy.setBuffer(constant.BUFFER, {"from": deployer})
    vault.setStrategy(strategy, {"from": deployer})
    vault.setProtocolFees(2000, 100, {"from": deployer})
    yield strategy


@pytest.fixture(scope="function")
def test_strategy_deposited(vault_deposited, deployer, governance):
    constant = data()
    strategy = TestStrategy.deploy(
        {"from": deployer},
    )
    strategy.init(
        constant.LONG_ASSET,
        constant.UNI_POOL,
        vault_deposited,
        constant.MCDEX_ORACLE,
        constant.ROUTER,
        governance,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.isV2,
        {"from": deployer} 
    )
    strategy.setBuffer(constant.BUFFER, {"from": deployer})
    vault_deposited.setStrategy(strategy, {"from": deployer})
    strategy.setSlippageTolerance(constant.TRADE_SLIPPAGE, {"from": deployer})
    vault_deposited.setProtocolFees(2000, 200, {"from": deployer})
    yield strategy


@pytest.fixture(scope="function")
def test_other_strategy(token, deployer, governance, users):
    constant = data()
    vault_deploy = BasisVault.deploy({"from": deployer})
    vaulty = vault_deploy.initialize(token, constant.DEPOSIT_LIMIT, {"from": deployer})
    for user in users:
        token.approve(vaulty, constant.DEPOSIT_AMOUNT, {"from": user})
        vaulty.deposit(constant.DEPOSIT_AMOUNT, user, {"from": user})
    strategy = TestStrategy.deploy(
        {"from": deployer},
    )
    strategy.init(
        constant.LONG_ASSET,
        constant.UNI_POOL,
        vaulty.address,
        constant.MCDEX_ORACLE,
        constant.ROUTER,
        governance,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.isV2,
        {"from": deployer} 
    )
    strategy.setBuffer(constant.BUFFER, {"from": deployer})
    vaulty.setStrategy(strategy, {"from": deployer})
    strategy.setSlippageTolerance(constant.TRADE_SLIPPAGE, {"from": deployer})
    yield strategy
