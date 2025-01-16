from dataclasses import dataclass
from typing import List

from app.objects.cadets import Cadet

from app.data_access.configuration.field_list import (
    WEEKEND_DAYS_ATTENDING_INPUT,
    ALL_DAYS_ATTENDING_INPUT,
    CADET_HEALTH,
)
from app.objects.exceptions import missing_data
from app.objects.day_selectors import (
    DaySelector,
    day_selector_stored_format_from_text,
    day_selector_to_text_in_stored_format,
    weekend_day_selector_from_text,
    create_day_selector_from_short_form_text,
)
from app.objects.events import Event
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)
from app.objects.generic_objects import (
    transform_class_instance_into_string,
    transform_string_into_class_instance,
    GenericSkipperManObjectWithIds,
)
from app.objects.registration_data import (
    RowInRegistrationData,
)
from app.objects.registration_status import RegistrationStatus, deleted_status
from app.objects.utils import clean_up_dict_with_nans

STATUS_KEY = "status"
AVAILABILITY = "availability"
CADET_ID = "cadet_id"
CHANGED = "changed"
NOTES = "notes"
HEALTH = "health"


@dataclass
class CadetWithIdAtEvent(GenericSkipperManObjectWithIds):
    cadet_id: str
    availability: DaySelector
    status: RegistrationStatus
    data_in_row: RowInRegistrationData
    notes: str = ""
    health: str = ""
    changed: bool = False

    def clear_row_data(self):
        self.data_in_row.clear_values()

    def is_active(self):
        return self.status.is_active

    @classmethod
    def from_dict_of_str(cls, dict_with_str):
        dict_with_str = clean_up_dict_with_nans(dict_with_str)
        availability_as_str = dict_with_str.pop(AVAILABILITY)
        if type(availability_as_str) is not str:
            availability_as_str = ""  ## corner case
        availability = day_selector_stored_format_from_text(availability_as_str)

        status_as_str = dict_with_str.pop(STATUS_KEY)
        status = RegistrationStatus(status_as_str)

        cadet_id = str(dict_with_str.pop(CADET_ID))

        changed_str = dict_with_str.pop(CHANGED)
        changed = transform_string_into_class_instance(bool, changed_str)

        notes = dict_with_str.pop(NOTES, "")
        health = dict_with_str.pop(HEALTH, "")

        return cls(
            cadet_id=cadet_id,
            availability=availability,
            status=status,
            data_in_row=RowInRegistrationData.from_external_dict(dict_with_str),
            changed=changed,
            notes=notes,
            health=health,
        )

    def as_str_dict(self) -> dict:
        as_dict = self.data_in_row.as_dict()
        status_as_str = self.status.name
        available_as_str = day_selector_to_text_in_stored_format(self.availability)
        notes = self.notes
        health = self.health

        as_dict[STATUS_KEY] = status_as_str
        as_dict[AVAILABILITY] = available_as_str
        as_dict[CADET_ID] = self.cadet_id
        as_dict[CHANGED] = transform_class_instance_into_string(self.changed)
        as_dict[NOTES] = notes
        as_dict[HEALTH] = health

        return as_dict


class ListOfCadetsWithIDAtEvent(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetWithIdAtEvent


    def mark_cadet_as_changed(self, cadet_id: str):
        cadet_at_event = self.cadet_at_event_or_missing_data(cadet_id)
        if cadet_at_event is missing_data:
            raise Exception("Cadet not in event to mark as deleted")
        cadet_at_event.changed = True

    def cadet_at_event_or_missing_data(self, cadet_id):
        if self.is_cadet_id_in_event(cadet_id):
            return self.cadet_at_event(cadet_id)
        else:
            return missing_data

    def cadet_at_event(self, cadet_id) -> CadetWithIdAtEvent:
        idx = self.idx_of_items_with_cadet_id(cadet_id)
        return self[idx]

    def idx_of_items_with_cadet_id(self, cadet_id: str):
        list_of_cadet_ids = self.list_of_cadet_ids()
        try:
            return list_of_cadet_ids.index(cadet_id)
        except ValueError:
            return missing_data

    def is_cadet_id_in_event(self, cadet_id: str):
        return cadet_id in self.list_of_cadet_ids()

    def list_of_ids(self) -> list:
        return self.list_of_cadet_ids()

    def list_of_cadet_ids(self) -> List[str]:
        return [str(item.cadet_id) for item in self]

    def add(self, cadet_at_event: CadetWithIdAtEvent):
        if self.is_cadet_id_in_event(cadet_at_event.cadet_id):
            raise Exception("Cadet already exists!")
        self.append(cadet_at_event)

    def replace_existing_cadet_at_event(self, new_cadet_at_event: CadetWithIdAtEvent):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(
            new_cadet_at_event.cadet_id
        )
        if existing_cadet_idx is missing_data:
            raise Exception(
                "Can't replace cadet id %s not in data" % new_cadet_at_event.cadet_id
            )

        self[existing_cadet_idx] = new_cadet_at_event
        self.mark_cadet_as_changed(new_cadet_at_event.cadet_id)

    def update_status_of_existing_cadet_at_event(
        self, cadet_id: str, new_status: RegistrationStatus
    ):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % cadet_id)
        existing_cadet_at_event = self[existing_cadet_idx]
        existing_cadet_at_event.status = new_status

        self[existing_cadet_idx] = existing_cadet_at_event
        self.mark_cadet_as_changed(cadet_id)


    def update_notes_for_existing_cadet_at_event(self, cadet_id: str, new_notes: str):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % cadet_id)
        existing_cadet_at_event = self[existing_cadet_idx]
        existing_cadet_at_event.notes = new_notes

        self[existing_cadet_idx] = existing_cadet_at_event
        self.mark_cadet_as_changed(cadet_id)

    def update_health_for_existing_cadet_at_event(self, cadet_id: str, new_health: str):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % cadet_id)
        existing_cadet_at_event = self[existing_cadet_idx]
        existing_cadet_at_event.health = new_health
        self[existing_cadet_idx] = existing_cadet_at_event
        self.mark_cadet_as_changed(cadet_id)

    def update_data_row_for_existing_cadet_at_event(
        self, cadet_id: str, new_data_in_row: RowInRegistrationData
    ):
        ## DO NOT MARK AS CHANGED - ONLY APPLIES TO AVAILABLILITY AND STATUS FIELDS
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % cadet_id)
        existing_cadet_at_event = self[existing_cadet_idx]
        existing_cadet_at_event.data_in_row = new_data_in_row
        self[existing_cadet_idx] = existing_cadet_at_event


def get_cadet_at_event_from_row_in_event_raw_registration_data(
    row_in_mapped_wa_event: RowInRegistrationData, cadet: Cadet, event: Event
) -> CadetWithIdAtEvent:
    status = row_in_mapped_wa_event.registration_status
    availability = get_attendance_selection_from_event_row(
        row_in_mapped_wa_event, event=event
    )
    health = get_health_from_event_row(row_in_mapped_wa_event)

    return CadetWithIdAtEvent(
        cadet_id=cadet.id,
        status=status,
        availability=availability,
        data_in_row=row_in_mapped_wa_event,
        changed=False,
        notes="",
        health=health,
    )


def get_attendance_selection_from_event_row(
    row: RowInRegistrationData, event: Event
) -> DaySelector:
    row_as_dict = row.as_dict()

    if WEEKEND_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return weekend_day_selector_from_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    elif ALL_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return create_day_selector_from_short_form_text(
            row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT]
        )

    return event.day_selector_for_days_in_event()


def get_health_from_event_row(row: RowInRegistrationData):
    return row.get_item(CADET_HEALTH, "")
