### FOLLOWING IS THE MASTER LIST OF FIELD MAPPINGS

CADET_FIRST_NAME = "cadet_first_name"
CADET_SURNAME = "cadet_second_name"
CADET_DATE_OF_BIRTH = "cadet_date_of_birth"
PAYMENT_STATUS = "registration_payment_status"
REGISTRATION_DATE = "registration_date"
WEEKEND_DAYS_ATTENDING_INPUT = "weekend_days_attending_input"
ALL_DAYS_ATTENDING_INPUT = "all_days_attending_input"

VOLUNTEER_STATUS = "volunteer_status"

VOLUNTEER1_AVAILABILITY = "volunteer1_availability_all_days"
VOLUNTEER1_WEEKEND_AVAILABILITY = "volunteer1_weekend_availability"
VOLUNTEER1_NAME = "volunteer1_name"
VOLUNTEER1_DUTIES = "volunteer1_duties"
VOLUNTEER1_SAME_OR_VARIED = "volunteer1_same_or_varied"
VOLUNTEER1_FOOD_PREFERENCE = "volunteer1_food_preference"

VOLUNTEER2_AVAILABILITY = "volunteer2_availability_all_days"
VOLUNTEER2_WEEKEND_AVAILABILITY = "volunteer2_weekend_availability"
VOLUNTEER2_NAME = "volunteer2_name"
VOLUNTEER2_DUTIES = "volunteer2_duties"
VOLUNTEER2_SAME_OR_VARIED = "volunteer2_same_or_varied"
VOLUNTEER2_FOOD_PREFERENCE = "volunteer2_food_preference"

ALL_FIELDS_EXPECTED_IN_WA_FILE = [
    CADET_FIRST_NAME,
CADET_SURNAME,
CADET_DATE_OF_BIRTH,
PAYMENT_STATUS,
REGISTRATION_DATE,
WEEKEND_DAYS_ATTENDING_INPUT,
ALL_DAYS_ATTENDING_INPUT,

VOLUNTEER_STATUS,

VOLUNTEER1_AVAILABILITY,
VOLUNTEER1_WEEKEND_AVAILABILITY,
VOLUNTEER1_NAME,
VOLUNTEER1_DUTIES,
VOLUNTEER1_SAME_OR_VARIED,
VOLUNTEER1_FOOD_PREFERENCE,

VOLUNTEER2_AVAILABILITY,
VOLUNTEER2_WEEKEND_AVAILABILITY,
VOLUNTEER2_NAME,
VOLUNTEER2_DUTIES,
VOLUNTEER2_SAME_OR_VARIED,
VOLUNTEER2_FOOD_PREFERENCE
]

## following are derived fields, not found in WA data
CADET_NAME = "Cadet"
GROUP_STR_NAME = "group"
ID_NAME = "cadet_id"
DAYS_ATTENDING = "days_attending"
CADET_ID = "cadet_id"

### THIS MUST BE ACCURATE OR FILE IN/OUT WILL FAIL
FIELDS_WITH_DATES = [CADET_DATE_OF_BIRTH]
FIELDS_WITH_DATETIMES = [REGISTRATION_DATE]
FIELDS_WITH_INTEGERS = []
FIELDS_AS_STR = [CADET_ID]

SPECIAL_FIELDS = [PAYMENT_STATUS]

## Rule of thumb is we do all editing in skipperman, not WA
## The only things that will change WA are those relating to payment, eg cancellation, change in numbers etc
## payment status will also change, but this is flagged seperately
FIELDS_TO_FLAG_WHEN_COMPARING_WA_DIFF = [WEEKEND_DAYS_ATTENDING_INPUT]
