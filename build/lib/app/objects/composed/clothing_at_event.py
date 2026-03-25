from dataclasses import dataclass
from typing import List, Dict, Tuple

from app.objects.utilities.exceptions import arg_not_passed, missing_data

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.clothing import (
    UNALLOCATED_COLOUR,
    ClothingAtEvent,
    no_clothing_requirements,
)
from app.objects.utilities.generic_list_of_objects import GenericListOfObjects
from app.objects.utilities.generic_objects import GenericSkipperManObject


@dataclass
class CadetWithClothingAtEvent(GenericSkipperManObject):
    cadet: Cadet
    size: str
    colour: str = UNALLOCATED_COLOUR

    @classmethod
    def from_dict_tuple(cls, dict_tuple: Tuple[Cadet, ClothingAtEvent]):
        cadet, clothing = dict_tuple
        return cls(cadet=cadet, size=clothing.size, colour=clothing.colour)


class ListOfCadetsWithClothingAtEvent(GenericListOfObjects):
    pass


class DictOfCadetsWithClothingAtEvent(Dict[Cadet, ClothingAtEvent]):
    @property
    def list_of_cadets(self):
        return ListOfCadets(list(self.keys()))

    def does_cadet_have_clothing(
        self,
        cadet: Cadet,
    ) -> bool:
        clothing = self.clothing_for_cadet(cadet, default=missing_data)
        return not clothing is missing_data

    def as_list(self) -> ListOfCadetsWithClothingAtEvent:
        return ListOfCadetsWithClothingAtEvent(
            [
                CadetWithClothingAtEvent.from_dict_tuple(cadet_with_clothing)
                for cadet_with_clothing in self.items()
            ]
        )

    def sort_by_colour_and_firstname(self) -> "DictOfCadetsWithClothingAtEvent":
        new_list_of_cadets = []
        for colour in self.get_colour_options():
            dict_this_colour = self.filter_for_colour(colour)
            dict_this_colour_sorted_by_name = dict_this_colour.sort_by_firstname()
            cadets_this_colour = dict_this_colour_sorted_by_name.list_of_cadets
            new_list_of_cadets = new_list_of_cadets + cadets_this_colour

        return self.filter_for_list_of_cadets(new_list_of_cadets)

    def count_of_size_and_colour(self, size: str, colour: str) -> int:
        return len(
            [
                clothing
                for clothing in self.values()
                if clothing.size == size and clothing.colour == colour
            ]
        )

    def colours(self):
        colours = [clothing.colour for clothing in self.values()]

        return colours

    def filter_for_list_of_cadets(self, list_of_cadets: ListOfCadets):
        raw_dict = dict(
            [
                (cadet, self.clothing_for_cadet(cadet))
                for cadet in list_of_cadets
                if cadet in self.list_of_cadets
            ]
        )
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def filter_for_colour(self, colour: str):
        raw_dict = dict(
            [
                (cadet, clothing)
                for cadet, clothing in self.items()
                if clothing.colour == colour
            ]
        )

        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def remove_if_in_list_of_cadets(self, list_of_cadets: ListOfCadets):
        raw_dict = dict(
            [
                (cadet, clothing)
                for cadet, clothing in self.items()
                if cadet not in list_of_cadets
            ]
        )
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def filter_for_surname(self, surname: str):
        raw_dict = dict(
            [
                (cadet, clothing)
                for cadet, clothing in self.items()
                if cadet.surname == surname
            ]
        )
        return DictOfCadetsWithClothingAtEvent(raw_dict)

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
        raw_dict = dict(sorted(self.items(), key=lambda x: x[0].surname))
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def sort_by_firstname(self):
        raw_dict = dict(sorted(self.items(), key=lambda x: x[0].first_name))
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def sort_by_name(self):
        raw_dict = dict(sorted(self.items(), key=lambda x: x[0].name))
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def sort_by_dob_asc(self):
        raw_dict = dict(sorted(self.items(), key=lambda x: x[0].date_of_birth))
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def sort_by_dob_desc(self):
        raw_dict = dict(sorted(self.items(), key=lambda x: x[0], reverse=True))
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def sort_by_size(self):
        raw_dict = dict(sorted(self.items(), key=lambda x: x[1].size))
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def sort_by_colour(self):
        raw_dict = dict(sorted(self.items(), key=lambda x: x[1].colour))
        return DictOfCadetsWithClothingAtEvent(raw_dict)

    def get_colour_options(self) -> List[str]:
        colours = [clothing.colour for clothing in self.values()]

        return list(set(colours))

    def get_clothing_size_options(self) -> List[str]:
        sizes = [clothing.size for clothing in self.values()]

        return list(set(sizes))

    def change_colour_group_for_cadet(self, cadet: Cadet, colour: str):
        clothing_for_cadet = self.clothing_for_cadet(cadet)
        clothing_for_cadet.colour = colour
        self[cadet] = clothing_for_cadet

    def clothing_for_cadet(
        self, cadet: Cadet, default=arg_not_passed
    ) -> ClothingAtEvent:
        if default is arg_not_passed:
            default = no_clothing_requirements
        clothing = self.get(cadet, default)

        return clothing


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
