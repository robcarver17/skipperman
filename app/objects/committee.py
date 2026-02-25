from dataclasses import dataclass
import datetime
from typing import Tuple

from app.data_access.configuration.fixed import MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS, YEARS_ON_CADET_COMMITTEE, \
    MAX_AGE_TO_JOIN_COMMITTEE, MONTH_WHEN_CADET_AGE_BRACKET_BEGINS, MIN_AGE_TO_JOIN_COMMITTEE, MONTH_WHEN_EGM_HAPPENS
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,

)
from app.objects.utilities.generic_objects import GenericSkipperManObject


@dataclass
class CadetWithIdCommitteeMember(GenericSkipperManObject):
    cadet_id: str
    date_term_starts: datetime.date
    date_term_ends: datetime.date
    deselected: bool = False

    def status_string(self):
        after_election = self.after_election()
        before_end_of_term = self.before_end_of_term()
        deselected = self.deselected

        ## These strings form a neat sort order
        if not after_election:
            return "Elected but not yet serving on committee"
        elif not before_end_of_term:
            return "Past committee member"
        elif deselected:
            return "Deselected"
        else:
            return "Current committee member"

    def currently_serving(self) -> bool:
        return self.after_election() and self.before_end_of_term()

    def after_election(self) -> bool:
        return datetime.date.today() >= self.date_term_starts

    def before_end_of_term(self) -> bool:
        return datetime.date.today() <= self.date_term_ends


class ListOfCadetsWithIdOnCommittee(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetWithIdCommitteeMember


def start_and_end_date_on_cadet_commmittee() -> Tuple[datetime.date, datetime.date]:
    start_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee_after_EGM(),
    )
    end_date_on_committee = datetime.date(
        day=1,
        month=MONTH_WHEN_NEW_COMMITTEE_YEAR_BEGINS,
        year=get_next_year_for_cadet_committee_after_EGM() + YEARS_ON_CADET_COMMITTEE,
    )

    return start_date_on_committee, end_date_on_committee


def earliest_and_latest_date_to_join_committee(next_year_for_committee: int):
    earliest_date = datetime.date(
        next_year_for_committee - MAX_AGE_TO_JOIN_COMMITTEE,
        MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
        1,
    )
    latest_date = datetime.date(
        next_year_for_committee - MIN_AGE_TO_JOIN_COMMITTEE,
        MONTH_WHEN_CADET_AGE_BRACKET_BEGINS,
        1,
    )

    return earliest_date, latest_date


def get_next_year_for_cadet_committee_after_EGM():
    today = datetime.date.today()
    if today.month < MONTH_WHEN_EGM_HAPPENS:
        return today.year
    else:
        return today.year + 1


def month_name_when_cadet_committee_age_bracket_begins():
    ARBITRARY_YEAR = 1990
    return datetime.date(
        ARBITRARY_YEAR, MONTH_WHEN_CADET_AGE_BRACKET_BEGINS, 1
    ).strftime("%B")
