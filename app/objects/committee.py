
from dataclasses import dataclass
from datetime import datetime

from app.objects.constants import missing_data

from app.objects.generic import GenericSkipperManObject, GenericListOfObjects


@dataclass
class CadetCommitteeMember(GenericSkipperManObject):
    cadet_id: str
    date_term_starts: datetime.date
    date_term_ends: datetime.date
    deselected: bool = False

    def currently_active(self):
        after_election = datetime.today()>=self.date_term_starts
        before_end_of_term = datetime.today()<=self.date_term_ends
        not_deselected = not self.deselected

        return after_election and before_end_of_term and not_deselected


class ListOfCadetsOnCommittee(GenericListOfObjects):
    def _object_class_contained(self):
        return CadetCommitteeMember

    def currently_active(self):
        return ListOfCadetsOnCommittee([cadet for cadet in self if cadet.currently_active()])

    def list_of_cadet_ids(self):
        return [cadet.cadet_id for cadet in self]

    def add_new_members(self, cadet_id: str, date_term_starts: datetime.date, date_term_ends: datetime.date):
        assert cadet_id not in self.list_of_cadet_ids()

        self.append(CadetCommitteeMember(cadet_id=cadet_id, date_term_starts=date_term_starts, date_term_ends=date_term_ends, deselected=False))

    def deselect_member(self, cadet_id:str):
        committee_member = self.cadet_committee_member_with_id(cadet_id)
        committee_member.deselected = True

    def reselect_member(self, cadet_id: str):
        committee_member = self.cadet_committee_member_with_id(cadet_id)
        committee_member.deselected = False

    def cadet_committee_member_with_id(self, cadet_id)-> CadetCommitteeMember:
        list_of_ids = self.list_of_cadet_ids()
        try:
            idx = list_of_ids.index(cadet_id)
        except ValueError:
            return missing_data

        return self[idx]
