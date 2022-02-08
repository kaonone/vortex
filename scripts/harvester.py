import os
import scripts.constants_testnet
import time
from dotenv import load_dotenv, find_dotenv
from brownie import (
    accounts,
    interface,
)


def main():
    constant = scripts.constants_testnet
    load_dotenv(find_dotenv())
    admin_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    strategy = interface.IStrategy(constant.ADDRESS_STRATEGY)
    harvester = accounts.add(admin_key)
    # initialize strategy
    strategy.harvest({"from": harvester})
    time.sleep(2)
    print("strategy harvested")
