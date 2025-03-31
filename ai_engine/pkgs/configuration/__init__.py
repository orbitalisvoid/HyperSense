__ALL__ = ["load_config"]

import yaml


def load_config(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
