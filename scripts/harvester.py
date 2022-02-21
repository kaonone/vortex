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
    if strategy.getFundingRate() > 0:
        strategy.harvest({"from": harvester})
        time.sleep(2)
        print("strategy harvested")
    else:
        strategy.unwind({"from": harvester})
        print("strategy unwind")
        print("funding rate negative , will try next 6 hours")
