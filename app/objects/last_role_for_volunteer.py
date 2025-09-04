
from dataclasses import dataclass

from app.objects.volunteers import Volunteer

from app.objects.day_selectors import (
    DaySelector,
    day_selector_stored_format_from_text,
    day_selector_to_text_in_stored_format,
    Day,
)
from app.objects.utilities.exceptions import (
    missing_data,
    arg_not_passed,
)
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_unique_object_with_attr_in_list,
    get_idx_of_unique_object_with_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.utilities.transform_data import clean_up_dict_with_nans
from app.objects.utilities.generic_list_of_objects import get_idx_of_unique_object_with_multiple_attr_in_list, get_subset_of_list_that_matches_multiple_attr

@dataclass
class MostCommonRoleForVolunteerAcrossEventsWithId(GenericSkipperManObject):
    volunteer_id: str
    role_id: str
    group_id: str


class ListOfMostCommonRoleForVolunteersAcrossEventsWithId(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return MostCommonRoleForVolunteerAcrossEventsWithId

    def update(self, volunteer_id: str, role_id: str, group_id:str):
        idx = get_idx_of_unique_object_with_multiple_attr_in_list(some_list=self,
                                                                  dict_of_attributes={
                                                                      'volunteer_id': volunteer_id
                                                                  }, default=None)
        if idx is None:
            self.append(MostCommonRoleForVolunteerAcrossEventsWithId(
                volunteer_id=volunteer_id,
                group_id=group_id,
                role_id=role_id,
            ))
        else:
            existing = self[idx]
            existing.role_id = role_id
            existing.group_id = group_id
            self[idx] = existing

