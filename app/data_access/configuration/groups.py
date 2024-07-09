import os
from dataclasses import dataclass
from typing import List

import yaml

from app.data_access.configuration.configuration import DATAPATH

home_directory = os.path.expanduser("~")
master_data_path = os.path.join(home_directory, DATAPATH)

GROUP_CONFIG_YAML_FILE = 'groups.yaml'
groups_config_filename = os.path.join(master_data_path, GROUP_CONFIG_YAML_FILE)




@dataclass
class GroupConfiguration:
    lake_training_group_names: List[str]
    river_training_group_names: List[str]
    mg_group_names: List[str]

    def save_to_filename(self, filename:str):
        with open(filename, 'w') as file_to_parse:
            yaml.dump(self.self_as_dict(), file_to_parse)

    def all_groups(self) ->List[str]:
        return \
        self.lake_training_group_names+\
         self.river_training_group_names+\
         self.mg_group_names+\
         [self.unallocated_group_name]

    @classmethod
    def get_from_filename(cls, filename:str):
        with open(groups_config_filename) as file_to_parse:
            group_configuration = yaml.load(file_to_parse, Loader=yaml.FullLoader)

        return cls(
            lake_training_group_names=group_configuration["lake_training_groups"],
            river_training_group_names=group_configuration["river_training_groups"],
            mg_group_names=group_configuration["mg_groups"]
        )

    def self_as_dict(self):
        return dict(
            lake_training_groups= self.lake_training_group_names,
        river_training_groups = self.river_training_group_names,
            mg_groups = self.mg_group_names
        )

    @property
    def unallocated_group_name(self):
        unallocated_group_name = "Unallocated"  ## FIXED DO NOT CHANGE

        return unallocated_group_name

def save_group_configuration_to_file(group_configuration: GroupConfiguration):
    group_configuration.save_to_filename(groups_config_filename)

group_configuration = GroupConfiguration.get_from_filename(groups_config_filename)

lake_training_group_names = group_configuration.lake_training_group_names
river_training_group_names = group_configuration.river_training_group_names
mg_group_names = group_configuration.mg_group_names
unallocated_group_name = group_configuration.unallocated_group_name
all_groups_names = group_configuration.all_groups()


