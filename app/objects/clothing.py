from dataclasses import dataclass
from typing import List

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject

UNALLOCATED_COLOUR = ""


@dataclass
class CadetWithClothingAndIdsAtEvent(GenericSkipperManObject):
    cadet_id: str
    size: str
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

    def clear_colour_group_for_cadet(
        self,
        cadet_id: str,
    ):
        object = self.object_with_cadet_id(cadet_id)
        object.colour = UNALLOCATED_COLOUR

    def change_clothing_size_for_cadet(self, cadet_id: str, size: str):
        object = self.object_with_cadet_id(cadet_id)
        object.size = size

    def object_with_cadet_id(self, cadet_id) -> CadetWithClothingAndIdsAtEvent:
        list_of_ids = self.list_of_cadet_ids()
        idx = list_of_ids.index(cadet_id)

        return self[idx]

    def filter_for_list_of_cadet_ids(self, list_of_cadet_ids: List[str]):
        return ListOfCadetsWithClothingAndIdsAtEvent(
            [object for object in self if object.cadet_id in list_of_cadet_ids]
        )


