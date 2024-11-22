from dataclasses import dataclass
from typing import List

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.clothing import UNALLOCATED_COLOUR, ListOfCadetsWithClothingAndIdsAtEvent
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject


@dataclass
class CadetWithClothingAtEvent(GenericSkipperManObject):
    cadet: Cadet
    size: str
    colour: str = UNALLOCATED_COLOUR

    @property
    def has_colour(self):
        return not self.colour == UNALLOCATED_COLOUR

    def as_dict(self) -> dict:
        return dict(
            Name=self.cadet.name,
            Age=int(self.cadet.approx_age_years()),
            Size=self.size,
            Colour=self.colour,
        )


class ListOfCadetsWithClothingAtEvent(List[CadetWithClothingAtEvent]):
    def __init__(self, raw_list: List[CadetWithClothingAtEvent], list_of_cadets_with_clothing_and_ids: ListOfCadetsWithClothingAndIdsAtEvent):
        super().__init__(raw_list)
        self._list_of_cadets_with_clothing_and_ids = list_of_cadets_with_clothing_and_ids

    def count_of_size_and_colour(self, size: str, colour: str) -> int:
        return len(
            [
                object
                for object in self
                if object.size == size and object.colour == colour
            ]
        )

    def colours(self):
        colours = [object.colour for object in self]

        return colours

    def filter_for_colour(self, colour: str):
        return ListOfCadetsWithClothingAtEvent(
            [object for object in self if object.colour == colour]
        )

    def remove_if_in_list_of_cadet_ids(self, list_of_cadet_ids: List[str]):
        return ListOfCadetsWithClothingAtEvent(
            [object for object in self if object.cadet.id not in list_of_cadet_ids]
        )

    def filter_for_surname(self, surname: str):
        return ListOfCadetsWithClothingAtEvent(
            [object for object in self if object.cadet.surname == surname]
        )

    def sort_by(self, sort_by: str):
        if sort_by == SORT_BY_FIRSTNAME:
            return self.sort_by_firstname()
        elif sort_by == SORT_BY_SURNAME:
            return self.sort_by_surname()
        elif sort_by == SORT_BY_DOB_ASC:
            return self.sort_by_dob_asc()
        elif sort_by == SORT_BY_DOB_DSC:
            return self.sort_by_dob_desc()
        elif sort_by == SORT_BY_SIZE:
            return self.sort_by_size()
        elif sort_by == SORT_BY_COLOUR:
            return self.sort_by_colour()
        else:
            raise "Sort %s not known" % sort_by

    def sort_by_surname(self):
        return ListOfCadetsWithClothingAtEvent(
            sorted(self, key=lambda x: x.cadet.surname)
        )

    def sort_by_firstname(self):
        return ListOfCadetsWithClothingAtEvent(
            sorted(self, key=lambda x: x.cadet.first_name)
        )

    def sort_by_name(self):
        return ListOfCadetsWithClothingAtEvent(
            sorted(self, key=lambda x: x.cadet.name)
        )

    def sort_by_dob_asc(self):
        return ListOfCadetsWithClothingAtEvent(
            sorted(self, key=lambda x: x.cadet.date_of_birth)
        )

    def sort_by_dob_desc(self):
        return ListOfCadetsWithClothingAtEvent(
            sorted(self, key=lambda x: x.cadet.date_of_birth, reverse=True)
        )

    def sort_by_size(self):
        return ListOfCadetsWithClothingAtEvent(sorted(self, key=lambda x: x.size))

    def sort_by_colour(self):
        return ListOfCadetsWithClothingAtEvent(
            sorted(self, key=lambda x: x.colour)
        )


    def get_colour_options(self) -> List[str]:
        colours = [object.colour for object in self]

        return list(set(colours))

    def get_clothing_size_options(self) -> List[str]:
        sizes = [object.size for object in self]

        return list(set(sizes))

    def list_of_cadet_ids(self):
        return [object.cadet.id for object in self]


def compose_list_of_cadets_with_clothing_at_event(list_of_cadets: ListOfCadets,
                                                  list_of_cadets_with_clothing_and_ids: ListOfCadetsWithClothingAndIdsAtEvent,
                                                  ):
    raw_list = [
                CadetWithClothingAtEvent(
                    cadet=list_of_cadets.cadet_with_id(
                        cadet_id=cadet_with_clothing.cadet_id
                    ),
                    size=cadet_with_clothing.size,
                    colour=cadet_with_clothing.colour,
                )
                for cadet_with_clothing in list_of_cadets_with_clothing_and_ids
            ]
    return ListOfCadetsWithClothingAtEvent(
            raw_list=raw_list,
            list_of_cadets_with_clothing_and_ids=list_of_cadets_with_clothing_and_ids
        )

    pass

SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
SORT_BY_DOB_ASC = "Sort by date of birth, ascending"
SORT_BY_DOB_DSC = "Sort by date of birth, descending"
SORT_BY_SIZE = "Sort by size"
SORT_BY_COLOUR = "Sort by colour"
all_sort_types = [
    SORT_BY_SURNAME,
    SORT_BY_FIRSTNAME,
    SORT_BY_DOB_ASC,
    SORT_BY_DOB_DSC,
    SORT_BY_SIZE,
    SORT_BY_COLOUR,
]

