import os

import yaml

from app.data_access.configuration.configuration import DATAPATH

home_directory = os.path.expanduser("~")
master_data_path = os.path.join(home_directory, DATAPATH)

GROUP_CONFIG_YAML_FILE = 'groups.yaml'
groups_config_filename = os.path.join(master_data_path, GROUP_CONFIG_YAML_FILE)


with open(groups_config_filename) as file_to_parse:
    configuration = yaml.load(file_to_parse, Loader=yaml.FullLoader)

LAKE_TRAINING_GROUP_NAMES = configuration["lake_training_groups"]
RIVER_TRAINING_GROUP_NAMES = configuration["river_training_groups"]
MG_GROUP_NAMES = configuration["mg_groups"]
UNALLOCATED_GROUP_NAME = configuration["unallocated"]
ALL_GROUPS_NAMES = (
    LAKE_TRAINING_GROUP_NAMES
    + RIVER_TRAINING_GROUP_NAMES
    + MG_GROUP_NAMES
    + [UNALLOCATED_GROUP_NAME]
)
