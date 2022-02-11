import os
import scripts.constants
import time
from dotenv import load_dotenv, find_dotenv
from brownie import (
    accounts,
    interface,
)


def main():
    constant = scripts.constants
    load_dotenv(find_dotenv())
    admin_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    strategy = interface.IStrategy(constant.STRATEGY_ADDRESS)
    harvester = accounts.add(admin_key)
    # initialize strategy
    strategy.harvest({"from": harvester})
    time.sleep(2)
    print("strategy harvested")
