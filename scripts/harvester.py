import os
import scripts.constants
import time
from dotenv import load_dotenv, find_dotenv
from brownie import accounts, BasisStrategy


def main():
    constant = scripts.constants
    load_dotenv(find_dotenv())
    admin_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    strategy = BasisStrategy.at(constant.STRATEGY_ADDRESS)
    harvester = accounts.add(admin_key)
    if strategy.getFundingRate() > 0:
        strategy.harvest({"from": harvester})
        time.sleep(2)
        print("strategy harvested")
    elif strategy.isUnwind() == False:
        strategy.unwind({"from": harvester})
        print("strategy unwound")
    else:
        print("trying next 6 hours")
