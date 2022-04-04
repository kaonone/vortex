from brownie import accounts, CreateCall
from scripts.utils.constants import set_create_call_contract


def main():
    accounts.clear()
    deployer = accounts.load("vortex_deployer")

    contract = CreateCall.deploy({"from": deployer}, publish_source=True)

    set_create_call_contract(contract.address)
