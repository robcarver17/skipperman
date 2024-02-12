from dataclasses import dataclass

from enum import Enum

from app.data_access.configuration.configuration import ACTIVE_STATUS, CANCELLED_STATUS
from app.objects.constants import missing_data
from app.objects.day_selectors import DaySelector, weekend_day_selector_from_text, \
    any_day_selector_from_short_form_text, day_selector_stored_format_from_text, day_selector_to_text_in_stored_format
from app.objects.events import Event
from app.objects.field_list import WEEKEND_DAYS_ATTENDING_INPUT, ALL_DAYS_ATTENDING_INPUT, PAYMENT_STATUS
from app.objects.mapped_wa_event import RowInMappedWAEvent
from app.objects.generic import GenericSkipperManObject, GenericListOfObjects
from app.objects.utils import clean_up_dict_with_nans

RowStatus = Enum("RowStatus", ["Cancelled", "Active", "Deleted"])
cancelled_status = RowStatus.Cancelled
active_status = RowStatus.Active
deleted_status = RowStatus.Deleted
all_possible_status = [cancelled_status, active_status, deleted_status]

class IdentifiedCadetAtEvent(GenericSkipperManObject):
    row_id: str
    cadet_id: str

class ListOfIdentifiedCadetsAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return IdentifiedCadetAtEvent

    def list_of_row_ids(self):
        return [item.row_id for item in self]

## following must match attributes
STATUS_KEY = "status"
AVAILABILITY = "availability"
CADET_ID = "cadet_id"
ROW_ID = "row_id"

@dataclass
class CadetAtEvent(GenericSkipperManObject):
    cadet_id: str
    availability: DaySelector
    status: RowStatus

    @classmethod
    def from_dict(cls, dict_with_str):
        dict_with_str = clean_up_dict_with_nans(dict_with_str)
        availability_as_str = dict_with_str.pop(AVAILABILITY)
        if type(availability_as_str) is not str:
            availability_as_str = "" ## corner case

        availability = day_selector_stored_format_from_text(availability_as_str)
        row_status_as_str = dict_with_str[STATUS_KEY]

        return cls(
            cadet_id=dict_with_str[CADET_ID],
            availability=availability,
            status=RowStatus[row_status_as_str]
        )


    def as_str_dict(self) -> dict:
        as_dict = self.as_dict()
        as_dict[STATUS_KEY] = self.status.name
        as_dict[AVAILABILITY] = day_selector_to_text_in_stored_format(self.availability)

        return as_dict



class ListOfCadetsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetAtEvent


def get_attendance_selection_from_event_row(
        row: RowInMappedWAEvent, event: Event) -> DaySelector:

    row_as_dict = row.as_dict()

    if WEEKEND_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return weekend_day_selector_from_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    elif ALL_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return any_day_selector_from_short_form_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    return event.day_selector_with_covered_days()


def get_status_from_row_of_mapped_wa_event_data(
    row_of_mapped_wa_event_data: RowInMappedWAEvent,
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
    row_of_mapped_wa_event_data: RowInMappedWAEvent,
) -> str:
    status_field = row_of_mapped_wa_event_data.get_item(
        PAYMENT_STATUS, missing_data
    )
    if status_field is missing_data:
        raise Exception(
            "Can't get status of entry because field %s is missing from mapping; check your field mapping"
            % PAYMENT_STATUS
        )

    return status_field
