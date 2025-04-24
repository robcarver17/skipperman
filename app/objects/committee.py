from dataclasses import dataclass
import datetime

from app.objects.utilities.generic_list_of_objects import GenericListOfObjects, \
    get_idx_of_multiple_object_with_multiple_attr_in_list
from app.objects.utilities.generic_objects import GenericSkipperManObject


@dataclass
class CadetWithIdCommitteeMember(GenericSkipperManObject):
    cadet_id: str
    date_term_starts: datetime.date
    date_term_ends: datetime.date
    deselected: bool = False

    def toggle_selection(self):
        self.deselected = not self.deselected

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

    def add(self, cadet_with_id_on_committee: CadetWithIdCommitteeMember):
        try:
            assert cadet_with_id_on_committee.cadet_id not in self.list_of_cadet_ids()
        except:
            raise Exception("Can't add duplicate cadets to committee")

        self.append(cadet_with_id_on_committee)

    def list_of_cadet_ids(self):
        return [cadet_with_id.cadet_id for cadet_with_id in self]

    def remove_cadet_with_id(self, cadet_id:str):
        while True:
            list_of_idx =get_idx_of_multiple_object_with_multiple_attr_in_list(self, dict_of_attributes={'cadet_id': cadet_id})
            if len(list_of_idx)==0:
                break
            self.pop(list_of_idx[0])
