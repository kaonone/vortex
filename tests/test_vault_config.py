import brownie
import constants
import constants_bsc
import random
from brownie import network


def data():
    if network.show_active() == "hardhat-arbitrum-fork":
        constant = constants
    else:
        constant = constants_bsc
    return constant


def test_vault_deployment(BasisVault, deployer, token):
    constant = data()
    vault = BasisVault.deploy({"from": deployer})
    vault.initialize(constant.USDC, constant.DEPOSIT_LIMIT, constant.INDIVIDUAL_DEPOSIT_LIMIT, {"from": deployer})
    assert vault.owner() == deployer
    assert vault.want() == constant.USDC
    assert vault.depositLimit() == constant.DEPOSIT_LIMIT

    assert vault.name() == "akBVUSDC-ETH"
    assert vault.symbol() == "akBasisVault-USDC-ETH"

    assert vault.totalLent() == 0
    assert vault.managementFee() == constant.MANAGEMENT_FEE
    assert vault.performanceFee() == constant.PERFORMANCE_FEE
    assert vault.pricePerShare() == constant.DECIMAL
    assert vault.decimals() == constant.VALUE_DEC
    assert vault.totalAssets() == 0
    assert vault.strategy() == brownie.ZERO_ADDRESS


def test_vault_set_non_strat_params(BasisVault, deployer, accounts):
    constant = data()
    vault = BasisVault.deploy({"from": deployer})
    vault.initialize(constant.USDC, constant.DEPOSIT_LIMIT, constant.INDIVIDUAL_DEPOSIT_LIMIT, {"from": deployer})
    with brownie.reverts():
        vault.setDepositLimit(0, {"from": accounts[9]})
    tx = vault.setDepositLimit(0, {"from": deployer})
    assert vault.depositLimit() == 0
    assert "DepositLimitUpdated" in tx.events
    assert tx.events["DepositLimitUpdated"]["depositLimit"] == 0

    with brownie.reverts():
        vault.setProtocolFees(1, 1, {"from": accounts[9]})
    with brownie.reverts("!_performanceFee"):
        vault.setProtocolFees(10_001, 0, {"from": deployer})
    with brownie.reverts("!_managementFee"):
        vault.setProtocolFees(0, 10_001, {"from": deployer})
    tx = vault.setProtocolFees(1, 1, {"from": deployer})
    assert vault.managementFee() == 1
    assert vault.performanceFee() == 1
    assert "ProtocolFeesUpdated" in tx.events
    assert (
        tx.events["ProtocolFeesUpdated"]["oldManagementFee"] == constant.MANAGEMENT_FEE
    )
    assert (
        tx.events["ProtocolFeesUpdated"]["oldPerformanceFee"]
        == constant.PERFORMANCE_FEE
    )
    assert tx.events["ProtocolFeesUpdated"]["newManagementFee"] == 1
    assert tx.events["ProtocolFeesUpdated"]["newPerformanceFee"] == 1


def test_vault_add_strategy(BasisVault, BasisStrategy, deployer, accounts):
    constant = data()
    vault = BasisVault.deploy({"from": deployer})
    vault.initialize(constant.USDC, constant.DEPOSIT_LIMIT, constant.INDIVIDUAL_DEPOSIT_LIMIT, {"from": deployer})
    strategy = BasisStrategy.deploy({"from": deployer})
    strategy.initialize(
        constant.LONG_ASSET,
        constant.UNI_POOL,
        vault,
        constant.ROUTER,
        constant.WETH,
        deployer,
        constant.MCLIQUIDITY,
        constant.PERP_INDEX,
        constant.BUFFER,
        constant.isV2,
        {"from": deployer},
    )
    with brownie.reverts():
        vault.setStrategy(strategy, {"from": accounts[9]})
    with brownie.reverts():
        vault.setStrategy(brownie.ZERO_ADDRESS, {"from": deployer})
    tx = vault.setStrategy(strategy, {"from": deployer})
    assert vault.strategy() == strategy
    assert "StrategyUpdated" in tx.events
    assert tx.events["StrategyUpdated"]["strategy"] == strategy


def test_pause_unpause(vault, deployer, randy):
    with brownie.reverts():
        vault.pause({"from": randy})
    with brownie.reverts():
        vault.unpause({"from": deployer})
    vault.pause({"from": deployer})
    assert vault.paused() == True
    with brownie.reverts():
        vault.pause({"from": deployer})
    with brownie.reverts():
        vault.unpause({"from": randy})
    vault.unpause({"from": deployer})
    assert vault.paused() == False
