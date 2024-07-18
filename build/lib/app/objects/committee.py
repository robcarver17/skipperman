from dataclasses import dataclass
import datetime
from typing import List

from app.objects.cadets import Cadet
from app.objects.exceptions import missing_data, MissingData

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject


@dataclass
class CadetWithIdCommitteeMember(GenericSkipperManObject):
    cadet_id: str
    date_term_starts: datetime.date
    date_term_ends: datetime.date
    deselected: bool = False

    def currently_active(self):
        after_election = datetime.date.today() >= self.date_term_starts
        before_end_of_term = datetime.date.today() <= self.date_term_ends
        not_deselected = not self.deselected

        return after_election and before_end_of_term and not_deselected

    def status_string(self):
        after_election = datetime.date.today() >= self.date_term_starts
        before_end_of_term = datetime.date.today() <= self.date_term_ends
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


class ListOfCadetsWithIdOnCommittee(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetWithIdCommitteeMember

    def currently_active(self):
        return ListOfCadetsWithIdOnCommittee(
            [cadet for cadet in self if cadet.currently_active()]
        )

    def list_of_cadet_ids(self):
        return [cadet.cadet_id for cadet in self]

    def add_new_members(
        self,
        cadet_id: str,
        date_term_starts: datetime.date,
        date_term_ends: datetime.date,
    ):
        assert cadet_id not in self.list_of_cadet_ids()

        self.append(
            CadetWithIdCommitteeMember(
                cadet_id=cadet_id,
                date_term_starts=date_term_starts,
                date_term_ends=date_term_ends,
                deselected=False,
            )
        )

    def deselect_member(self, cadet_id: str):
        committee_member = self.cadet_committee_member_with_id(cadet_id)
        committee_member.deselected = True

    def reselect_member(self, cadet_id: str):
        committee_member = self.cadet_committee_member_with_id(cadet_id)
        committee_member.deselected = False

    def cadet_committee_member_with_id(self, cadet_id) -> CadetWithIdCommitteeMember:
        list_of_ids = self.list_of_cadet_ids()
        try:
            idx = list_of_ids.index(cadet_id)
        except ValueError:
            raise MissingData

        return self[idx]


@dataclass
class CadetOnCommittee:
    cadet_on_committee: CadetWithIdCommitteeMember
    cadet: Cadet

    def __lt__(self, other):
        if (
            self.cadet_on_committee.status_string()
            < other.cadet_on_committee.status_string()
        ):
            return True
        elif (
            self.cadet_on_committee.status_string()
            > other.cadet_on_committee.status_string()
        ):
            return False

        return self.cadet.name < other.cadet.name

    @property
    def cadet_id(self):
        return self.cadet.id

    @property
    def deselected(self):
        return self.cadet_on_committee.deselected


class ListOfCadetsOnCommittee(List[CadetOnCommittee]):
    pass
