from dataclasses import dataclass

from app.objects.day_selectors import DaySelector, day_selector_stored_format_from_text, \
    day_selector_to_text_in_stored_format, Day
from app.objects.exceptions import missing_data
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
    list_of_associated_cadet_id: list
    preferred_duties: str = ""  ## information only
    same_or_different: str = ""  ## information only
    any_other_information: str = (
        ""  ## information only - double counted as required twice
    )
    notes: str = ""

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

    def is_volunteer_already_at_event(self, volunteer_id: str):
        all_ids = self.list_of_volunteer_ids
        return str(volunteer_id) in all_ids

    def list_of_volunteer_ids_associated_with_cadet_id(self, cadet_id: str):
        list_of_volunteers = self.list_of_volunteers_associated_with_cadet_id(cadet_id)
        return list_of_volunteers.list_of_volunteer_ids

    def list_of_volunteers_associated_with_cadet_id(self, cadet_id: str):
        return ListOfVolunteersAtEventWithId(
            [
                volunteer_at_event
                for volunteer_at_event in self
                if cadet_id in volunteer_at_event.list_of_associated_cadet_id
            ]
        )

    def update_volunteer_at_event(self, volunteer_at_event: VolunteerAtEventWithId):
        current_volunteer_idx = self.index_of_volunteer_at_event_with_id(
            volunteer_at_event.volunteer_id
        )
        if current_volunteer_idx is missing_data:
            raise Exception("Can't update if volunteer doesn't exist at event")

        ## ignore warning, it's an in place replacement
        self[current_volunteer_idx] = volunteer_at_event

    def remove_volunteer_with_id(self, volunteer_id: str):
        idx_of_volunteer_at_event = self.index_of_volunteer_at_event_with_id(
            volunteer_id
        )
        if idx_of_volunteer_at_event is missing_data:
            pass
        else:
            del self[idx_of_volunteer_at_event]

    def update_volunteer_notes_at_event(self, volunteer_id: str, new_notes: str):
        volunteer_at_event = self.volunteer_at_event_with_id(volunteer_id)
        volunteer_at_event.notes = new_notes

    def remove_cadet_id_association_from_volunteer(
        self, cadet_id: str, volunteer_id: str
    ):
        volunteer_at_event = self.volunteer_at_event_with_id(volunteer_id)
        if volunteer_at_event is missing_data:
            return None
        associated_cadets = volunteer_at_event.list_of_associated_cadet_id
        if cadet_id not in associated_cadets:
            return None

        associated_cadets.remove(cadet_id)

    def volunteer_at_event_with_id(self, volunteer_id: str) -> VolunteerAtEventWithId:
        index_of_matching_volunteer = self.index_of_volunteer_at_event_with_id(
            volunteer_id
        )
        if index_of_matching_volunteer is missing_data:
            return missing_data
        else:
            return self[index_of_matching_volunteer]

    def index_of_volunteer_at_event_with_id(self, volunteer_id: str) -> int:
        list_of_ids = self.list_of_volunteer_ids
        list_of_matching_indices = [
            idx for idx, item_id in enumerate(list_of_ids) if item_id == volunteer_id
        ]
        if len(list_of_matching_indices) == 0:
            return missing_data
        elif len(list_of_matching_indices) == 1:
            return list_of_matching_indices[0]
        else:
            raise Exception("A volunteer can't appear more than once at an event")

    @property
    def list_of_volunteer_ids(self) -> list:
        return [str(object.volunteer_id) for object in self]

    def add_volunteer_with_just_id(self, volunteer_id: str, availability: DaySelector):
        if volunteer_id in self.list_of_volunteer_ids:
            return
        new_volunteer = VolunteerAtEventWithId(
            volunteer_id=volunteer_id,
            availablity=availability,
            list_of_associated_cadet_id=[],
        )
        self.append(new_volunteer)

    def add_new_volunteer(self, volunteer_at_event: VolunteerAtEventWithId):
        existing_volunteer_at_event = self.volunteer_at_event_with_id(
            volunteer_id=volunteer_at_event.volunteer_id
        )
        if existing_volunteer_at_event is missing_data:
            self.append(volunteer_at_event)
        else:
            raise Exception(
                "Can't add volunteer with id %s to event again"
                % volunteer_at_event.volunteer_id
            )

    def add_cadet_id_to_existing_volunteer(self, volunteer_id: str, cadet_id: str):
        existing_volunteer_at_event = self.volunteer_at_event_with_id(
            volunteer_id=volunteer_id
        )
        add_cadet_association_to_existing_volunteer_with_cadet_id(
            existing_volunteer_at_event=existing_volunteer_at_event, cadet_id=cadet_id
        )

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

    def list_of_volunteers_available_on_given_day(
        self, day: Day
    ) -> "ListOfVolunteersAtEventWithId":
        new_list_of_volunteers_at_event = [
            volunteer for volunteer in self if volunteer.available_on_day(day)
        ]
        return ListOfVolunteersAtEventWithId(new_list_of_volunteers_at_event)


def add_cadet_association_to_existing_volunteer(
    existing_volunteer_at_event: VolunteerAtEventWithId,
    new_volunteer_at_event: VolunteerAtEventWithId,
):
    try:
        assert len(new_volunteer_at_event.list_of_associated_cadet_id) == 1
    except:
        raise Exception(
            "A new volunteer at an event can only have one cadet associated with them"
        )
    cadet_id = new_volunteer_at_event.list_of_associated_cadet_id[0]
    add_cadet_association_to_existing_volunteer_with_cadet_id(
        existing_volunteer_at_event=existing_volunteer_at_event, cadet_id=cadet_id
    )


def add_cadet_association_to_existing_volunteer_with_cadet_id(
    existing_volunteer_at_event: VolunteerAtEventWithId, cadet_id: str
):
    if str(cadet_id) in existing_volunteer_at_event.list_of_associated_cadet_id:
        pass
    else:
        existing_volunteer_at_event.list_of_associated_cadet_id.append(cadet_id)
