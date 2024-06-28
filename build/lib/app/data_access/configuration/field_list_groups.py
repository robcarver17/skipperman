import pandas as pd

## Editable/non editable in registration data page


from app.data_access.configuration.field_list import *

## Required to get this to work
from app.data_access.configuration import field_list
from app.data_access.configuration.field_list import (
    VOLUNTEER1_NAME,
    VOLUNTEER1_DUTIES,
    VOLUNTEER1_SAME_OR_VARIED,
    VOLUNTEER1_FOOD_PREFERENCE,
    VOLUNTEER2_AVAILABILITY,
    VOLUNTEER2_WEEKEND_AVAILABILITY,
    VOLUNTEER2_NAME,
    VOLUNTEER2_DUTIES,
    VOLUNTEER2_SAME_OR_VARIED,
    VOLUNTEER2_FOOD_PREFERENCE,
    REGISTRATION_TOTAL_FEE,
    REGISTRATION_INTERNAL_NOTES,
    CADET_FOOD_PREFERENCE,
)

all_fields = dir(field_list)
ALL_FIELDS_EXPECTED_IN_WA_FILE_MAPPING = [
    eval(field) for field in all_fields if not field[0] == "_"
]

ALL_FIELDS_AS_PD_SERIES = pd.Series(ALL_FIELDS_EXPECTED_IN_WA_FILE_MAPPING)

FIELDS_WITH_DATES = [CADET_DATE_OF_BIRTH]
FIELDS_WITH_DATETIMES = [REGISTRATION_DATE]
FIELDS_WITH_INTEGERS = []
FIELDS_AS_STR = [
    RESPONSIBLE_ADULT_NUMBER
]  ## Only fields where resolving as natural field would cause problems eg phone numbers

## VIEW ONLY
## Rule of thumb is we do all editing in skipperman, not WA
## don't include everything just what is required for information purposes

FIELDS_VIEW_ONLY_IN_EDIT_VIEW = [
    ANY_OTHER_INFORMATION,
    CADET_FOOD_PREFERENCE,
    REGISTRATION_DATE,
    PAYMENT_STATUS,
    REGISTRATION_TOTAL_FEE,
    REGISTERED_BY_FIRST_NAME,
    REGISTERED_BY_LAST_NAME,
    REGISTERED_EMAIL,
    REGISTERED_PHONE,
    REGISTRATION_INTERNAL_NOTES,
]
FIELDS_TO_EDIT_IN_EDIT_VIEW = [  ## excludes status, days attending, food preference since these are added afterwards
    RESPONSIBLE_ADULT_NAME,
    RESPONSIBLE_ADULT_NUMBER,
]
NAME_KEY_IN_VOLUNTEER_FIELDS_DICT = "VOLUNTEER_NAME"
AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT = "AVAILABILITY"
WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT = "WEEKEND_AVAILABILITY"
DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT = "DUTIES"
SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT = "SAME_OR_VARIED"
FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT = "FOOD_PREFERENCE"
LIST_OF_VOLUNTEER_FIELDS = [
    {
        ## First volunteer
        AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER1_AVAILABILITY,
        WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER1_WEEKEND_AVAILABILITY,
        NAME_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER1_NAME,
        DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER1_DUTIES,
        SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER1_SAME_OR_VARIED,
        FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER1_FOOD_PREFERENCE,
    },
    {
        ## Second volunteer
        AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER2_AVAILABILITY,
        WEEKEND_AVAILABILITY_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER2_WEEKEND_AVAILABILITY,
        NAME_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER2_NAME,
        DUTIES_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER2_DUTIES,
        SAME_OR_VARIED_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER2_SAME_OR_VARIED,
        FOOD_PREFERENCE_KEY_IN_VOLUNTEER_FIELDS_DICT: VOLUNTEER2_FOOD_PREFERENCE,
    },
]

### CADET ALLOCATION
GROUP_ALLOCATION_FIELDS = [
    CADET_BOAT_OWNERSHIP_STATUS,
    DESIRED_BOAT,
    CADET_WANTS_MG,
    CADET_GROUP_PREFERENCE,
    CADET_HIGHEST_QUALIFICATION,
    CADET_PREVIOUS_EXPERIENCE,
    CADET_BOAT_CLASS,
    CADET_BOAT_SAIL_NUMBER,
    CADET_DOUBLE_HANDED_PARTNER,
    ANY_OTHER_INFORMATION,
]

GROUP_ALLOCATION_FIELDS_HIDE = [CADET_BOAT_SAIL_NUMBER]  ## as also an entry item
GROUP_ALLOCATION_FIELDS_TO_IGNORE_WHEN_RACING_ONLY = [
    DESIRED_BOAT,
    CADET_WANTS_MG,
    CADET_GROUP_PREFERENCE,
    CADET_HIGHEST_QUALIFICATION,
    CADET_PREVIOUS_EXPERIENCE,
]
