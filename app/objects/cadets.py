from dataclasses import dataclass
import datetime

from app.data_access.configuration.configuration import (
    MIN_CADET_AGE,
    MAX_CADET_AGE,
    SIMILARITY_LEVEL_TO_WARN_DATE,
    SIMILARITY_LEVEL_TO_WARN_NAME,
)
from app.objects.generic import GenericSkipperManObjectWithIds, GenericListOfObjectsWithIds
from app.objects.utils import transform_date_into_str, similar
from app.objects.constants import arg_not_passed, DAYS_IN_YEAR, missing_data
from app.objects.utils import union_of_x_and_y

@dataclass
class Cadet(GenericSkipperManObjectWithIds):
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
        return \
            self.has_same_name(other)\
            and self.date_of_birth == other.date_of_birth

    def has_same_name(self, other):
        return self.first_name==other.first_name and self.surname == other.surname

    def __hash__(self):
        return hash(
            self.first_name + "_" + self.surname + "_" + self._date_of_birth_as_str
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
    def _date_of_birth_as_str(self) -> str:
        dob = self.date_of_birth
        return transform_date_into_str(dob)

    def similarity_name(self, other_cadet: "Cadet") -> float:
        return similar(self.name, other_cadet.name)

    def similarity_surname(self, other_cadet: "Cadet") -> float:
        return similar(self.surname, other_cadet.surname)

    def similarity_dob(self, other_cadet: "Cadet") -> float:
        return similar(self._date_of_birth_as_str, other_cadet._date_of_birth_as_str)

multiple_matches = object()

class ListOfCadets(GenericListOfObjectsWithIds):
    def matching_cadet(self, cadet: Cadet, exact_match_required: bool = False) -> Cadet:
        exact_match = [cadet_in_list for cadet_in_list in self if cadet==cadet_in_list]
        if len(exact_match)==1:
            return exact_match[0]
        elif len(exact_match)>1:
            raise Exception("Multiple matching cadets found!")

        ### no exact matches required
        if exact_match_required:
            return missing_data
        else:
            return self.matching_cadets_on_name_only(cadet)

    def matching_cadets_on_name_only(self, cadet: Cadet) -> Cadet:
        names_match = [cadet_in_list for cadet_in_list in self if cadet.has_same_name(cadet_in_list)]

        if len(names_match)>1:
            ## multiple matches, as good as missing data
            return missing_data
        elif len(names_match)==0:
            return missing_data

        return names_match[0]

    def exact_match(self, cadet: Cadet) -> Cadet:
        return self[self.index(cadet)]

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
        similar_dob = self.similar_dob(cadet, dob_threshold=dob_threshold)
        similar_names = self.similar_names(cadet, name_threshold=name_threshold)
        joint_list_of_similar_cadets = union_of_x_and_y(similar_names, similar_dob)

        return ListOfCadets(joint_list_of_similar_cadets)

    def similar_names(self, cadet: Cadet, name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,):
        similar_names = [
            other_cadet
            for other_cadet in self
            if cadet.similarity_name(other_cadet) > name_threshold
        ]

        return ListOfCadets(similar_names)

    def similar_dob(self, cadet: Cadet, dob_threshold: float = SIMILARITY_LEVEL_TO_WARN_DATE,):
        similar_dob = [
            other_cadet
            for other_cadet in self
            if cadet.similarity_dob(other_cadet) > dob_threshold
        ]

        return ListOfCadets(similar_dob)

    def similar_surnames(self, cadet: Cadet, name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,):
        similar_surnames = [
            other_cadet
            for other_cadet in self
            if cadet.similarity_surname(other_cadet) > name_threshold
        ]

        return ListOfCadets(similar_surnames)

    def id_given_name(self, name: str):
        ids = [cadet.id for cadet in self if cadet.name==name]
        if len(ids)==0:
            return missing_data
        if len(ids)>1:
            raise Exception("Can't have multiple cadets with same name")

        return ids[0]

def is_cadet_age_surprising(cadet: Cadet):
    age = cadet.approx_age_years()

    return age < MIN_CADET_AGE or age > MAX_CADET_AGE


DEFAULT_DATE_OF_BIRTH = datetime.date(1970,1,1)

default_cadet = Cadet(
    first_name=" ",
    surname=" ",
    date_of_birth=DEFAULT_DATE_OF_BIRTH
)

