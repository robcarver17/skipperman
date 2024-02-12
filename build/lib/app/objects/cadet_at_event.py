from enum import Enum

from app.data_access.configuration.configuration import ACTIVE_STATUS, CANCELLED_STATUS
from app.objects.constants import missing_data
from app.objects.day_selectors import DaySelector, weekend_day_selector_from_text, any_day_selector_from_short_form_text
from app.objects.events import Event
from app.objects.field_list import WEEKEND_DAYS_ATTENDING_INPUT, ALL_DAYS_ATTENDING_INPUT, PAYMENT_STATUS
from app.objects.mapped_wa_event_deltas import RowInMappedWAEventDeltaRow

RowStatus = Enum("RowStatus", ["Cancelled", "Active", "Deleted"])
cancelled_status = RowStatus.Cancelled
active_status = RowStatus.Active
deleted_status = RowStatus.Deleted
all_possible_status = [cancelled_status, active_status, deleted_status]


def get_attendance_selection_from_event_row(
        row: RowInMappedWAEventDeltaRow, event: Event) -> DaySelector:

    row_as_dict = row.data_in_row.as_dict()

    if WEEKEND_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return weekend_day_selector_from_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    elif ALL_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return any_day_selector_from_short_form_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    return event.day_selector_with_covered_days()


def get_status_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEventDeltaRow,
) -> RowStatus:
    status_str = get_status_str_from_row_of_mapped_wa_event_data(
        row_of_mapped_wa_event_data
    )
    if status_str in ACTIVE_STATUS:
        return active_status

    if status_str in CANCELLED_STATUS:
        return cancelled_status

    raise Exception(
        "WA has used a status of %s in the mapped field %s, not recognised, update configuration.py"
        % (status_str, PAYMENT_STATUS)
    )


def get_status_str_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEventDeltaRow,
) -> str:
    status_field = row_of_mapped_wa_event_data.get_data_attribute_or_missing_data(
        PAYMENT_STATUS
    )
    if status_field is missing_data:
        raise Exception(
            "Can't get status of entry because field %s is missing from mapping; check your field mapping"
            % PAYMENT_STATUS
        )

    return status_field
