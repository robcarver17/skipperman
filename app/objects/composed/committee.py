from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.objects.utilities.exceptions import MissingData, arg_not_passed

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.committee import (
    CadetWithIdCommitteeMember,
    ListOfCadetsWithIdOnCommittee,
)
from app.objects.utilities.generic_list_of_objects import (
    get_unique_object_with_attr_in_list,
)


@dataclass
class CadetOnCommittee:
    cadet_with_id_on_committee: CadetWithIdCommitteeMember
    cadet: Cadet

    def __lt__(self, other):
        if (
            self.cadet_with_id_on_committee.status_string()
            < other.cadet_with_id_on_committee.status_string()
        ):
            return True
        elif (
            self.cadet_with_id_on_committee.status_string()
            > other.cadet_with_id_on_committee.status_string()
        ):
            return False

        return self.cadet.name < other.cadet.name

    def toggle_selection(self):
        self.cadet_with_id_on_committee.toggle_selection()

    @classmethod
    def new(
        cls,
        cadet: Cadet,
        date_term_starts: datetime.date,
        date_term_ends: datetime.date,
    ):
        cadet_with_id_on_committee = CadetWithIdCommitteeMember(
            cadet_id=cadet.id,
            date_term_ends=date_term_ends,
            date_term_starts=date_term_starts,
        )

        return cls(cadet=cadet, cadet_with_id_on_committee=cadet_with_id_on_committee)

    @property
    def cadet_id(self):
        return self.cadet.id

    @property
    def deselected(self):
        return self.cadet_with_id_on_committee.deselected

    def status_string(self) -> str:
        return self.cadet_with_id_on_committee.status_string()

    def currently_serving(self):
        return self.cadet_with_id_on_committee.currently_serving()

    @property
    def date_term_starts(self) -> datetime.date:
        return self.cadet_with_id_on_committee.date_term_starts

    @property
    def date_term_ends(self) -> datetime.date:
        return self.cadet_with_id_on_committee.date_term_ends


class ListOfCadetsOnCommittee(List[CadetOnCommittee]):
    def __init__(
        self,
        raw_list: List[CadetOnCommittee],
        list_of_cadets_with_id_on_commitee: ListOfCadetsWithIdOnCommittee,
    ):
        self._list_of_cadets_with_id_on_committee = list_of_cadets_with_id_on_commitee
        super().__init__(raw_list)

    def toggle_selection_for_cadet(self, cadet: Cadet):
        specific_member = self.get_cadet_on_committee(cadet)
        specific_member.toggle_selection()

    def get_cadet_on_committee(self, cadet: Cadet, default=arg_not_passed):
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="cadet_id", attr_value=cadet.id, default=default
        )

    def is_cadet_currently_on_committee(self, cadet: Cadet) -> bool:
        for cadet_on_committee in self:
            if (
                cadet_on_committee.cadet_id == cadet.id
                and cadet_on_committee.currently_serving()
            ):
                return True

        return False

    def is_cadet_elected_to_committee(self, cadet: Cadet) -> bool:
        for cadet_on_committee in self:
            if cadet_on_committee.cadet_id == cadet.id:
                return True

        return False

    def list_of_cadets_currently_serving(self) -> ListOfCadets:
        return ListOfCadets(
            [
                cadet_on_committee.cadet
                for cadet_on_committee in self
                if cadet_on_committee.currently_serving()
            ]
        )

    def delete_cadet_from_data(self, cadet: Cadet):
        for cadet_on_committee in self:
            if cadet_on_committee.cadet_id == cadet.id:
                self.remove(cadet_on_committee)
                break

        self.list_of_cadets_with_id_on_commitee.remove_cadet_with_id(cadet_id=cadet.id)

    def add_new_member(
        self,
        cadet: Cadet,
        date_term_starts: datetime.date,
        date_term_ends: datetime.date,
    ):
        try:
            assert not self.is_cadet_elected_to_committee(cadet)
        except:
            raise Exception("Cadet is already elected to committee")

        cadet_on_committee = CadetOnCommittee.new(
            cadet=cadet,
            date_term_starts=date_term_starts,
            date_term_ends=date_term_ends,
        )
        self.append(cadet_on_committee)

        ## Change underlying - no need to change list of cadets
        self.list_of_cadets_with_id_on_commitee.add(
            cadet_on_committee.cadet_with_id_on_committee
        )

    @property
    def list_of_cadets_with_id_on_commitee(self) -> ListOfCadetsWithIdOnCommittee:
        return self._list_of_cadets_with_id_on_committee

    @list_of_cadets_with_id_on_commitee.setter
    def list_of_cadets_with_id_on_commitee(
        self, list_of_cadets_with_id_on_committee: ListOfCadetsWithIdOnCommittee
    ):
        self._list_of_cadets_with_id_on_committee = list_of_cadets_with_id_on_committee


def create_list_of_cadet_committee_members_from_underlying_data(
    list_of_cadets: ListOfCadets,
    list_of_cadets_with_id_on_commitee: ListOfCadetsWithIdOnCommittee,
) -> ListOfCadetsOnCommittee:
    raw_list = create_raw_list_of_cadet_committee_members_from_underlying_data(
        list_of_cadets=list_of_cadets,
        list_of_cadets_with_id_on_commitee=list_of_cadets_with_id_on_commitee,
    )
    return ListOfCadetsOnCommittee(
        raw_list=raw_list,
        list_of_cadets_with_id_on_commitee=list_of_cadets_with_id_on_commitee,
    )


def create_raw_list_of_cadet_committee_members_from_underlying_data(
    list_of_cadets: ListOfCadets,
    list_of_cadets_with_id_on_commitee: ListOfCadetsWithIdOnCommittee,
) -> List[CadetOnCommittee]:
    list_of_members = []
    for cadet_with_id_on_committee in list_of_cadets_with_id_on_commitee:
        try:
            cadet = list_of_cadets.cadet_with_id(cadet_with_id_on_committee.cadet_id)
        except MissingData:
            continue  ## or throw error?

        list_of_members.append(
            CadetOnCommittee(
                cadet=cadet, cadet_with_id_on_committee=cadet_with_id_on_committee
            )
        )

    return list_of_members
