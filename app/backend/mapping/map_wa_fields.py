from datetime import datetime

import pandas as pd

from app.data_access.configuration.configuration import (
    WA_ACTIVE_AND_PAID_STATUS,
    WA_CANCELLED_STATUS,
    WA_PARTIAL_PAID_STATUS,
    WA_UNPAID_STATUS,
)
from app.data_access.configuration.field_list import (
    REGISTERED_BY_FIRST_NAME,
    REGISTERED_BY_LAST_NAME,
    REGISTRATION_DATE,
    PAYMENT_STATUS,
)
from app.data_access.configuration.field_list_groups import MINIMUM_REQUIRED_FOR_REGISTRATION
from app.data_access.store.object_store import ObjectStore

from app.backend.mapping.list_of_field_mappings import get_field_mapping_for_event
from app.objects.events import Event
from app.objects.exceptions import missing_data
from app.objects.registration_status import (
    RegistrationStatus,
    POSSIBLE_STATUS_NAMES,
    active_paid_status,
    cancelled_status,
    empty_status,
    active_part_paid_status,
    active_unpaid_status,
)
from app.objects.utils import transform_datetime_into_str
from app.objects.wa_field_mapping import ListOfWAFieldMappings
from app.objects.registration_data import (
    RegistrationDataForEvent,
    RowInRegistrationData,
)
from app.backend.file_handling import load_spreadsheet_file_and_clear_nans


def map_wa_fields_in_df_for_event_and_add_special_fields(
    object_store: ObjectStore, event: Event, filename: str
) -> RegistrationDataForEvent:
    mapped_wa_event_data = map_wa_fields_in_df_for_event(
        object_store=object_store, event=event, filename=filename
    )
    mapped_wa_event_data_with_row_status = (
        create_row_status_from_wa_fields_in_event_data(mapped_wa_event_data)
    )
    mapped_wa_event_data_with_row_status_and_id = (
        add_row_id_from_wa_fields_in_event_data(mapped_wa_event_data_with_row_status)
    )

    return mapped_wa_event_data_with_row_status_and_id


def map_wa_fields_in_df_for_event(
    object_store: ObjectStore, event: Event, filename: str
) -> RegistrationDataForEvent:
    wa_as_df = load_spreadsheet_file_and_clear_nans(filename)
    # Set up WA event mapping fields
    wa_field_mapping = get_field_mapping_for_event(
        event=event, object_store=object_store
    )

    # Do the field mapping
    # need to think about what happens if a field is missing
    mapped_wa_event_data = map_wa_fields_in_df(
        wa_as_df=wa_as_df,
        wa_field_mapping=wa_field_mapping,
    )

    return mapped_wa_event_data


def map_wa_fields_in_df(
    wa_as_df: pd.DataFrame,
    wa_field_mapping: ListOfWAFieldMappings,
) -> RegistrationDataForEvent:
    fields_in_wa_file = list(wa_as_df.columns)
    matching_wa_fields = wa_field_mapping.matching_wa_fields(fields_in_wa_file)
    dict_of_mapped_data = {}
    for wa_fieldname in matching_wa_fields:
        my_fieldname = wa_field_mapping.skipperman_field_given_wa_field(wa_fieldname)
        dict_of_mapped_data[my_fieldname] = wa_as_df[wa_fieldname]

    mapped_wa_event_data = RegistrationDataForEvent.from_dict(dict_of_mapped_data)

    return mapped_wa_event_data


def create_row_status_from_wa_fields_in_event_data(
    mapped_wa_event_data: RegistrationDataForEvent,
) -> RegistrationDataForEvent:
    for row_of_mapped_wa_event_data in mapped_wa_event_data:
        add_status_to_row_of_mapped_wa_event_data(row_of_mapped_wa_event_data)

    return mapped_wa_event_data


def add_status_to_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInRegistrationData,
):
    status = get_status_from_row_of_mapped_wa_event_data(row_of_mapped_wa_event_data)
    row_of_mapped_wa_event_data.registration_status = status


def get_status_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInRegistrationData,
) -> RegistrationStatus:
    status_str = get_status_str_from_row_of_mapped_wa_event_data(
        row_of_mapped_wa_event_data
    )
    if status_str in POSSIBLE_STATUS_NAMES:
        return RegistrationStatus(status_str)

    elif status_str in WA_ACTIVE_AND_PAID_STATUS:
        return active_paid_status

    elif status_str in WA_CANCELLED_STATUS:
        return cancelled_status

    elif status_str in WA_UNPAID_STATUS:
        return active_unpaid_status

    elif status_str in WA_PARTIAL_PAID_STATUS:
        return active_part_paid_status

    elif status_str == "":
        return empty_status
    else:
        raise Exception(
            "WA has used a status of %s in the mapped field %s, not recognised, update configuration.py"
            % (status_str, PAYMENT_STATUS)
        )


def get_status_str_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInRegistrationData,
) -> str:
    status_field = row_of_mapped_wa_event_data.get_item(PAYMENT_STATUS, missing_data)
    if status_field is missing_data:
        raise Exception(
            "Can't get status of entry because field %s is missing from WA mapping; check your field mapping"
            % PAYMENT_STATUS
        )

    return status_field


def add_row_id_from_wa_fields_in_event_data(
    registration_data: RegistrationDataForEvent,
) -> RegistrationDataForEvent:
    for row_in_registration_data in registration_data:
        add_unique_row_identified_to_row(row_in_registration_data)

    return registration_data

try:
    assert REGISTRATION_DATE in MINIMUM_REQUIRED_FOR_REGISTRATION
    assert REGISTERED_BY_FIRST_NAME in MINIMUM_REQUIRED_FOR_REGISTRATION
    assert REGISTERED_BY_LAST_NAME in MINIMUM_REQUIRED_FOR_REGISTRATION
except:
    raise Exception("Mismatch between unique row identifier and minimum required for registration")

def add_unique_row_identified_to_row(row_in_registration_data: RowInRegistrationData):
    row_id = unique_row_identifier(
        registration_date=row_in_registration_data[REGISTRATION_DATE],
        registered_by_first_name=row_in_registration_data[REGISTERED_BY_FIRST_NAME],
        registered_by_last_name=row_in_registration_data[REGISTERED_BY_LAST_NAME],
    )
    row_in_registration_data.row_id = row_id


def unique_row_identifier(
    registration_date: datetime.date,
    registered_by_last_name: str,
    registered_by_first_name: str,
) -> str:
    ## generate a unique hash from reg date, name, first name
    reg_datetime_as_str = transform_datetime_into_str(registration_date)
    row_id = "%s_%s_%s" % (
        reg_datetime_as_str,
        registered_by_last_name.lower().strip(),
        registered_by_first_name.lower().strip(),
    )

    return row_id
