
from dataclasses import dataclass
from typing import Dict

from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject, dict_from_str, dict_as_str
from app.objects.utilities.generic_list_of_objects import get_idx_of_unique_object_with_multiple_attr_in_list

@dataclass
class GroupNamesForEventsAndCadetPersistentVersionWithIds(GenericSkipperManObject):
    cadet_id: str
    dict_of_event_ids_and_group_names: dict[str, str]

    @classmethod
    def from_dict_of_str(cls, dict_with_str: Dict[str,str]):
        cadet_id = dict_with_str['cadet_id']
        dict_of_event_ids_and_group_names = dict_with_str['dict_of_event_ids_and_group_names']
        dict_of_event_ids_and_group_names = dict_from_str(dict_of_event_ids_and_group_names)

        return cls(cadet_id=cadet_id, dict_of_event_ids_and_group_names=dict_of_event_ids_and_group_names)

class ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return GroupNamesForEventsAndCadetPersistentVersionWithIds

    def get_dict_for_cadet_id(self, cadet_id: str) -> Dict[str,str]:
        idx = get_idx_of_unique_object_with_multiple_attr_in_list(some_list=self,
                                                                  dict_of_attributes={
                                                                      'cadet_id': cadet_id
                                                                  }, default=None)
        if idx is None:
            return {}

        return self[idx].dict_of_event_ids_and_group_names

    def update_does_not_update_core_data(self, cadet_id: str, dict_of_event_ids_and_group_names:  Dict[str, str]):
        idx = get_idx_of_unique_object_with_multiple_attr_in_list(some_list=self,
                                                                  dict_of_attributes={
                                                                      'cadet_id': cadet_id
                                                                  }, default=None)
        if idx is None:
            self.append(GroupNamesForEventsAndCadetPersistentVersionWithIds(
                cadet_id=cadet_id,
                dict_of_event_ids_and_group_names=dict_of_event_ids_and_group_names))
        else:
            existing = self[idx]
            existing.dict_of_event_ids_and_group_names = dict_of_event_ids_and_group_names

