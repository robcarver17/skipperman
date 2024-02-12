import datetime
import pandas as pd

# from app.logic import_wa edit_provided_cadet_details
from app.objects.cadets import Cadet
from app.objects.field_list import CADET_SURNAME, CADET_DATE_OF_BIRTH, CADET_FIRST_NAME
from app.objects.constants import NoMoreData

from app.backend.data.mapped_events import save_mapped_wa_event_delta_rows, load_existing_mapped_wa_event_with_ids, \
    save_mapped_wa_event_with_no_ids, load_mapped_wa_event
from app.objects.mapped_wa_event_deltas import (
    RowInMappedWAEventDeltaRow,
    RowInMappedWAEvent,
)
from app.objects.events import Event



def get_first_unmapped_row_for_event(event: Event):
    all_unmapped_rows = load_unmapped_rows_for_event(event)
    if len(all_unmapped_rows) == 0:
        raise NoMoreData()
    return all_unmapped_rows[0]


def load_unmapped_rows_for_event(event: Event):
    return load_mapped_wa_event(event)


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


def add_row_data_with_id_included_and_delete_from_unmapped_data(
    event: Event, new_row: RowInMappedWAEvent, cadet_id: str
):
    new_row_with_cadet_id = RowInMappedWAEventDeltaRow.from_row_without_id(
        cadet_id=cadet_id, data_in_row=new_row
    )
    existing_mapped_wa_event_with_ids = load_existing_mapped_wa_event_with_ids(
        event=event
    )

    existing_mapped_wa_event_with_ids.add_row(new_row_with_cadet_id)

    delete_first_unmapped_row_for_event(event)
    save_mapped_wa_event_delta_rows(
        mapped_wa_event_data_with_ids=existing_mapped_wa_event_with_ids, event=event
    )


def delete_first_unmapped_row_for_event(event: Event):
    all_unmapped_rows = load_unmapped_rows_for_event(event)
    if len(all_unmapped_rows) == 0:
        raise NoMoreData()
    all_unmapped_rows.pop(0)
    save_mapped_wa_event_with_no_ids(
        event=event, mapped_wa_event_data_with_no_ids=all_unmapped_rows
    )


