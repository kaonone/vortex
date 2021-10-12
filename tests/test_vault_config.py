import brownie
import constants
import random


def test_vault_deployment(BasisVault, deployer):
    vault = BasisVault.deploy(
        constants.USDC, constants.DEPOSIT_LIMIT, {"from": deployer}
    )
    assert vault.owner() == deployer
    assert vault.want() == constants.USDC
    assert vault.depositLimit() == constants.DEPOSIT_LIMIT

    assert vault.name() == "akBVUSDC-ETH"
    assert vault.symbol() == "akBasisVault-USDC-ETH"

    assert vault.totalLent() == 0
    assert vault.managementFee() == constants.MANAGEMENT_FEE
    assert vault.performanceFee() == constants.PERFORMANCE_FEE
    assert vault.totalAssets() == 0
    assert vault.pricePerShare() == 1
    assert vault.strategy() == brownie.ZERO_ADDRESS


def test_vault_set_non_strat_params(BasisVault, deployer, accounts):
    vault = BasisVault.deploy(
        constants.USDC, constants.DEPOSIT_LIMIT, {"from": deployer}
    )
    with brownie.reverts():
        vault.setDepositLimit(0, {"from": accounts[9]})
    tx = vault.setDepositLimit(0, {"from": deployer})
    assert vault.depositLimit() == 0
    assert "DepositLimitUpdated" in tx.events
    assert tx.events["DepositLimitUpdated"]["depositLimit"] == 0

    with brownie.reverts():
        vault.setProtocolFees(1, 1, {"from": accounts[9]})
    tx = vault.setProtocolFees(1, 1, {"from": deployer})
    assert vault.managementFee() == 1
    assert vault.performanceFee() == 1
    assert "ProtocolFeesUpdated" in tx.events
    assert (
        tx.events["ProtocolFeesUpdated"]["oldManagementFee"] == constants.MANAGEMENT_FEE
    )
    assert (
        tx.events["ProtocolFeesUpdated"]["oldPerformanceFee"]
        == constants.PERFORMANCE_FEE
    )
    assert tx.events["ProtocolFeesUpdated"]["newManagementFee"] == 1
    assert tx.events["ProtocolFeesUpdated"]["newPerformanceFee"] == 1


def test_vault_add_strategy(BasisVault, BasisStrategy, deployer, accounts):
    vault = BasisVault.deploy(
        constants.USDC, constants.DEPOSIT_LIMIT, {"from": deployer}
    )
    strategy = BasisStrategy.deploy(
        constants.LONG_ASSET,
        constants.UNI_POOL,
        vault,
        constants.MCDEX_ORACLE,
        constants.ROUTER,
        deployer,
        constants.MCLIQUIDITY,
        constants.PERP_INDEX,
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
