from dataclasses import dataclass
import datetime

from app.data_access.configuration.configuration import (
    MIN_CADET_AGE,
    MAX_CADET_AGE,
    SIMILARITY_LEVEL_TO_WARN_DATE,
    SIMILARITY_LEVEL_TO_WARN_NAME,
)
from app.objects.generic import GenericSkipperManObject, GenericListOfObjects
from app.objects.utils import transform_str_from_date, similar, list_duplicate_indices
from app.objects.constants import arg_not_passed, DAYS_IN_YEAR


@dataclass(frozen=True)
class Cadet(GenericSkipperManObject):
    first_name: str
    surname: str
    date_of_birth: datetime.date

    def __repr__(self):
        return "%s %s (%s)" % (
            self.first_name.title(),
            self.surname.title(),
            str(self.date_of_birth),
        )

    def approx_age_years(self, at_date: datetime.date = arg_not_passed) -> float:
        if at_date is arg_not_passed:
            at_date = datetime.date.today()

        age_delta = at_date - self.date_of_birth
        return age_delta.days / DAYS_IN_YEAR

    @property
    def name(self):
        return self.first_name.title() + " " + self.surname.title()

    @property
    def initial_and_surname(self):
        initial = self.first_name[0].upper()
        return "%s. %s" % (initial, self.surname.title())

    @property
    def id(self) -> str:
        return (
            self.first_name.lower()
            + "_"
            + self.surname.lower()
            + "_"
            + self._date_of_birth_as_str
        )

    @property
    def _date_of_birth_as_str(self) -> str:
        dob = self.date_of_birth
        return transform_str_from_date(dob)

    def similarity_name(self, other_cadet: "Cadet") -> float:
        return similar(self.name, other_cadet.name)

    def similarity_dob(self, other_cadet: "Cadet") -> float:
        return similar(self._date_of_birth_as_str, other_cadet._date_of_birth_as_str)


def cadet_name_from_id(cadet_id: str) -> str:
    first_name, surname, __ = cadet_id.split("_")

    return first_name.title() + " " + surname.title()


class ListOfCadets(GenericListOfObjects):
    def duplicate_indices(self) -> list:
        ## eg if cadets in position 0,3 are the same, and in 5, 20, will return
        #   [[0,3],[5,20]]
        list_of_ids = self.list_of_ids
        list_of_index_of_duplicate_ids = list_duplicate_indices(list_of_ids)

        return list_of_index_of_duplicate_ids

    def sort_by_surname(self):
        return ListOfCadets(sorted(self, key=lambda x: x.surname))

    def sort_by_firstname(self):
        return ListOfCadets(sorted(self, key=lambda x: x.first_name))

    def sort_by_dob_asc(self):
        return ListOfCadets(sorted(self, key=lambda x: x.date_of_birth))

    def sort_by_dob_desc(self):
        return ListOfCadets(sorted(self, key=lambda x: x.date_of_birth, reverse=True))

    @property
    def _object_class_contained(self):
        return Cadet

    def similar_cadets(
        self,
        cadet: Cadet,
        name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,
        dob_threshold: float = SIMILARITY_LEVEL_TO_WARN_DATE,
    ) -> "ListOfCadets":

        similar_dob = [
            other_cadet
            for other_cadet in self
            if cadet.similarity_dob(other_cadet) > dob_threshold
        ]
        similar_names = [
            other_cadet
            for other_cadet in self
            if cadet.similarity_name(other_cadet) > name_threshold
        ]

        joint_list_of_similar_cadets = list(set(similar_dob + similar_names))

        return ListOfCadets(joint_list_of_similar_cadets)


def is_cadet_age_surprising(cadet: Cadet):
    age = cadet.approx_age_years()

    return age < MIN_CADET_AGE or age > MAX_CADET_AGE


default_cadet = Cadet("", "", datetime.date.today() - datetime.timedelta(days=8 * 365))
