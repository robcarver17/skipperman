from dataclasses import dataclass

from app.objects.volunteers import Volunteer

from app.objects.day_selectors import (
    DaySelector,
    day_selector_stored_format_from_text,
    day_selector_to_text_in_stored_format,
    Day,
)
from app.objects.exceptions import missing_data, MissingData, MultipleMatches
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.utils import clean_up_dict_with_nans

LIST_KEY = "list_of_associated_cadet_id"
AVAILABILITY_KEY = "availablity"
NOTES = "notes"


@dataclass
class VolunteerAtEventWithId(GenericSkipperManObject):
    volunteer_id: str
    availablity: DaySelector
    list_of_associated_cadet_id: list  ## no longer used
    preferred_duties: str = ""  ## information only
    same_or_different: str = ""  ## information only
    any_other_information: str = (
        ""  ## information only - double counted as required twice
    )
    notes: str = ""


    def clear_user_data(self):
        self.any_other_information = ""
        self.notes = ""

    @classmethod
    def from_dict_of_str(cls, dict_with_str):
        dict_with_str = clean_up_dict_with_nans(dict_with_str)
        list_of_cadet_ids_as_str = str(dict_with_str[LIST_KEY])
        if len(list_of_cadet_ids_as_str) == 0:
            list_of_cadet_ids = []
        else:
            list_of_cadet_ids = list_of_cadet_ids_as_str.split(",")
            list_of_cadet_ids = [
                str(int(float(cadet_id))) for cadet_id in list_of_cadet_ids
            ]

        availability_as_str = dict_with_str[AVAILABILITY_KEY]
        if type(availability_as_str) is not str:
            availability_as_str = ""  ## corner case

        availability = day_selector_stored_format_from_text(availability_as_str)

        return cls(
            volunteer_id=str(dict_with_str["volunteer_id"]),
            preferred_duties=str(dict_with_str["preferred_duties"]),
            same_or_different=str(dict_with_str["same_or_different"]),
            any_other_information=str(dict_with_str["any_other_information"]),
            list_of_associated_cadet_id=list_of_cadet_ids,
            availablity=availability,
            notes=dict_with_str["notes"],
        )

    def as_str_dict(self) -> dict:
        as_dict = self.as_dict()

        ## all strings except the list
        list_of_associated_cadets = self.list_of_associated_cadet_id
        list_of_associated_cadets_as_str = ",".join(list_of_associated_cadets)
        as_dict[LIST_KEY] = list_of_associated_cadets_as_str

        availability = self.availablity
        as_dict[AVAILABILITY_KEY] = day_selector_to_text_in_stored_format(availability)

        return as_dict

    def available_on_day(self, day: Day) -> bool:
        return self.availablity.available_on_day(day)


class ListOfVolunteersAtEventWithId(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerAtEventWithId

    def clear_user_data(self):
        for volunteer_at_event in self:
            volunteer_at_event.clear_private_data()

    def update_notes(self, volunteer: Volunteer, new_notes: str):
        volunteer_at_event = self.volunteer_at_event_with_id(volunteer.id)
        volunteer_at_event.notes = new_notes

    def make_volunteer_available_on_day(self, volunteer: Volunteer, day: Day):
        volunteer_at_event = self.volunteer_at_event_with_id(volunteer.id)
        volunteer_at_event.availablity.make_available_on_day(day)

    def make_volunteer_unavailable_on_day(self, volunteer: Volunteer, day: Day):
        volunteer_at_event = self.volunteer_at_event_with_id(volunteer.id)
        volunteer_at_event.availablity.make_unavailable_on_day(day)

    def remove_volunteer_with_id(self, volunteer_id: str):
        idx_of_volunteer_at_event = self.index_of_volunteer_at_event_with_id(
            volunteer_id
        )
        if idx_of_volunteer_at_event is missing_data:
            raise Exception("Can't drop non existent volunteer")
        else:
            del self[idx_of_volunteer_at_event]

    def volunteer_at_event_with_id(self, volunteer_id: str) -> VolunteerAtEventWithId:
        index_of_matching_volunteer = self.index_of_volunteer_at_event_with_id(
        volunteer_id
        )

        return self[index_of_matching_volunteer]

    def index_of_volunteer_at_event_with_id(self, volunteer_id: str) -> int:
        list_of_ids = self.list_of_volunteer_ids
        list_of_matching_indices = [
            idx for idx, item_id in enumerate(list_of_ids) if item_id == volunteer_id
        ]
        if len(list_of_matching_indices) == 0:
            raise MissingData
        elif len(list_of_matching_indices) == 1:
            return list_of_matching_indices[0]
        else:
            raise MultipleMatches("A volunteer can't appear more than once at an event")

    @property
    def list_of_volunteer_ids(self) -> list:
        return [str(object.volunteer_id) for object in self]

    def add_new_volunteer(self, volunteer_at_event: VolunteerAtEventWithId):
        if self.volunteer_already_exist(volunteer_at_event):
            raise Exception(
                "Can't add volunteer with id %s to event again"
                % volunteer_at_event.volunteer_id
            )

        self.append(volunteer_at_event)

    def volunteer_already_exist(self, volunteer_at_event: VolunteerAtEventWithId):
        try:
            self.volunteer_at_event_with_id(
                volunteer_id=volunteer_at_event.volunteer_id
            )
            return True
        except MissingData:
            return False

    def sort_by_list_of_volunteer_ids(
        self, list_of_ids
    ) -> "ListOfVolunteersAtEventWithId":
        new_list_of_volunteers_at_event = [
            self.volunteer_at_event_with_id(id) for id in list_of_ids
        ]
        new_list_of_volunteers_at_event = [
            volunteer_at_event
            for volunteer_at_event in new_list_of_volunteers_at_event
            if volunteer_at_event is not missing_data
        ]

        return ListOfVolunteersAtEventWithId(new_list_of_volunteers_at_event)
