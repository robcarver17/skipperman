from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.objects.utilities.exceptions import arg_not_passed

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.committee import (
    CadetWithIdCommitteeMember,

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

