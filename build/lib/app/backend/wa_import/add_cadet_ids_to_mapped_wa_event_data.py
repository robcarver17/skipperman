import datetime
import pandas as pd

from app.objects.cadets import Cadet
from app.data_access.configuration.field_list import CADET_SURNAME, CADET_DATE_OF_BIRTH, CADET_FIRST_NAME

from app.backend.data.cadets_at_event import load_identified_cadets_at_event, save_identified_cadets_at_event

from app.objects.events import Event
from app.objects.mapped_wa_event import RowInMappedWAEvent


def get_cadet_data_from_row_of_mapped_data_no_checks(
    row_of_mapped_data: RowInMappedWAEvent,
) -> Cadet:
    first_name = row_of_mapped_data[CADET_FIRST_NAME]
    second_name = row_of_mapped_data[CADET_SURNAME]
    dob = row_of_mapped_data[CADET_DATE_OF_BIRTH]
    dob_as_date = _translate_df_timestamp_to_datetime(dob)

    return Cadet(
        first_name=first_name.strip(),
        surname=second_name.strip(),
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
    event: Event, row_id: str, cadet_id: str
):

    list_of_cadets_at_event = load_identified_cadets_at_event(event)
    list_of_cadets_at_event.add(row_id=row_id, cadet_id=cadet_id)
    save_identified_cadets_at_event(list_of_cadets_at_event=list_of_cadets_at_event, event=event)

