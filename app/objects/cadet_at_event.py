from dataclasses import dataclass
from typing import List

from app.objects.constants import missing_data
from app.objects.day_selectors import DaySelector, day_selector_stored_format_from_text, \
    day_selector_to_text_in_stored_format, weekend_day_selector_from_text, any_day_selector_from_short_form_text, Day
from app.objects.events import Event
from app.data_access.configuration.field_list import WEEKEND_DAYS_ATTENDING_INPUT, ALL_DAYS_ATTENDING_INPUT, \
    CADET_HEALTH, RESPONSIBLE_ADULT_NUMBER, RESPONSIBLE_ADULT_NAME
from app.objects.generic import GenericSkipperManObjectWithIds, GenericListOfObjectsWithIds, GenericListOfObjects, \
    GenericSkipperManObject, transform_string_into_class_instance, transform_class_instance_into_string

from app.objects.utils import clean_up_dict_with_nans
from app.objects.mapped_wa_event import RowInMappedWAEvent, RegistrationStatus, deleted_status

SKIP_TEST_CADET_ID = str(-9999)

@dataclass
class IdentifiedCadetAtEvent(GenericSkipperManObject):
    row_id: str
    cadet_id: str

    @property
    def is_test_cadet(self):
        return self.cadet_id==SKIP_TEST_CADET_ID

    @classmethod
    def test_cadet(cls, row_id: str):
        return cls(cadet_id=SKIP_TEST_CADET_ID, row_id=row_id)

class ListOfIdentifiedCadetsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return IdentifiedCadetAtEvent

    def __add__(self, other: IdentifiedCadetAtEvent):
        self.add(row_id=other.row_id, cadet_id=other.cadet_id)

    def is_cadet_with_id_in_identified_list(self, cadet_id) -> bool:
        list_of_row_ids = self.list_of_unique_row_id_given_cadet_id(cadet_id)
        missing = list_of_row_ids is missing_data
        return not missing

    def row_has_identified_cadet_including_test_cadets(self, row_id:str):
        return row_id in self.list_of_row_ids_including_test_cadets()

    def list_of_row_ids_including_test_cadets(self):
        return [item.row_id for item in self]

    def add(self, row_id: str, cadet_id: str):
        try:
            assert row_id not in self.list_of_row_ids_including_test_cadets()
        except:
            raise Exception("Row ID can't appear more than once")

        self.append(IdentifiedCadetAtEvent(row_id=row_id, cadet_id=cadet_id))

    def add_cadet_to_skip(self, row_id: str):
        try:
            assert row_id not in self.list_of_row_ids_including_test_cadets()
        except:
            raise Exception("Row ID can't appear more than once")

        self.append(IdentifiedCadetAtEvent.test_cadet(row_id=row_id))

    def cadet_id_given_row_id(self, row_id: str) -> str:
        matching = [item for item in self if item.row_id == row_id]
        if len(matching)==0:
            return missing_data
        elif len(matching)>1:
            raise Exception("Can't have same row_id more than once")

        matching_item = matching[0]
        cadet_id = str(matching_item.cadet_id)

        if cadet_id==SKIP_TEST_CADET_ID:
            return missing_data

        return cadet_id

    def list_of_unique_row_id_given_cadet_id(self, cadet_id: str) -> List[str]:
        matching = [item.row_id for item in self if item.cadet_id == cadet_id]
        if len(matching)==0:
            return missing_data
        elif len(matching)>1:
            raise Exception("Can't have same row_id more than once")

        return matching

    def list_of_row_ids_given_cadet_id_allowing_duplicates(self, cadet_id: str) -> List[str]:
        matching = [item.row_id for item in self if item.cadet_id == cadet_id]

        return matching


## following must match attributes
STATUS_KEY = "status"
AVAILABILITY = "availability"
CADET_ID = "cadet_id"
CHANGED = "changed"
NOTES = "notes"
HEALTH = "health"

@dataclass
class CadetAtEvent(GenericSkipperManObjectWithIds):
    cadet_id: str
    availability: DaySelector
    status: RegistrationStatus
    data_in_row: RowInMappedWAEvent
    notes: str = ''
    health: str = ''
    changed: bool  = False

    def clear_row_data(self):
        self.data_in_row.clear_values()

    def emergency_contact(self):
        contact = self.get_item_from_data(RESPONSIBLE_ADULT_NUMBER, '')
        contact_name = self.get_item_from_data(RESPONSIBLE_ADULT_NAME, '')

        return "%s (%s)" % (contact_name, str(contact))

    def get_item_from_data(self, key_name, default=''):
        return self.data_in_row.get_item(key_name, default=default)

    def is_active(self):
        return self.status.is_active

    @classmethod
    def from_dict(cls, dict_with_str):
        dict_with_str = clean_up_dict_with_nans(dict_with_str)
        availability_as_str = dict_with_str.pop(AVAILABILITY)
        if type(availability_as_str) is not str:
            availability_as_str = "" ## corner case
        availability = day_selector_stored_format_from_text(availability_as_str)

        status_as_str = dict_with_str.pop(STATUS_KEY)
        status =RegistrationStatus(status_as_str)

        cadet_id = str(dict_with_str.pop(CADET_ID))

        changed_str = dict_with_str.pop(CHANGED)
        changed = transform_string_into_class_instance(bool, changed_str)

        notes = dict_with_str.pop(NOTES, '')
        health = dict_with_str.pop(HEALTH, '')

        return cls(
            cadet_id=cadet_id,
            availability=availability,
            status=status,
            data_in_row=RowInMappedWAEvent.from_external_dict(dict_with_str),
            changed=changed,
            notes=notes,
            health=health
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



class ListOfCadetsAtEvent(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetAtEvent

    def active_and_available_on_day(self, day: Day):
        active = self.list_of_active_cadets_at_event()
        return active.subset_available_on_day(day)

    def subset_available_on_day(self, day: Day):
        return ListOfCadetsAtEvent([cadet_at_event for cadet_at_event in self if cadet_at_event.availability.available_on_day(day)])

    def list_of_active_cadet_ids(self):
        new_list = self.list_of_active_cadets_at_event()
        return new_list.list_of_cadet_ids()

    def list_of_active_cadets_at_event(self):
        new_list = [cadet_at_event for cadet_at_event in self if cadet_at_event.is_active()]
        return ListOfCadetsAtEvent(new_list)

    def mark_cadet_as_deleted(self, cadet_id: str):
        cadet_at_event = self.cadet_at_event_or_missing_data(cadet_id)
        if cadet_at_event is missing_data:
            raise Exception("Cadet not in event to mark as deleted")
        cadet_at_event.status = deleted_status
        cadet_at_event.changed = True

    def mark_cadet_as_unchanged(self, cadet_id: str):
        cadet_at_event = self.cadet_at_event_or_missing_data(cadet_id)
        if cadet_at_event is missing_data:
            raise Exception("Cadet not in event to mark as unchanged")
        cadet_at_event.changed = False

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

    def cadet_at_event(self, cadet_id) -> CadetAtEvent:
        idx = self.idx_of_items_with_cadet_id(cadet_id)
        return self[idx]

    def idx_of_items_with_cadet_id(self, cadet_id: str):
        list_of_cadet_ids= self.list_of_cadet_ids()
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

    def add(self, cadet_at_event: CadetAtEvent):
        if self.is_cadet_id_in_event(cadet_at_event.cadet_id):
            raise Exception("Cadet already exists!")
        self.append(cadet_at_event)

    def subset_given_cadet_ids(self, list_of_ids: List[str]):
        new_list = [self.cadet_at_event_or_missing_data(cadet_id) for cadet_id in list_of_ids if self.is_cadet_id_in_event(cadet_id)]
        return ListOfCadetsAtEvent(new_list)

    def replace_existing_cadet_at_event(self, new_cadet_at_event:CadetAtEvent):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(new_cadet_at_event.cadet_id)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % new_cadet_at_event.cadet_id)

        self[existing_cadet_idx] = new_cadet_at_event
        self.mark_cadet_as_changed(new_cadet_at_event.cadet_id)

    def update_status_of_existing_cadet_at_event(self, cadet_id:str, new_status: RegistrationStatus):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % cadet_id)
        existing_cadet_at_event = self[existing_cadet_idx]
        existing_cadet_at_event.status = new_status

        self[existing_cadet_idx] = existing_cadet_at_event
        self.mark_cadet_as_changed(cadet_id)

    def update_availability_of_existing_cadet_at_event(self, cadet_id:str, new_availabilty: DaySelector):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % cadet_id)
        existing_cadet_at_event = self[existing_cadet_idx]
        existing_cadet_at_event.availability = new_availabilty

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

    def clear_data_row_for_existing_cadet_at_event(self, cadet_id: str):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id)
        if existing_cadet_idx is missing_data:
            return
        existing_cadet_at_event = self[existing_cadet_idx]
        existing_cadet_at_event.clear_row_data()
        self[existing_cadet_idx] = existing_cadet_at_event

    def update_data_row_for_existing_cadet_at_event(self, cadet_id:str, new_data_in_row: RowInMappedWAEvent):
        ## DO NOT MARK AS CHANGED - ONLY APPLIES TO AVAILABLILITY AND STATUS FIELDS
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % cadet_id)
        existing_cadet_at_event = self[existing_cadet_idx]
        existing_cadet_at_event.data_in_row = new_data_in_row
        self[existing_cadet_idx] = existing_cadet_at_event


def get_cadet_at_event_from_row_in_mapped_event(
        row_in_mapped_wa_event: RowInMappedWAEvent,
        cadet_id: str,
        event: Event

) -> CadetAtEvent:

    status = row_in_mapped_wa_event.registration_status
    availability = get_attendance_selection_from_event_row(row_in_mapped_wa_event, event=event)
    health = get_health_from_event_row(row_in_mapped_wa_event)

    return CadetAtEvent(
        cadet_id=cadet_id,
        status=status,
        availability=availability,
        data_in_row=row_in_mapped_wa_event,
        changed=False,
        notes='',
        health=health
    )

def get_attendance_selection_from_event_row(
        row: RowInMappedWAEvent, event: Event) -> DaySelector:

    row_as_dict = row.as_dict()

    if WEEKEND_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return weekend_day_selector_from_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    elif ALL_DAYS_ATTENDING_INPUT in row_as_dict.keys():
        return any_day_selector_from_short_form_text(row_as_dict[WEEKEND_DAYS_ATTENDING_INPUT])

    return event.day_selector_with_covered_days()

def get_health_from_event_row(row: RowInMappedWAEvent):
    return row.get_item(CADET_HEALTH, '')