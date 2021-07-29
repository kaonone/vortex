from brownie import *
from config import (
  BADGER_DEV_MULTISIG,
  WANT,
  LP_COMPONENT,
  REWARD_TOKEN,
  DEFAULT_GOV_PERFORMANCE_FEE,
  DEFAULT_PERFORMANCE_FEE,
  DEFAULT_WITHDRAWAL_FEE
)
from dotmap import DotMap
from scripts.deploy import deploy
import pytest

@pytest.fixture
def tokens():
  return [WANT, LP_COMPONENT, REWARD_TOKEN]

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
def strategy(deployed):
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


      
