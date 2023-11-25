from dataclasses import dataclass
import datetime

from app.data_access.configuration.configuration import (
    MIN_CADET_AGE,
    MAX_CADET_AGE,
    SIMILARITY_LEVEL_TO_WARN_DATE,
    SIMILARITY_LEVEL_TO_WARN_NAME,
)
from app.objects.generic import GenericSkipperManObject, GenericListOfObjects
from app.objects.utils import transform_str_from_date, similar
from app.objects.constants import arg_not_passed, DAYS_IN_YEAR



@dataclass
class Cadet(GenericSkipperManObject):
    first_name: str
    surname: str
    date_of_birth: datetime.date
    id: str = arg_not_passed

    def __repr__(self):
        return "%s %s (%s)" % (
            self.first_name.title(),
            self.surname.title(),
            str(self.date_of_birth),
        )

    def __eq__(self, other):
        return (self.first_name==other.first_name) and (self.surname==other.surname) and (self.date_of_birth==other.date_of_birth)

    def __hash__(self):
        return hash(self.first_name+"_"+self.surname+"_"+self._date_of_birth_as_str)

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
    def _date_of_birth_as_str(self) -> str:
        dob = self.date_of_birth
        return transform_str_from_date(dob)

    def similarity_name(self, other_cadet: "Cadet") -> float:
        return similar(self.name, other_cadet.name)

    def similarity_dob(self, other_cadet: "Cadet") -> float:
        return similar(self._date_of_birth_as_str, other_cadet._date_of_birth_as_str)


class ListOfCadets(GenericListOfObjects):

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


default_cadet = Cadet(first_name=" ", surname=" ", date_of_birth=datetime.date.today() - datetime.timedelta(days=8 * 365))
