import yaml
from app.data_access.primitives import get_relative_pathname_from_list

## IMPORTANT: In the unlikely event we move the config file, this needs changing
configuration_file = get_relative_pathname_from_list(
    ["app", "data_access", "configuration", "configuration.yaml"]
)

with open(configuration_file) as file_to_parse:
    configuration = yaml.load(file_to_parse, Loader=yaml.FullLoader)


## Get everything from config as constants.py

SECRET_KEY = configuration["secret_key"]

### directories
DATAPATH = configuration["datapath"]
BACKUP_DATA =configuration["backuppath"]
USER_DATA = configuration["userdata"]
UPLOADS = configuration["uploads"]
DOWNLOAD_DIRECTORY = configuration["download_subdirectory"]
PUBLIC_REPORTING_SUBDIRECTORY = configuration["public_reporting_subdirectory"]



NUMBER_OF_BACKUPS = configuration["number_of_backups_to_keep"]

## links
WEBLINK_FOR_QUALIFICATIONS = configuration["weblink_for_qualifications"]
PUBLIC_WEB_PATH = configuration["public_web_path"]
HOMEPAGE = configuration["homepage"]

SIMILARITY_LEVEL_TO_WARN_NAME = configuration[
    "similarity_level_to_warn_when_comparing_names"
]
SIMILARITY_LEVEL_TO_WARN_DATE = configuration[
    "similarity_level_to_warn_when_comparing_dates"
]

MIN_CADET_AGE = configuration["minimum_cadet_age"]
MAX_CADET_AGE = configuration["maximium_cadet_age"]

## WA
## Status of payment_status, used to determine cadet status
WA_ACTIVE_STATUS = configuration["wild_apricot_payment_fields_which_are_active_status"]
WA_CANCELLED_STATUS = configuration[
    "wild_apricot_payment_fields_which_are_cancelled_status"
]
WILD_APRICOT_EVENT_ID = configuration["wild_apricot_event_id"]
WILD_APRICOT_FILE_TYPES = configuration["wild_apricot_file_types"]
#
# File handling
## GROUPS
LAKE_TRAINING_GROUP_NAMES = configuration["lake_training_groups"]
RIVER_TRAINING_GROUP_NAMES = configuration["river_training_groups"]
MG_GROUP_NAMES = configuration["mg_groups"]
UNALLOCATED_GROUP_NAME = configuration["unallocated"]



ALL_GROUPS_NAMES = (
        LAKE_TRAINING_GROUP_NAMES + RIVER_TRAINING_GROUP_NAMES + MG_GROUP_NAMES + [UNALLOCATED_GROUP_NAME]
)

# VOLUNTEERS
VOLUNTEER_SKILLS = configuration['volunteer_skills']
VOLUNTEER_TEAMS = configuration['volunteer_teams']
VOLUNTEERS_SKILL_FOR_PB2 = configuration['power_boat_skills'][0]

VOLUNTEERS_REQUIRING_BOATS = configuration['volunteers_requiring_boats']


VOLUNTEERS_REQUIRING_GROUP = configuration['volunteers_requiring_group']

INSTRUCTOR_TEAM_NAME = configuration['instructor_team']
INSTRUCTOR_TEAM = VOLUNTEER_TEAMS[INSTRUCTOR_TEAM_NAME]
SI_ROLE = configuration['senior_instructor']

RIVER_SAFETY = 'River safety'
LAKE_SAFETY = 'Lake safety'

### si at an event can see all groups

## Page sizes - not configured in yaml as won't need changing
MAX_FILE_SIZE = configuration["max_file_size"]
UPLOAD_EXTENSIONS = configuration["upload_extensions"]


def DEPRECATE_get_volunteer_roles():
    ## FIXME REPLACE WITH CONFIGURABLE FILE in backend
    volunteer_roles = []
    for team in VOLUNTEER_TEAMS.values():
        for role in team:
            if role not in volunteer_roles:  ## avoids duplication eg deputy skipper while preserving order
                volunteer_roles.append(role)

    return volunteer_roles

VOLUNTEER_ROLES = DEPRECATE_get_volunteer_roles()

MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE = configuration['min_colour_groups_to_distribute']

UNABLE_TO_VOLUNTEER_KEYWORD = "unable"