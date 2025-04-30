import yaml
import pytz
from app.data_access.file_access import get_relative_pathname_from_list
from app.objects.skill_import import from_skills_dict_in_import_config_to_import_config

## IMPORTANT: In the unlikely event we move the config file, this needs changing
configuration_file = get_relative_pathname_from_list(
    ["app", "data_access", "configuration", "configuration.yaml"]
)

with open(configuration_file) as file_to_parse:
    configuration = yaml.load(file_to_parse, Loader=yaml.FullLoader)


### directories
DATAPATH = configuration["datapath"]
BACKUP_DATA = configuration["backuppath"]
USER_DATA = configuration["userdata"]
UPLOADS = configuration["uploads"]
DOWNLOAD_DIRECTORY = configuration["download_subdirectory"]
PUBLIC_REPORTING_SUBDIRECTORY = configuration["public_reporting_subdirectory"]

## backups
NUMBER_OF_BACKUPS = configuration["number_of_backups_to_keep"]

## links
WEBLINK_FOR_QUALIFICATIONS = configuration["weblink_for_qualifications"]
HOMEPAGE = configuration["homepage"]
PUBLIC_WEB_PATH = "%s/%s/" % (HOMEPAGE, PUBLIC_REPORTING_SUBDIRECTORY)

## Cadets
SIMILARITY_LEVEL_TO_WARN_NAME = configuration[
    "similarity_level_to_warn_when_comparing_names_on_event_import"
]
SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_FIRST_NAMES = configuration[
    "similarity_level_to_match_a_very_similar_cadet_first_name_on_event_import"
]
SIMILARITY_LEVEL_TO_WARN_NAME_ON_MATCHING_MEMBERSHIP_LIST = configuration[
    "similarity_level_to_warn_when_comparing_names_in_membership_list"
]

## Volunteers
SIMILARITY_LEVEL_TO_WARN_VOLUNTEER_NAME = configuration[
    "similarity_level_to_warn_when_comparing_volunteer_names_on_event_import"
]
SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_VOLUNTEER_NAME = configuration[
    "similarity_level_to_match_a_very_similar_volunteer_name_on_event_import"
]


MIN_CADET_AGE = configuration["minimum_cadet_age"]
MAX_CADET_AGE = configuration["maximium_cadet_age"]

## WA
## Status of payment_status, used to determine cadet status
WA_ACTIVE_AND_PAID_STATUS = configuration[
    "wild_apricot_payment_fields_which_are_active_and_paid_status"
]
WA_PARTIAL_PAID_STATUS = configuration[
    "wild_apricot_payment_fields_which_are_part_paid_status"
]
WA_UNPAID_STATUS = configuration["wild_apricot_payment_fields_which_are_unpaid_status"]
WA_CANCELLED_STATUS = configuration[
    "wild_apricot_payment_fields_which_are_cancelled_status"
]
WILD_APRICOT_EVENT_ID = configuration["wild_apricot_event_id"]
ALLOWED_UPLOAD_FILE_TYPES = configuration["allowed_upload_file_types"]
#

## Page sizes
MAX_FILE_SIZE = configuration["max_file_size"]
UPLOAD_EXTENSIONS = configuration["upload_extensions"]

MINIMUM_COLOUR_GROUPS_TO_DISTRIBUTE = configuration["min_colour_groups_to_distribute"]

## if following in volunteer status field can't volunteer
UNABLE_TO_VOLUNTEER_KEYWORD_LIST = configuration[
    "if_volunteer_unable_to_volunteer_contains"
]
MIN_AGE_WHEN_CADET_CAN_BE_AT_EVENT_WITHOUT_PARENT = configuration[
    "minimum_age_when_cadet_can_be_at_event_without_parent"
]
CADET_COMMITTEE_SHIRT_COLOUR = configuration["cadet_committee_shirt_colour"]

SUPPORT_EMAIL = configuration["support_email"]

WA_FIELD_LIST_FILE = configuration["WA_field_list_file"]

IMPORT_SKILLS_CONFIG = from_skills_dict_in_import_config_to_import_config(
    configuration["import_skills_csv"]
)

local_timezone = pytz.timezone(configuration["pytz_timezone"])
