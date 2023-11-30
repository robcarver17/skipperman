### FOLLOWING IS THE MASTER LIST OF FIELD MAPPINGS

CADET_FIRST_NAME = "cadet_first_name"
CADET_SURNAME = "cadet_second_name"
CADET_DATE_OF_BIRTH = "cadet_date_of_birth"
PAYMENT_STATUS = "registration_payment_status"
REGISTRATION_DATE = "registration_date"
DAYS_ATTENDED = "days_attending"
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
FIELDS_TO_FLAG_WHEN_COMPARING_WA_DIFF = [
    DAYS_ATTENDED
]

## following are derived names, not found in WA data
CADET_NAME = "Cadet"
GROUP_STR_NAME = "group"
ID_NAME = "cadet_id"
