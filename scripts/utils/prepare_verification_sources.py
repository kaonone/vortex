import os
import shutil


def get_output_path(contract):
    info = contract.get_verification_info()
    return f"verification_sources/{info['contract_name']}"


def clean_folder(path):
    try:
        shutil.rmtree(path)
    except:
        pass


def prepare_verification_sources(contract):
    output_path = get_output_path(contract)
    clean_folder(output_path)
    os.makedirs(output_path, exist_ok=True)

    info = contract.get_verification_info()

    for key, value in info["standard_json_input"]["sources"].items():
        with open(f"{output_path}/{key}", "x", encoding="utf-8") as file:
            file.write(value["content"])
