from copy import copy
from dataclasses import dataclass

from app.data_access.configuration.configuration import VOLUNTEER_ROLES, LAKE, RIVER, OTHER, LAKE_VOLUNTEER_ROLES, RIVER_VOLUNTEER_ROLES
from app.objects.generic import GenericSkipperManObject, get_class_instance_from_str_dict, GenericListOfObjects
from app.objects.groups import Group
from app.objects.food import FoodRequirements, no_food_requirements
from app.objects.day_selectors import DaySelector, day_selector_stored_format_from_text, day_selector_to_text_in_stored_format, NO_DAYS_SELECTED
from app.objects.constants import missing_data

## Must match arguments in dataclass below
LIST_KEY = 'list_of_associated_cadet_id'
FOOD_REQUIRED_KEY = 'food_requirements'
AVAILABILITY_KEY = 'availablity'
## FIXME - Boats done seperately


@dataclass
class VolunteerAtEvent(GenericSkipperManObject):
    volunteer_id: str
    availablity: DaySelector
    list_of_associated_cadet_id: list
    food_requirements: FoodRequirements = no_food_requirements
    preferred_duties: str = "" ## information only
    same_or_different:  str = ""  ## information only
    any_other_information:  str = ""  ## information only - double counted as required twice
    #group: str = "" FIXME REMOVE CHANGES BY DAY SET SEPERATELY
    #role: str - FIXME REMOVE CHANGES BY DAY


    @classmethod
    def from_dict(cls, dict_with_str):
        list_of_cadet_ids_as_str = dict_with_str[LIST_KEY]
        if len(list_of_cadet_ids_as_str)==0:
            list_of_cadet_ids=[]
        else:
            list_of_cadet_ids= list_of_cadet_ids_as_str.split(",")

        food_requirements_as_str  =dict_with_str[FOOD_REQUIRED_KEY]
        food_requirements = FoodRequirements.from_str(food_requirements_as_str)

        availability_as_str = dict_with_str[AVAILABILITY_KEY]
        availability = day_selector_stored_format_from_text(availability_as_str)

        return cls(
            volunteer_id=dict_with_str['volunteer_id'],
            preferred_duties=dict_with_str['preferred_duties'],
            same_or_different=dict_with_str['same_or_different'],
            any_other_information=dict_with_str['any_other_information'],
            list_of_associated_cadet_id=list_of_cadet_ids,
            food_requirements=food_requirements,
            availablity=availability
        )


    def as_str_dict(self) -> dict:
        as_dict = self.as_dict()

        ## all strings except the list
        list_of_associated_cadets = self.list_of_associated_cadet_id
        list_of_associated_cadets_as_str = ",".join(list_of_associated_cadets)
        as_dict[LIST_KEY] = list_of_associated_cadets_as_str

        food_requirements = self.food_requirements
        as_dict[FOOD_REQUIRED_KEY] = food_requirements.to_str()

        availability = self.availablity
        as_dict[AVAILABILITY_KEY] = day_selector_to_text_in_stored_format(availability)

        return as_dict

    """
    @property
    def location(self):
        if self.role in LAKE_VOLUNTEER_ROLES:
            return LAKE
        elif self.role in RIVER_VOLUNTEER_ROLES:
            return RIVER
        elif not self.group == "":
            group = Group(self.group)
            if group.is_lake_training():
                return LAKE
            elif group.is_race_group() or group.is_river_training():
                return RIVER

        return OTHER
    """


class ListOfVolunteersAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerAtEvent

    def list_of_volunteer_ids_associated_with_cadet_id(self, cadet_id: str):
        return ListOfVolunteersAtEvent([volunteer_at_event for volunteer_at_event in self if cadet_id in volunteer_at_event.list_of_associated_cadet_id])

    def update_volunteer_at_event(self, volunteer_at_event: VolunteerAtEvent):
        current_volunteer = self.volunteer_at_event_with_id(volunteer_at_event.volunteer_id)
        if current_volunteer is missing_data:
            raise Exception("Can't update if volunteer doesn't exist at event")

        ## ignore warning, it's an in place replacement
        current_volunteer = volunteer_at_event


    def remove_volunteer_with_id(self, volunteer_id: str):
        volunteer_at_event = self.volunteer_at_event_with_id(volunteer_id)
        if volunteer_at_event is missing_data:
            pass
        else:
            del(volunteer_at_event)

    def remove_cadet_id_association_from_volunteer(self, cadet_id: str, volunteer_id:str):
        volunteer_at_event = self.volunteer_at_event_with_id(volunteer_id)
        if volunteer_at_event is missing_data:
            return None
        associated_cadets = volunteer_at_event.list_of_associated_cadet_id
        if cadet_id not in associated_cadets:
            return None

        associated_cadets.remove(cadet_id)

    def volunteer_at_event_with_id(self, volunteer_id: str) -> VolunteerAtEvent:
        list_of_matching_volunteers = [item for item in self if item.volunteer_id==volunteer_id]
        if len(list_of_matching_volunteers)==0:
            return missing_data
        elif len(list_of_matching_volunteers)==1:
            return list_of_matching_volunteers[0]
        else:
            raise Exception("A volunteer can't appear more than once at an event")


    def add_potentially_new_volunteer_with_cadet_association(self, volunteer_at_event: VolunteerAtEvent):
        existing_volunteer_at_event = self.volunteer_at_event_with_id(volunteer_id=volunteer_at_event.volunteer_id)
        if existing_volunteer_at_event is missing_data:
            self.append(volunteer_at_event)
        else:
            add_cadet_association_to_existing_volunteer(existing_volunteer_at_event=existing_volunteer_at_event, new_volunteer_at_event=volunteer_at_event)

def add_cadet_association_to_existing_volunteer(existing_volunteer_at_event: VolunteerAtEvent, new_volunteer_at_event: VolunteerAtEvent):
    try:
        assert len(new_volunteer_at_event.list_of_associated_cadet_id)==1
    except:
        raise Exception("A new volunteer at an event can only have one cadet associated with them")
    cadet_id = new_volunteer_at_event.list_of_associated_cadet_id[0]
    if cadet_id in existing_volunteer_at_event.list_of_associated_cadet_id:
        pass
    else:
        existing_volunteer_at_event.list_of_associated_cadet_id.append(cadet_id)

class CadetWithoutVolunteerAtEvent(GenericSkipperManObject):
    cadet_id: str
    event_id: str

class ListOfCadetsWithoutVolunteersAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return CadetWithoutVolunteerAtEvent

    def list_of_cadet_ids_for_event(self, event_id: str):
        list_of_ids = [item.cadet_id for item in self if item.event_id==event_id]
        return list_of_ids

    def add_cadet_id_without_volunteer(self, cadet_id: str, event_id: str):
        if cadet_id in self.list_of_cadet_ids_for_event(event_id):
            ## already there
            pass
        else:
            self.append(CadetWithoutVolunteerAtEvent(cadet_id=cadet_id, event_id=event_id))