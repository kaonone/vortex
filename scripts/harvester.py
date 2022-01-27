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
    admin_key = os.getenv("ADMIN_PRIVATE_KEY")
    strategy = interface.IStrategy(constant.ADDRESS_STRATEGY)
    harvester = accounts.add(admin_key)
    strategy.harvest({"from": harvester})
    time.sleep(2)
    print("strategy harvested")