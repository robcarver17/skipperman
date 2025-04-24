from app.data_access.configuration.field_list import (
    HELM_SURNAME,
    HELM_FIRST_NAME,
    CREW_SURNAME,
    CREW_FIRST_NAME,
    CADET_FIRST_NAME,
    CADET_SURNAME,
    CADET_DOUBLE_HANDED_PARTNER,
)

from app.objects.registration_data import (
    RegistrationDataForEvent,
    RowInRegistrationData,
)
from app.objects.utilities.utils import in_both_x_and_y


def convert_mapped_wa_event_potentially_with_joined_rows(
    mapped_wa_event: RegistrationDataForEvent,
) -> RegistrationDataForEvent:
    for row in mapped_wa_event:
        if does_row_contain_helm_and_crew(row):
            modify_row(row)
        else:
            continue

    return mapped_wa_event


def does_row_contain_helm_and_crew(row: RowInRegistrationData) -> bool:
    fields = list(row.keys())
    return (
        len(
            in_both_x_and_y(
                fields, [HELM_SURNAME, HELM_FIRST_NAME, CREW_SURNAME, CREW_FIRST_NAME]
            )
        )
        > 0
    )


def modify_row(row: RowInRegistrationData):
    helm_first_name = row.pop(HELM_FIRST_NAME)
    helm_surname = row.pop(HELM_SURNAME)

    crew_first_name = row.pop(CREW_FIRST_NAME)
    crew_surname = row.pop(CREW_SURNAME)

    crew_name = "%s %s" % (crew_first_name, crew_surname)

    ## no date of births, they will be blank

    row[CADET_FIRST_NAME] = helm_first_name
    row[CADET_SURNAME] = helm_surname
    row[CADET_DOUBLE_HANDED_PARTNER] = crew_name
