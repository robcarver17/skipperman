from dataclasses import dataclass
import datetime
from typing import List

from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_DATE,
    SIMILARITY_LEVEL_TO_WARN_NAME,
    MIN_AGE_WHEN_CADET_CAN_BE_AT_EVENT_WITHOUT_PARENT,
    MIN_CADET_AGE,
    MAX_CADET_AGE,
)
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.membership_status import (
    MembershipStatus,
    none_member,
    current_member,
    lapsed_member,
    system_unconfirmed_member,
    describe_status,
    user_unconfirmed_member,
)
from app.objects.utils import (
    transform_date_into_str,
    similar,
    transform_str_or_datetime_into_date,
    in_x_not_in_y,
)
from app.objects.exceptions import (
    arg_not_passed,
    DAYS_IN_YEAR,
    MissingData,
    MultipleMatches,
)
from app.objects.utils import union_of_x_and_y

DEFAULT_DATE_OF_BIRTH = datetime.date(1970, 1, 1)


@dataclass
class Cadet(GenericSkipperManObjectWithIds):
    first_name: str
    surname: str
    date_of_birth: datetime.date
    membership_status: MembershipStatus
    id: str = arg_not_passed

    @classmethod
    def new(
        cls,
        first_name: str,
        surname: str,
        date_of_birth: datetime.date,
        membership_status: MembershipStatus,
        id: str = arg_not_passed,
    ):
        return cls(
            first_name=first_name.strip(" ").title(),
            surname=surname.strip(" ").title(),
            date_of_birth=transform_str_or_datetime_into_date(date_of_birth),
            membership_status=membership_status,
            id=id,
        )

    def __repr__(self):
        return "%s %s%s %s" % (
            self.first_name,
            self.surname,
            self.date_of_birth_as_string(),
            describe_status(self.membership_status),
        )

    def date_of_birth_as_string(self):
        if self.date_of_birth == DEFAULT_DATE_OF_BIRTH:
            return ""
        else:
            return " (%s)" % str(self.date_of_birth)

    def __eq__(self, other):
        ## Doesn't consider membership status
        return self.has_same_name(other) and self.date_of_birth == other.date_of_birth

    def __lt__(self, other):
        return self.name < other.name

    def has_same_name(self, other):
        return self.first_name == other.first_name and self.surname == other.surname

    def __hash__(self):
        return hash(
            self.first_name + "_" + self.surname + "_" + self._date_of_birth_as_str
        )

    def add_asterix_to_name(self) -> "Cadet":
        return Cadet(
            first_name=self.first_name,
            surname=self.surname + "*",
            date_of_birth=self.date_of_birth,
            id=self.id,
            membership_status=self.membership_status,
        )

    @classmethod
    def from_name_only(cls, first_name: str, surname: str) -> "Cadet":
        return cls(
            first_name=first_name,
            surname=surname,
            date_of_birth=DEFAULT_DATE_OF_BIRTH,
            membership_status=none_member,
        )

    def replace_all_attributes_except_id_with_those_from_new_cadet(
        self, new_cadet: "Cadet"
    ):
        self.first_name = new_cadet.first_name
        self.surname = new_cadet.surname
        self.date_of_birth = new_cadet.date_of_birth
        self.membership_status = new_cadet.membership_status

    def approx_age_years(self, at_date: datetime.date = arg_not_passed) -> float:
        if at_date is arg_not_passed:
            at_date = datetime.date.today()

        age_delta = at_date - self.date_of_birth
        return age_delta.days / DAYS_IN_YEAR

    @property
    def name(self):
        return self.first_name + " " + self.surname

    @property
    def initial_and_surname(self):
        initial = self.first_name[0].upper()
        return "%s. %s" % (initial, self.surname)

    @property
    def _date_of_birth_as_str(self) -> str:
        dob = self.date_of_birth
        return transform_date_into_str(dob)

    def similarity_name(self, other_cadet: "Cadet") -> float:
        return similar(self.name, other_cadet.name)


    def similarity_surname(self, other_cadet: "Cadet") -> float:
        return similar(self.surname, other_cadet.surname)

    def similarity_dob(self, other_cadet: "Cadet") -> float:
        if self.has_default_date_of_birth or other_cadet.has_default_date_of_birth:
            return 0.0
        else:
            return similar(
                self._date_of_birth_as_str, other_cadet._date_of_birth_as_str
            )

    def day_and_month_of_birth_matches_other_data(self, other_date: datetime.date):
        return (
            self.date_of_birth.day == other_date.day
            and self.date_of_birth.month == other_date.month
        )

    @property
    def has_default_date_of_birth(self):
        return self.date_of_birth == DEFAULT_DATE_OF_BIRTH


class ListOfCadets(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Cadet

    def pop_cadet(self, cadet: Cadet):
        cadet_idx = self.index_of_id(cadet.id)
        return self.pop(cadet_idx)

    def current_members_only(self):
        return ListOfCadets([
            cadet for cadet in self
            if cadet.membership_status==current_member
        ])

    def set_all_current_members_to_temporary_unconfirmed_status(self):
        for cadet in self:
            if cadet.membership_status == current_member:
                cadet.membership_status = system_unconfirmed_member

    def set_all_temporary_unconfirmed_members_to_lapsed_and_return_list(
        self,
    ) -> "ListOfCadets":
        list_of_cadets = []
        for cadet in self:
            if cadet.membership_status == system_unconfirmed_member:
                cadet.membership_status = lapsed_member
                list_of_cadets.append(cadet)

        return ListOfCadets(list_of_cadets)

    def set_all_user_unconfirmed_members_to_non_members_and_return_list(
        self,
    ) -> "ListOfCadets":
        list_of_cadets = []
        for cadet in self:
            if cadet.membership_status == user_unconfirmed_member:
                cadet.membership_status = none_member
                list_of_cadets.append(cadet)

        return ListOfCadets(list_of_cadets)

    def excluding_cadets_from_other_list(self, list_of_cadets: "ListOfCadets"):
        list_of_ids = in_x_not_in_y(self.list_of_ids, list_of_cadets.list_of_ids)
        return self.subset_from_list_of_ids_retaining_order(list_of_ids)

    def add(self, cadet: Cadet):
        if cadet in self:
            ## __eq__ compares name, surname, and DOB
            raise Exception("Cadet %s already in list of existing cadets" % str(cadet))

        cadet_id = self.next_id()
        cadet.id = cadet_id
        self.append(cadet)

        return cadet

    def update_cadet(self, existing_cadet: Cadet, new_cadet: Cadet):
        self.replace_cadet_with_id_with_new_cadet_details(
            existing_cadet_id=existing_cadet.id, new_cadet=new_cadet
        )

    def confirm_cadet_as_member(self, existing_cadet: Cadet):
        existing_cadet.membership_status = current_member
        self.replace_cadet_with_id_with_new_cadet_details(
            existing_cadet_id=existing_cadet.id, new_cadet=existing_cadet
        )

    def replace_cadet_with_id_with_new_cadet_details(
        self, existing_cadet_id: str, new_cadet: Cadet
    ):
        existing_cadet = self.cadet_with_id(existing_cadet_id)
        existing_cadet.replace_all_attributes_except_id_with_those_from_new_cadet(
            new_cadet
        )

    def matching_cadet_with_name(
        self, cadet_name: str, default=arg_not_passed
    ) -> Cadet:
        exact_match = [
            cadet_in_list for cadet_in_list in self if cadet_in_list.name == cadet_name
        ]
        if len(exact_match) == 1:
            return exact_match[0]
        elif len(exact_match) > 1:
            raise MultipleMatches(
                "Multiple matching cadets found looking for %s!" % cadet_name
            )
        elif len(exact_match) == 0:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

    def matching_cadet(self, cadet: Cadet, default=arg_not_passed) -> Cadet:
        exact_match = [
            cadet_in_list for cadet_in_list in self if cadet == cadet_in_list
        ]
        if len(exact_match) == 1:
            return exact_match[0]
        elif len(exact_match) > 1:
            raise MultipleMatches(
                "Multiple matching cadets found looking for %s!" % str(cadet)
            )
        elif len(exact_match) == 0:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

    def sort_by_similarity_name_against_cadet(self, cadet: Cadet):
        similarity_scores_and_cadets = [dict(cadet=cadet_in_list, score=cadet.similarity_name(cadet_in_list)) for cadet_in_list in self]
        return self._sort_by_similarity_given_scores(similarity_scores_and_cadets)

    def sort_by_similarity_dob_against_cadet(self, cadet: Cadet):
        similarity_scores_and_cadets = [dict(cadet=cadet_in_list, score=cadet.similarity_dob(cadet_in_list)) for cadet_in_list in self]
        return self._sort_by_similarity_given_scores(similarity_scores_and_cadets)

    def _sort_by_similarity_given_scores(self, similarity_scores_and_cadets: List[dict]):
        sorted_similarity_scores_and_cadets = sorted(similarity_scores_and_cadets, key=lambda x: x['score'], reverse=True)
        sorted_cadets = [score_and_cadet['cadet'] for score_and_cadet in sorted_similarity_scores_and_cadets]

        return ListOfCadets(sorted_cadets)

    def sort_by_surname(self):
        return ListOfCadets(sorted(self, key=lambda x: x.surname))

    def sort_by_firstname(self):
        return ListOfCadets(sorted(self, key=lambda x: x.first_name))

    def sort_by_name(self):
        return ListOfCadets(sorted(self, key=lambda x: x.name))

    def sort_by_dob_asc(self):
        return ListOfCadets(sorted(self, key=lambda x: x.date_of_birth))

    def sort_by_dob_desc(self):
        return ListOfCadets(sorted(self, key=lambda x: x.date_of_birth, reverse=True))

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

    def similar_names(
        self,
        cadet: Cadet,
        name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,
    ):
        if cadet is default_cadet or cadet is test_cadet:
            return ListOfCadets([])

        similar_names = [
            other_cadet
            for other_cadet in self
            if cadet.similarity_name(other_cadet) > name_threshold
        ]

        return ListOfCadets(similar_names)

    def similar_dob(
        self,
        cadet: Cadet,
        dob_threshold: float = SIMILARITY_LEVEL_TO_WARN_DATE,
    ):
        if (
            cadet is default_cadet
            or cadet is test_cadet
            or cadet.has_default_date_of_birth
        ):
            return ListOfCadets([])

        similar_dob = [
            other_cadet
            for other_cadet in self
            if cadet.similarity_dob(other_cadet) > dob_threshold
        ]

        return ListOfCadets(similar_dob)

    def similar_surnames(
        self,
        cadet: Cadet,
        name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,
    ):
        similar_surnames = [
            other_cadet
            for other_cadet in self
            if cadet.similarity_surname(other_cadet) > name_threshold
        ]

        return ListOfCadets(similar_surnames)


    def cadet_with_id(self, cadet_id: str, default=arg_not_passed) -> Cadet:
        if cadet_id == test_cadet_id:
            return test_cadet

        return self.object_with_id(cadet_id, default=default)


def cadet_is_too_young_to_be_without_parent(cadet: Cadet) -> bool:
    return cadet.approx_age_years() < MIN_AGE_WHEN_CADET_CAN_BE_AT_EVENT_WITHOUT_PARENT


def is_cadet_age_surprising(cadet: Cadet):
    age = cadet.approx_age_years()

    return age < MIN_CADET_AGE or age > MAX_CADET_AGE


SKIP_TEST_CADET_ID = str(-9999)


default_cadet = Cadet(
    first_name=" ",
    surname=" ",
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    membership_status=none_member,
)


test_cadet = Cadet(
    "Test",
    "",
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    membership_status=none_member,
    id=SKIP_TEST_CADET_ID,
)

test_cadet_id = test_cadet.id


def sort_a_list_of_cadets(
    master_list: ListOfCadets, sort_by: str = arg_not_passed,
        similar_cadet: Cadet = arg_not_passed,
) -> ListOfCadets:
    if sort_by is arg_not_passed:
        return master_list
    if sort_by == SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    elif sort_by == SORT_BY_DOB_ASC:
        return master_list.sort_by_dob_asc()
    elif sort_by == SORT_BY_DOB_DSC:
        return master_list.sort_by_dob_desc()
    elif sort_by == SORT_BY_SIMILARITY_NAME:
        return master_list.sort_by_similarity_name_against_cadet(cadet=similar_cadet)
    elif sort_by == SORT_BY_SIMILARITY_DOB:
        return master_list.sort_by_similarity_dob_against_cadet(cadet=similar_cadet)
    else:
        raise Exception("Sort order %s not known" % sort_by)



SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
SORT_BY_DOB_ASC = "Sort by date of birth, oldest 1st"
SORT_BY_DOB_DSC = "Sort by date of birth, youngest 1st"
SORT_BY_SIMILARITY_DOB = "Sort by similarity of DOB"
SORT_BY_SIMILARITY_NAME = "Sort by similarity of name"