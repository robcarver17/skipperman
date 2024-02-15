
from dataclasses import dataclass
from typing import List

from app.objects.generic import GenericSkipperManObject,  GenericListOfObjects
from app.objects.food import FoodRequirements, no_food_requirements
from app.objects.day_selectors import DaySelector, day_selector_stored_format_from_text, day_selector_to_text_in_stored_format
from app.objects.constants import missing_data
from app.objects.utils import clean_up_dict_with_nans


NO_VOLUNTEER_ALLOCATED = "NO_volunteer_allocated"

@dataclass
class RowIDAndIndex:
    row_id: str
    volunteer_index: int

@dataclass
class IdentifiedVolunteerAtEvent(GenericSkipperManObject):
    row_id: str
    volunteer_index: int
    volunteer_id: str

    @property
    def is_not_allocated(self):
        return self.volunteer_id == NO_VOLUNTEER_ALLOCATED

    @classmethod
    def identified_as_processed_not_allocated(cls, row_id: str, volunteer_index: int):
        return cls(row_id=row_id, volunteer_index=volunteer_index, volunteer_id=NO_VOLUNTEER_ALLOCATED)

    @property
    def row_and_index(self):
        return RowIDAndIndex(row_id=self.row_id, volunteer_index=self.volunteer_index)

class ListOfIdentifiedVolunteersAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return IdentifiedVolunteerAtEvent

    def list_of_identified_volunteers_with_volunteer_id(self, volunteer_id: str) -> 'ListOfIdentifiedVolunteersAtEvent':
        items = [item for item in self if item.volunteer_id ==volunteer_id]
        return ListOfIdentifiedVolunteersAtEvent(items)

    def unique_list_of_volunteer_ids(self):
        volunteer_ids = [item.volunteer_id for item in self]
        return list(set(volunteer_ids))

    def append(self, other: IdentifiedVolunteerAtEvent):
        self.add(row_id=other.row_id, volunteer_id=other.volunteer_id, volunteer_index = other.volunteer_index)

    def list_of_row_ids_and_indices(self) -> List[RowIDAndIndex]:
        return [item.row_and_index for item in self]

    def identified_as_processed_not_allocated(self, row_id: str,  volunteer_index: int):
        row_and_index = RowIDAndIndex(row_id=row_id, volunteer_index=volunteer_index)
        try:
            assert row_and_index not in self.list_of_row_ids_and_indices()
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.append(IdentifiedVolunteerAtEvent.identified_as_processed_not_allocated(row_id=row_id, volunteer_index=volunteer_index))

    def add(self, row_id: str, volunteer_id: str, volunteer_index: int):
        row_and_index = RowIDAndIndex(row_id=row_id, volunteer_index=volunteer_index)
        try:
            assert row_and_index not in self.list_of_row_ids_and_indices()
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.append(IdentifiedVolunteerAtEvent(row_id=row_id, volunteer_index=volunteer_index, volunteer_id=volunteer_id))

    def volunteer_id_given_row_id_and_index(self, row_id: str, volunteer_index: int) -> str:
        matching = [item for item in self if item.row_id == row_id and item.volunteer_index == volunteer_index]
        if len(matching)==0:
            raise missing_data
        elif len(matching)>1:
            raise Exception("Can't have same row_id and volunteer index more than once")

        matching_item = matching[0]

        return matching_item.cadet_id



## Must match arguments in dataclass below
LIST_KEY = 'list_of_associated_cadet_id'
AVAILABILITY_KEY = 'availablity'


@dataclass
class VolunteerAtEvent(GenericSkipperManObject):
    volunteer_id: str
    availablity: DaySelector
    list_of_associated_cadet_id: list
    preferred_duties: str = "" ## information only
    same_or_different:  str = ""  ## information only
    any_other_information:  str = ""  ## information only - double counted as required twice


    @classmethod
    def from_dict(cls, dict_with_str):
        dict_with_str = clean_up_dict_with_nans(dict_with_str)
        list_of_cadet_ids_as_str = str(dict_with_str[LIST_KEY])
        if len(list_of_cadet_ids_as_str)==0:
            list_of_cadet_ids =[]
        else:
            list_of_cadet_ids = list_of_cadet_ids_as_str.split(",")

        availability_as_str = dict_with_str[AVAILABILITY_KEY]
        if type(availability_as_str) is not str:
            availability_as_str = "" ## corner case

        availability = day_selector_stored_format_from_text(availability_as_str)

        return cls(
            volunteer_id=str(dict_with_str['volunteer_id']),
            preferred_duties=str(dict_with_str['preferred_duties']),
            same_or_different=str(dict_with_str['same_or_different']),
            any_other_information=str(dict_with_str['any_other_information']),
            list_of_associated_cadet_id=list_of_cadet_ids,
            availablity=availability
        )


    def as_str_dict(self) -> dict:
        as_dict = self.as_dict()

        ## all strings except the list
        list_of_associated_cadets = self.list_of_associated_cadet_id
        list_of_associated_cadets_as_str = ",".join(list_of_associated_cadets)
        as_dict[LIST_KEY] = list_of_associated_cadets_as_str

        availability = self.availablity
        as_dict[AVAILABILITY_KEY] = day_selector_to_text_in_stored_format(availability)

        print("AS DICT: %s" % as_dict)

        return as_dict



class ListOfVolunteersAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerAtEvent

    def list_of_volunteer_ids_associated_with_cadet_id(self, cadet_id: str):
        list_of_volunteers = self.list_of_volunteers_associated_with_cadet_id(cadet_id)
        return list_of_volunteers.list_of_volunteer_ids

    def list_of_volunteers_associated_with_cadet_id(self, cadet_id: str):
        return ListOfVolunteersAtEvent([volunteer_at_event for volunteer_at_event in self if cadet_id in volunteer_at_event.list_of_associated_cadet_id])

    def update_volunteer_at_event(self, volunteer_at_event: VolunteerAtEvent):
        current_volunteer_idx = self.index_of_volunteer_at_event_with_id(volunteer_at_event.volunteer_id)
        if current_volunteer_idx is missing_data:
            raise Exception("Can't update if volunteer doesn't exist at event")

        ## ignore warning, it's an in place replacement
        self[current_volunteer_idx] = volunteer_at_event

    def remove_volunteer_with_id(self, volunteer_id: str):
        idx_of_volunteer_at_event = self.index_of_volunteer_at_event_with_id(volunteer_id)
        if idx_of_volunteer_at_event is missing_data:
            pass
        else:
            del(self[idx_of_volunteer_at_event])

    def remove_cadet_id_association_from_volunteer(self, cadet_id: str, volunteer_id:str):
        volunteer_at_event = self.volunteer_at_event_with_id(volunteer_id)
        if volunteer_at_event is missing_data:
            return None
        associated_cadets = volunteer_at_event.list_of_associated_cadet_id
        if cadet_id not in associated_cadets:
            return None

        associated_cadets.remove(cadet_id)

    def volunteer_at_event_with_id(self, volunteer_id: str) -> VolunteerAtEvent:
        index_of_matching_volunteer = self.index_of_volunteer_at_event_with_id(volunteer_id)
        if index_of_matching_volunteer is missing_data:
            return missing_data
        else:
            return self[index_of_matching_volunteer]

    def index_of_volunteer_at_event_with_id(self, volunteer_id: str) -> int:
        list_of_ids = self.list_of_volunteer_ids
        list_of_matching_indices = [idx for idx, item_id in enumerate(list_of_ids) if item_id==volunteer_id]
        if len(list_of_matching_indices)==0:
            return missing_data
        elif len(list_of_matching_indices)==1:
            return list_of_matching_indices[0]
        else:
            raise Exception("A volunteer can't appear more than once at an event")

    @property
    def list_of_volunteer_ids(self) -> list:
        return [object.volunteer_id for object in self]

    def add_volunteer_with_just_id(self, volunteer_id: str, availability: DaySelector):
        if volunteer_id in self.list_of_volunteer_ids:
            return
        new_volunteer = VolunteerAtEvent(volunteer_id=volunteer_id, availablity=availability,
                         list_of_associated_cadet_id=[])
        self.append(new_volunteer)

    def add_new_volunteer(self, volunteer_at_event: VolunteerAtEvent):
        existing_volunteer_at_event = self.volunteer_at_event_with_id(volunteer_id=volunteer_at_event.volunteer_id)
        if existing_volunteer_at_event is missing_data:
            self.append(volunteer_at_event)
        else:
            raise Exception("Can't add volunteer with id %s to event again" % volunteer_at_event.volunteer_id)

    def add_cadet_id_to_existing_volunteer(self, volunteer_id: str, cadet_id: str):
        existing_volunteer_at_event = self.volunteer_at_event_with_id(volunteer_id=volunteer_id)
        add_cadet_association_to_existing_volunteer_with_cadet_id(existing_volunteer_at_event=existing_volunteer_at_event, cadet_id=cadet_id)

    def sort_by_list_of_volunteer_ids(self, list_of_ids) -> 'ListOfVolunteersAtEvent':
        new_list_of_volunteers_at_event = [self.volunteer_at_event_with_id(id) for id in list_of_ids]
        new_list_of_volunteers_at_event = [volunteer_at_event for volunteer_at_event in new_list_of_volunteers_at_event
                                           if volunteer_at_event is not missing_data]

        return ListOfVolunteersAtEvent(new_list_of_volunteers_at_event)

def add_cadet_association_to_existing_volunteer(existing_volunteer_at_event: VolunteerAtEvent, new_volunteer_at_event: VolunteerAtEvent):
    try:
        assert len(new_volunteer_at_event.list_of_associated_cadet_id)==1
    except:
        raise Exception("A new volunteer at an event can only have one cadet associated with them")
    cadet_id = new_volunteer_at_event.list_of_associated_cadet_id[0]
    add_cadet_association_to_existing_volunteer_with_cadet_id(existing_volunteer_at_event=existing_volunteer_at_event,
                                                              cadet_id=cadet_id)

def add_cadet_association_to_existing_volunteer_with_cadet_id(existing_volunteer_at_event: VolunteerAtEvent, cadet_id: str):
    if cadet_id in existing_volunteer_at_event.list_of_associated_cadet_id:
        pass
    else:
        existing_volunteer_at_event.list_of_associated_cadet_id.append(cadet_id)


