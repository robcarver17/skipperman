from dataclasses import dataclass
from typing import List

from app.objects.exceptions import arg_not_passed, missing_data
from app.objects.generic_list_of_objects import GenericListOfObjects, get_unique_object_with_attr_in_list
from app.objects.generic_objects import GenericSkipperManObject

UNALLOCATED_COLOUR = ""
UNALLOCATED_SIZE = ""


@dataclass
class CadetWithClothingAndIdsAtEvent(GenericSkipperManObject):
    cadet_id: str
    size: str = UNALLOCATED_SIZE
    colour: str = UNALLOCATED_COLOUR


class ListOfCadetsWithClothingAndIdsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetWithClothingAndIdsAtEvent

    def add_new_cadet_with_clothing_size_and_optionally_colour(
        self, cadet_id: str, size: str, colour: str = UNALLOCATED_COLOUR
    ):
        assert cadet_id not in self.list_of_cadet_ids()
        self.append(
            CadetWithClothingAndIdsAtEvent(cadet_id=cadet_id, size=size, colour=colour)
        )

    def list_of_cadet_ids(self):
        return [object.cadet_id for object in self]

    def change_colour_group_for_cadet(self, cadet_id: str, colour: str):
        object = self.object_with_cadet_id(cadet_id)
        object.colour = colour

    def remove_clothing_for_cadet_at_event(self, cadet_id:str):
        object_with_cadet_id = self.object_with_cadet_id(cadet_id, default=missing_data)
        if object_with_cadet_id is missing_data:
            return
        self.remove(object_with_cadet_id)

    def clear_colour_group_for_cadet(
        self,
        cadet_id: str,
    ):
        object = self.object_with_cadet_id(cadet_id)
        object.colour = UNALLOCATED_COLOUR

    def change_clothing_size_for_cadet(self, cadet_id: str, size: str):
        object = self.object_with_cadet_id(cadet_id)
        object.size = size

    def object_with_cadet_id(self, cadet_id: str, default=arg_not_passed) -> CadetWithClothingAndIdsAtEvent:
        return get_unique_object_with_attr_in_list(
        some_list=self,
            attr_name='cadet_id',
            attr_value=cadet_id,
            default=default
        )

    def filter_for_list_of_cadet_ids(self, list_of_cadet_ids: List[str]):
        return ListOfCadetsWithClothingAndIdsAtEvent(
            [object for object in self if object.cadet_id in list_of_cadet_ids]
        )


@dataclass
class ClothingAtEvent:
    size: str = UNALLOCATED_SIZE
    colour: str = UNALLOCATED_COLOUR

    @property
    def has_colour(self):
        return not self.colour == UNALLOCATED_COLOUR

    def clear_colour(self):
        self.colour = UNALLOCATED_COLOUR

    @classmethod
    def create_empty(cls):
        return cls()

no_clothing_requirements= ClothingAtEvent.create_empty()