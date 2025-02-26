import datetime
from typing import List

import pandas as pd

from app.objects.exceptions import arg_not_passed
from app.objects.membership_status import none_member, user_unconfirmed_member

from app.data_access.configuration.field_list import (
    CADET_FIRST_NAME,
    CADET_SURNAME,
    CADET_DATE_OF_BIRTH,
)
from app.objects.cadets import Cadet, DEFAULT_DATE_OF_BIRTH

from app.objects.registration_data import (
    RegistrationDataForEvent,
    RowInRegistrationData,
)

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.data_access.store.object_definitions import (
    object_definition_for_mapped_registration_data,
)


def get_cadet_data_from_row_of_registration_data_no_checks(
    row_of_mapped_data: RowInRegistrationData,
) -> Cadet:
    print(row_of_mapped_data)
    first_name = row_of_mapped_data.get(CADET_FIRST_NAME, "")
    second_name = row_of_mapped_data.get(CADET_SURNAME, "")
    dob = row_of_mapped_data.get(CADET_DATE_OF_BIRTH, None)
    if dob is None:
        dob_as_date = DEFAULT_DATE_OF_BIRTH
    else:
        dob_as_date = _translate_df_timestamp_to_datetime(dob)

    cadet = Cadet.new(
        first_name=first_name,
        surname=second_name,
        date_of_birth=dob_as_date,
        membership_status=user_unconfirmed_member,
    )


    return cadet


def _translate_df_timestamp_to_datetime(df_timestamp) -> datetime.date:
    if type(df_timestamp) is datetime.date:
        return df_timestamp

    if type(df_timestamp) is pd._libs.tslibs.timestamps.Timestamp:
        return df_timestamp.date()

    if type(df_timestamp) is str:
        return datetime.datetime.strptime(df_timestamp, "")

    raise Exception(
        "Can't handle timestamp %s with type %s"
        % (str(df_timestamp), str(type(df_timestamp)))
    )


def get_row_in_raw_registration_data_given_id(
    object_store: ObjectStore, event: Event, row_id: str, default = arg_not_passed
) -> RowInRegistrationData:
    registration_data = get_raw_mapped_registration_data(
        object_store=object_store, event=event
    )

    return registration_data.get_row_with_rowid(row_id=row_id, default=default)


def get_list_of_row_ids_in_raw_registration_data_for_event(
    object_store: ObjectStore, event: Event
) -> List[str]:
    registration_data = get_raw_mapped_registration_data(
        object_store=object_store, event=event
    )
    return registration_data.list_of_row_ids()


def does_event_have_imported_registration_data(
    object_store: ObjectStore, event: Event
) -> bool:
    reg_data = get_raw_mapped_registration_data(object_store=object_store, event=event)
    return len(reg_data) > 0


def get_raw_mapped_registration_data(
    object_store: ObjectStore, event: Event
) -> RegistrationDataForEvent:
    return object_store.get(
        object_definition=object_definition_for_mapped_registration_data,
        event_id=event.id,
    )


def update_raw_mapped_registration_data(
    object_store: ObjectStore, event: Event, registration_data: RegistrationDataForEvent
):
    object_store.update(
        object_definition=object_definition_for_mapped_registration_data,
        event_id=event.id,
        new_object=registration_data,
    )
