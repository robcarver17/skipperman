from dataclasses import dataclass

from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,

)
from app.objects.utilities.generic_objects import GenericSkipperManObject

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

    def list_of_cadet_ids(self):
        return [object.cadet_id for object in self]



@dataclass
class ClothingAtEvent:
    size: str = UNALLOCATED_SIZE
    colour: str = UNALLOCATED_COLOUR

    @property
    def has_colour(self):
        return not self.colour == UNALLOCATED_COLOUR


    @classmethod
    def create_empty(cls):
        return cls()


no_clothing_requirements = ClothingAtEvent.create_empty()
