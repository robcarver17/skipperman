from dataclasses import dataclass
import datetime

from app.data_access.configuration.configuration import (
    MIN_AGE_WHEN_CADET_CAN_BE_AT_EVENT_WITHOUT_PARENT,
    MIN_CADET_AGE,
    MAX_CADET_AGE,
)
from app.data_access.configuration.fixed import MONTH_WHEN_CADET_AGE_BRACKET_BEGINS
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds
from app.objects.membership_status import (
    MembershipStatus,
    none_member,
    current_member,
    lapsed_member,
    system_unconfirmed_member,
    describe_status,
    user_unconfirmed_member,
)
from app.objects.utilities.utils import (
    transform_date_into_str,
    transform_str_or_datetime_into_date,
    in_x_not_in_y,
)
from app.objects.utilities.exceptions import (
    arg_not_passed,
    DAYS_IN_YEAR,
    MissingData,
    MultipleMatches,
)

DOB_SURE = "Known"
DOB_UNKNOWN = "I need to confirm - leave blank for now"
DOB_IRRELEVANT = "Non member - don't need to know"


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
        dob_status: str = DOB_SURE,
        id: str = arg_not_passed,
    ):
        return cls(
            first_name=first_name.strip(" ").title(),
            surname=surname.strip(" ").title(),
            date_of_birth=dob_from_passed_dob(
                date_of_birth=date_of_birth, dob_status=dob_status
            ),
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
        if self.has_default_date_of_birth:
            return ""  ## for old data
        elif self.has_unknown_date_of_birth:
            return "(DOB unconfirmed)"
        elif self.has_irrelevant_date_of_birth:
            return ""  ## typically used for non members
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

    def day_and_month_of_birth_matches_other_data(self, other_date: datetime.date):
        return (
            self.date_of_birth.day == other_date.day
            and self.date_of_birth.month == other_date.month
        )

    @property
    def has_default_date_of_birth(self):
        return self.date_of_birth == DEFAULT_DATE_OF_BIRTH

    @property
    def has_unknown_date_of_birth(self):
        return self.date_of_birth == UNCONFIRMED_DATE_OF_BIRTH

    @property
    def has_irrelevant_date_of_birth(self):
        return self.date_of_birth == IRRELEVANT_DATE_OF_BIRTH


def dob_from_passed_dob(date_of_birth: datetime.date, dob_status: str):
    if dob_status == DOB_SURE:
        use_date_of_birth = transform_str_or_datetime_into_date(date_of_birth)
    elif dob_status == DOB_IRRELEVANT:
        use_date_of_birth = IRRELEVANT_DATE_OF_BIRTH
    elif dob_status == DOB_UNKNOWN:
        use_date_of_birth = UNCONFIRMED_DATE_OF_BIRTH
    else:
        raise Exception("DOB status %s unknown" % dob_status)

    return use_date_of_birth


class ListOfCadets(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Cadet

    def pop_cadet(self, cadet: Cadet):
        cadet_idx = self.index_of_id(cadet.id)
        return self.pop(cadet_idx)

    def current_members_only(self):
        return ListOfCadets(
            [cadet for cadet in self if cadet.membership_status == current_member]
        )

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

    def cadet_with_id(self, cadet_id: str, default=arg_not_passed) -> Cadet:
        if cadet_id == permanent_skip_cadet_id:
            return permanent_skip_cadet
        elif cadet_id == temporary_skip_cadet_id:
            return temporary_skip_cadet

        return self.object_with_id(cadet_id, default=default)


def cadet_is_too_young_to_be_without_parent(cadet: Cadet) -> bool:
    return cadet.approx_age_years() < MIN_AGE_WHEN_CADET_CAN_BE_AT_EVENT_WITHOUT_PARENT


def is_cadet_age_surprising(cadet: Cadet):
    too_old = cadet_seems_too_old(cadet)
    too_young = cadet_seems_too_young(cadet)

    return too_old or too_young


def cant_check_dob(cadet: Cadet):
    return (
        cadet.has_default_date_of_birth
        or cadet.has_unknown_date_of_birth
        or cadet.has_irrelevant_date_of_birth
    )


def cadet_seems_too_old(cadet: Cadet):
    if cant_check_dob(cadet):
        return False

    date_of_birth = cadet.date_of_birth
    appropriate_year = get_appropriate_year_for_cadet_start_point()
    cut_off_date = datetime.date(
        year=appropriate_year - MAX_CADET_AGE - 1,
        month=MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
        day=1,
    )

    return date_of_birth < cut_off_date


def cadet_seems_too_young(cadet: Cadet):
    if cant_check_dob(cadet):
        return False

    date_of_birth = cadet.date_of_birth
    appropriate_year = get_appropriate_year_for_cadet_start_point()
    cut_off_date = datetime.date(
        year=appropriate_year - MIN_CADET_AGE - 1,
        month=MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
        day=1,
    )

    return date_of_birth >= cut_off_date


def how_old(date_of_birth: datetime.date):
    diff = datetime.date.today() - date_of_birth
    return diff.total_seconds() / (60 * 60 * 24 * 365.25)


def get_appropriate_year_for_cadet_start_point():
    today = datetime.date.today()
    if today.month < MONTH_WHEN_CADET_AGE_BRACKET_BEGINS:
        return today.year
    else:
        return today.year + 1


PERMANENT_SKIP_TEST_CADET_ID = str(-9999)
TEMPORARY_SKIP_TEST_CADET_ID = str(9991)

DEFAULT_DATE_OF_BIRTH = datetime.date(1970, 1, 1)
UNCONFIRMED_DATE_OF_BIRTH = datetime.date(1950, 1, 1)
IRRELEVANT_DATE_OF_BIRTH = datetime.date(1960, 1, 1)

default_cadet = Cadet.new(
    first_name=" ",
    surname=" ",
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    membership_status=user_unconfirmed_member,
    dob_status=DOB_UNKNOWN,
)


permanent_skip_cadet = Cadet(
    "Test",
    "",
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    membership_status=none_member,
    id=PERMANENT_SKIP_TEST_CADET_ID,
)

permanent_skip_cadet_id = permanent_skip_cadet.id

temporary_skip_cadet = Cadet(
    "Temp skip",
    "",
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    membership_status=none_member,
    id=TEMPORARY_SKIP_TEST_CADET_ID,
)

temporary_skip_cadet_id = temporary_skip_cadet.id
