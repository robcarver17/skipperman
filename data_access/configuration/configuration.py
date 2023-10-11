import yaml
from data_access.configuration.file_access import get_relative_pathname_from_list

## IMPORTANT: In the unlikely event we move the config file, this needs changing
configuration_file = get_relative_pathname_from_list(
    ["data_access", "configuration", "configuration.yaml"]
)

with open(configuration_file) as file_to_parse:
    configuration = yaml.load(file_to_parse, Loader=yaml.FullLoader)

SIMILARITY_LEVEL_TO_WARN_NAME = configuration[
    "similarity_level_to_warn_when_comparing_cadet_names"
]
SIMILARITY_LEVEL_TO_WARN_AGE = configuration[
    "similarity_level_to_warn_when_comparing_cadet_ages"
]

MIN_CADET_AGE = configuration["minimum_cadet_age"]
MAX_CADET_AGE = configuration["maximium_cadet_age"]

## Status of payment_status, used to determine cadet status
ACTIVE_STATUS = configuration["wild_apricot_payment_fields_which_are_active_status"]
CANCELLED_STATUS = configuration[
    "wild_apricot_payment_fields_which_are_cancelled_status"
]

## GROUPS
LAKE_TRAINING_GROUPS = configuration["lake_training_groups"]
RIVER_TRAINING_GROUPS = configuration["river_training_groups"]
MG_GROUPS = configuration["mg_groups"]
