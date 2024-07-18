import datetime
import pandas as pd
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.cadets import Cadet, DEFAULT_DATE_OF_BIRTH
from app.data_access.configuration.field_list import (
    CADET_SURNAME,
    CADET_DATE_OF_BIRTH,
    CADET_FIRST_NAME,
)

from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData

from app.objects.events import Event
from app.objects.mapped_wa_event import RowInMappedWAEvent


def get_cadet_data_from_row_of_mapped_data_no_checks(
    row_of_mapped_data: RowInMappedWAEvent,
) -> Cadet:
    first_name = row_of_mapped_data.get(CADET_FIRST_NAME, "")
    second_name = row_of_mapped_data.get(CADET_SURNAME, "")
    dob = row_of_mapped_data.get(CADET_DATE_OF_BIRTH, None)
    if dob is None:
        dob_as_date = DEFAULT_DATE_OF_BIRTH
    else:
        dob_as_date = _translate_df_timestamp_to_datetime(dob)

    return Cadet.new(
        first_name=first_name,
        surname=second_name,
        date_of_birth=dob_as_date,
    )


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


def add_identified_cadet_and_row(
    interface: abstractInterface, event: Event, row_id: str, cadet_id: str
):
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    cadets_at_event_data.add_identified_cadet_id_and_row(
        event=event, row_id=row_id, cadet_id=cadet_id
    )


def mark_row_as_skip_cadet(interface: abstractInterface, event: Event, row_id: str):
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    cadets_at_event_data.mark_row_as_skip_cadet(event=event, row_id=row_id)


def is_row_in_event_already_identified_with_cadet(
    row: RowInMappedWAEvent, interface: abstractInterface, event: Event
) -> bool:
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    row_id_has_identified_cadet = (
        cadets_at_event_data.row_has_identified_cadet_including_test_cadets(
            row=row, event=event
        )
    )

    return row_id_has_identified_cadet
