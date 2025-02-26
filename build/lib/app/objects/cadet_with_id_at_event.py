from dataclasses import dataclass
from typing import List, Union

from app.objects.cadets import Cadet

from app.data_access.configuration.field_list import (
    WEEKEND_DAYS_ATTENDING_INPUT,
    ALL_DAYS_ATTENDING_INPUT,
    CADET_HEALTH,
)
from app.objects.exceptions import missing_data, arg_not_passed
from app.objects.day_selectors import (
    DaySelector,
    day_selector_stored_format_from_text,
    day_selector_to_text_in_stored_format,
     create_day_selector_from_short_form_text_with_passed_days,
)
from app.objects.events import Event
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds, get_unique_object_with_attr_in_list, get_idx_of_unique_object_with_attr_in_list,
)
from app.objects.generic_objects import (
    transform_class_instance_into_string,
    transform_string_into_class_instance,
    GenericSkipperManObjectWithIds,
)
from app.objects.registration_data import (
    RowInRegistrationData,
)
from app.objects.registration_status import RegistrationStatus
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
    changed: bool = False ## no longer used but kept for data compatibility

    def clear_private_data(self):
        self.clear_row_data()
        self.notes = ""
        self.health = ""

    def clear_row_data(self):
        self.data_in_row.clear_values()

    @classmethod
    def from_dict_of_str(cls, dict_with_str):
        dict_with_str = clean_up_dict_with_nans(dict_with_str)
        availability_as_str = dict_with_str.pop(AVAILABILITY, '')
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
            data_in_row=RowInRegistrationData.from_dict_of_str(dict_with_str),
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

    def clear_private_data(self):
        for cadet_with_id_at_event in self:
            cadet_with_id_at_event.clear_private_data()


    def cadet_with_id_and_data_at_event(self, cadet_id: str, default = arg_not_passed) -> CadetWithIdAtEvent:
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='cadet_id',
            attr_value=cadet_id,
            default=default
        )

    def add(self, cadet_at_event: CadetWithIdAtEvent):
        if self.is_cadet_id_in_event(cadet_at_event.cadet_id):
            raise Exception("Cadet already exists!")
        self.append(cadet_at_event)

    def replace_existing_cadet_at_event(self, new_cadet_at_event: CadetWithIdAtEvent):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(
            new_cadet_at_event.cadet_id, default=missing_data
        )
        if existing_cadet_idx is missing_data:
            raise Exception(
                "Can't replace cadet id %s not in data" % new_cadet_at_event.cadet_id
            )

        self[existing_cadet_idx] = new_cadet_at_event

    def update_status_of_existing_cadet_at_event(
        self, cadet_id: str, new_status: RegistrationStatus
    ):
        self._update_item_for_existing_cadet_at_event(
            cadet_id=cadet_id,
            new_item=new_status,
            attribute='status'
        )

    def update_notes_for_existing_cadet_at_event(self, cadet_id: str, new_notes: str):
        self._update_item_for_existing_cadet_at_event(
            cadet_id=cadet_id,
            new_item=new_notes,
            attribute='notes'
        )

    def update_health_for_existing_cadet_at_event(self, cadet_id: str, new_health: str):

        self._update_item_for_existing_cadet_at_event(
            cadet_id=cadet_id,
            new_item=new_health,
            attribute='health'
        )



    def update_data_row_for_existing_cadet_at_event(
        self, cadet_id: str, new_data_in_row: RowInRegistrationData
    ):
        self._update_item_for_existing_cadet_at_event(
            cadet_id=cadet_id,
            new_item=new_data_in_row,
            attribute='data_in_row'
        )


    def _update_item_for_existing_cadet_at_event(
        self, cadet_id: str, attribute: str, new_item: Union[RowInRegistrationData, str, RegistrationStatus]
    ):
        existing_cadet_idx = self.idx_of_items_with_cadet_id(cadet_id, default=missing_data)
        if existing_cadet_idx is missing_data:
            raise Exception("Can't replace cadet id %s not in data" % cadet_id)
        existing_cadet_at_event = self[existing_cadet_idx]
        setattr(existing_cadet_at_event, attribute, new_item)
        self[existing_cadet_idx] = existing_cadet_at_event

    def idx_of_items_with_cadet_id(self, cadet_id: str, default = arg_not_passed):
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='cadet_id',
            attr_value=cadet_id,
            default=default

        )


    def is_cadet_id_in_event(self, cadet_id: str):
        return cadet_id in self.list_of_cadet_ids()


    def list_of_cadet_ids(self) -> List[str]:
        return [str(item.cadet_id) for item in self]


def get_cadet_at_event_from_row_in_event_raw_registration_data(
    row_in_registration_data: RowInRegistrationData, cadet: Cadet, event: Event
) -> CadetWithIdAtEvent:
    status = row_in_registration_data.registration_status
    availability = get_sailor_attendance_selection_from_event_row(
        row_in_registration_data, event=event
    )
    health = get_health_from_event_row(row_in_registration_data)

    return CadetWithIdAtEvent(
        cadet_id=cadet.id,
        status=status,
        availability=availability,
        data_in_row=row_in_registration_data,
        changed=False,
        notes="",
        health=health,
    )


def get_sailor_attendance_selection_from_event_row(
    row: RowInRegistrationData, event: Event
) -> DaySelector:
    row_as_dict = row.as_dict()
    days_in_event = event.days_in_event()

    weekend_selection = row_as_dict.get(WEEKEND_DAYS_ATTENDING_INPUT, '')
    day_selection = row_as_dict.get(ALL_DAYS_ATTENDING_INPUT, '')

    if len(weekend_selection)>0:
        print("From selection %s" % weekend_selection)
        return create_day_selector_from_short_form_text_with_passed_days(
            weekend_selection, days_in_event=days_in_event
        )
    elif len(day_selection)>0:
        print("From selection %s" % day_selection)
        return create_day_selector_from_short_form_text_with_passed_days(
            day_selection, days_in_event=days_in_event
        )
    else:
        print("Not found, doing all days")
        day_selector_for_all_days_at_event = event.day_selector_for_days_in_event()
        return day_selector_for_all_days_at_event

def get_health_from_event_row(row: RowInRegistrationData):
    return row.get_item(CADET_HEALTH, "")
