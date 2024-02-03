import yaml
from app.data_access.file_access import get_relative_pathname_from_list


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
UPLOADS = configuration["uploads"]
STAGING = configuration["staging"]
REPORTING_SUBDIRECTORY = configuration["reporting_subdirectory"]


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
ACTIVE_STATUS = configuration["wild_apricot_payment_fields_which_are_active_status"]
CANCELLED_STATUS = configuration[
    "wild_apricot_payment_fields_which_are_cancelled_status"
]
WILD_APRICOT_EVENT_ID = configuration["wild_apricot_event_id"]
WILD_APRICOT_FILE_TYPES = configuration["wild_apricot_file_types"]
#
# File handling
MAX_FILE_SIZE = configuration["max_file_size"]
UPLOAD_EXTENSIONS = configuration["upload_extensions"]
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
VOLUNTEER_LOCATIONS = configuration['volunteer_locations']
VOLUNTEER_ROLES = configuration['volunteer_roles']
VOLUNTEERS_REQUIRING_GROUP = configuration['volunteers_requiring_group']

LAKE = 'Lake'
RIVER = 'River'
OTHER = 'Other'

LAKE_VOLUNTEER_ROLES = VOLUNTEER_LOCATIONS[LAKE]
RIVER_VOLUNTEER_ROLES = VOLUNTEER_LOCATIONS[RIVER]

## Page sizes - not configured in yaml as won't need changing
A4_PAGESIZE = "A4"
A3_PAGESIZE = "A3"
ALL_PAGESIZE = [A3_PAGESIZE, A4_PAGESIZE]
DEFAULT_PAGESIZE = A4_PAGESIZE
ALL_FONTS = ["Courier", "Helvetica", "Arial", "Times"]
DEFAULT_FONT = "Arial"
UNIT_MM = "mm"
WIDTH = "width"
HEIGHT = "height"
PAGESIZE_MM = {
    A4_PAGESIZE: {WIDTH: 210, HEIGHT: 297},
    A3_PAGESIZE: {WIDTH: 297, HEIGHT: 420},
}
MM_PER_POINT_OF_FONT_SIZE = 0.353  ## DO NOT CHANGE THIS IS STANDARD
APPROX_WIDTH_TO_HEIGHT_RATIO = (
    0.6  ## DO NOT CHANGE: Exact value will depend on font used and letters
)
TITLE_MULTIPLIER = (
    2  ## how much bigger titles are than everything else, has to be integer
)
EDGE_MARGIN_MM = 10  ## change if you like but bear in mind printable area
COLUMN_GAP_MM = 10  ## change if you like but bear in mind readability / efficiency
LINE_GAP_AS_PERCENTAGE_OF_CHARACTER_HEIGHT = (
    0.2  ## change if you like but bear in mind readability / efficiency
)
MAX_FONT_SIZE = 18