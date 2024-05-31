from collections import Counter
from dataclasses import dataclass
from typing import List

from app.objects.cadets import Cadet, ListOfCadets

from app.objects.generic import GenericSkipperManObject, GenericListOfObjects
UNALLOCATED_COLOUR = ""

@dataclass
class CadetWithClothingAtEvent(GenericSkipperManObject):
    cadet_id:str
    size: str
    colour: str = UNALLOCATED_COLOUR


class ListOfCadetsWithClothingAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetWithClothingAtEvent

    def add_new_cadet_with_clothing_size_and_optionally_colour(self, cadet_id: str, size: str, colour: str = UNALLOCATED_COLOUR):
        assert cadet_id not in self.list_of_cadet_ids()
        self.append(CadetWithClothingAtEvent(cadet_id=cadet_id,
                                             size=size,
                                             colour=colour))

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
        object.size=size

    def object_with_cadet_id(self, cadet_id) -> CadetWithClothingAtEvent:
        list_of_ids = self.list_of_cadet_ids()
        idx = list_of_ids.index(cadet_id)

        return self[idx]

    def filter_for_list_of_cadet_ids(self, list_of_cadet_ids: List[str]):
        return ListOfCadetsWithClothingAtEvent([object for object in self if object.cadet_id in list_of_cadet_ids])

@dataclass
class CadetObjectWithClothingAtEvent(GenericSkipperManObject):
    cadet: Cadet
    size: str
    colour: str = UNALLOCATED_COLOUR

    @property
    def has_colour(self):
        return not self.colour==UNALLOCATED_COLOUR

class ListOfCadetObjectsWithClothingAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetObjectWithClothingAtEvent

    def colours(self):
        colours = [object.colour for object in self]

        return colours

    def filter_for_surname(self, surname:str):
        return ListOfCadetObjectsWithClothingAtEvent([object for object in self if object.cadet.surname==surname])

    def sort_by(self, sort_by: str):
        if sort_by==SORT_BY_FIRSTNAME:
            return self.sort_by_firstname()
        elif sort_by==SORT_BY_SURNAME:
            return self.sort_by_surname()
        elif sort_by==SORT_BY_DOB_ASC:
            return self.sort_by_dob_asc()
        elif sort_by==SORT_BY_DOB_DSC:
            return self.sort_by_dob_desc()
        elif sort_by==SORT_BY_SIZE:
            return self.sort_by_size()
        elif sort_by==SORT_BY_COLOUR:
            return self.sort_by_colour()
        else:
            raise  "Sort %s not known" % sort_by

    def sort_by_surname(self):
        return ListOfCadetObjectsWithClothingAtEvent(sorted(self, key=lambda x: x.cadet.surname))

    def sort_by_firstname(self):
        return ListOfCadetObjectsWithClothingAtEvent(sorted(self, key=lambda x: x.cadet.first_name))

    def sort_by_name(self):
        return ListOfCadetObjectsWithClothingAtEvent(sorted(self, key=lambda x: x.cadet.name))

    def sort_by_dob_asc(self):
        return ListOfCadetObjectsWithClothingAtEvent(sorted(self, key=lambda x: x.cadet.date_of_birth))

    def sort_by_dob_desc(self):
        return ListOfCadetObjectsWithClothingAtEvent(sorted(self, key=lambda x: x.cadet.date_of_birth, reverse=True))

    def sort_by_size(self):
        return ListOfCadetObjectsWithClothingAtEvent(sorted(self, key=lambda x: x.size))

    def sort_by_colour(self):
        return ListOfCadetObjectsWithClothingAtEvent(sorted(self, key=lambda x: x.colour))

    @classmethod
    def from_list_of_cadets(cls, list_of_cadets: ListOfCadets, list_of_cadets_with_clothing: ListOfCadetsWithClothingAtEvent):
        return ListOfCadetObjectsWithClothingAtEvent(
            [
                CadetObjectWithClothingAtEvent(
                    cadet=list_of_cadets.cadet_with_id(cadet_id=cadet_with_clothing.cadet_id),
                    size =cadet_with_clothing.size,
                    colour=cadet_with_clothing.colour
                )

                for cadet_with_clothing in list_of_cadets_with_clothing
            ]
        )

    def get_colour_options(self) -> List[str]:
        colours = [object.colour for object in self]

        return list(set(colours))

    def get_clothing_size_options(self) -> List[str]:
        sizes = [object.size for object in self]

        return list(set(sizes))


SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
SORT_BY_DOB_ASC = "Sort by date of birth, ascending"
SORT_BY_DOB_DSC = "Sort by date of birth, descending"
SORT_BY_SIZE = "Sort by size"
SORT_BY_COLOUR = "Sort by colour"
all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC, SORT_BY_SIZE, SORT_BY_COLOUR]
