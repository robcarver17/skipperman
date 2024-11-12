from dataclasses import dataclass
import datetime

from app.objects.exceptions import MissingData

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject


@dataclass
class CadetWithIdCommitteeMember(GenericSkipperManObject):
    cadet_id: str
    date_term_starts: datetime.date
    date_term_ends: datetime.date
    deselected: bool = False

    def toggle_selection(self):
        self.deselected = not self.deselected

    def currently_active(self):
        currently_serving = self.currently_serving()
        not_deselected = not self.deselected

        return currently_serving and not_deselected

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

    ## FIXME LEGACY METHODS CAN REMOVE ONCE CLOTHING DONE LOGIC NOW IN COMPOSED
    def currently_active(self):
        return ListOfCadetsWithIdOnCommittee(
            [cadet for cadet in self if cadet.currently_active()]
        )

    def list_of_cadet_ids(self):
        return [cadet.cadet_id for cadet in self]
