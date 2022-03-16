import json
from brownie import chain


def get_utils_path():
    return f"addresses/{chain.id}/utils.json"


def get_vaults_path():
    return f"addresses/{chain.id}/vaults.json"


def get_deploy_config_path():
    return f"config/{chain.id}/deploy.json"


def get_utils_addresses():
    with open(get_utils_path(), "r", encoding="utf-8") as file:
        return json.load(file)


def get_deploy_config():
    with open(get_deploy_config_path(), "r", encoding="utf-8") as file:
        return json.load(file)


def get_vaults_addresses():
    with open(get_vaults_path(), "r", encoding="utf-8") as file:
        return json.load(file)

def get_latest_vault_addresses():
    addresses = get_vaults_addresses()
    vaults_len = len(addresses)
    return addresses[vaults_len - 1]


def set_create_call_contract(address):
    with open(get_utils_path(), "r+", encoding="utf-8") as file:
        data = json.load(file)

        data["create_call"] = address

        file.seek(0)
        json.dump(data, file, indent=2)


def set_vaults_registry_contract(address):
    with open(get_utils_path(), "r+", encoding="utf-8") as file:
        data = json.load(file)

        data["vaults_registry"] = address

        file.seek(0)
        json.dump(data, file, indent=2)


def add_vault_contract(vault_address, strategy_address):
    with open(get_vaults_path(), "r+", encoding="utf-8") as file:
        data = json.load(file)

        new_vault_data = {
            'vault': vault_address,
            'strategy': strategy_address,
        }

        data.append(new_vault_data)

        file.seek(0)
        json.dump(data, file, indent=2)
