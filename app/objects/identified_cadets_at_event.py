from dataclasses import dataclass
from typing import List

from app.objects.cadets import Cadet, test_cadet_id

from app.objects.exceptions import MissingData
from app.objects.generic_list_of_objects import (
    GenericListOfObjects,
    get_idx_of_unique_object_with_attr_in_list,
    index_not_found, get_idx_of_multiple_object_with_multiple_attr_in_list,
)
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.exceptions import MultipleMatches
from app.objects.exceptions import arg_not_passed


@dataclass
class IdentifiedCadetAtEvent(GenericSkipperManObject):
    row_id: str
    cadet_id: str

    @property
    def is_test_cadet(self):
        return self.cadet_id == test_cadet_id

    @classmethod
    def create_row_for_test_cadet(cls, row_id: str):
        return cls(cadet_id=test_cadet_id, row_id=row_id)


class ListOfIdentifiedCadetsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return IdentifiedCadetAtEvent

    def delete_cadet_from_identified_data(self, cadet_id:str):
        while True:
            list_of_idx =get_idx_of_multiple_object_with_multiple_attr_in_list(self, dict_of_attributes={'cadet_id': cadet_id})
            if len(list_of_idx)==0:
                break
            self.pop(list_of_idx[0])

    def row_does_not_have_identified_cadet_including_test_cadets(self, row_id: str):
        return not self.row_has_identified_cadet_including_test_cadets(row_id)

    def row_has_identified_cadet_including_test_cadets(self, row_id: str):
        return row_id in self.list_of_row_ids_including_test_cadets()

    def list_of_row_ids_including_test_cadets(self):
        return [item.row_id for item in self]

    def add_cadet_and_row_association(self, cadet: Cadet, row_id: str):
        try:
            assert self.row_does_not_have_identified_cadet_including_test_cadets(row_id)
        except:
            raise Exception(
                "Row ID %s is already mapped to an identified cadet" % row_id
            )

        self.append(IdentifiedCadetAtEvent(row_id=row_id, cadet_id=cadet.id))

    def add_row_with_test_cadet(self, row_id: str):
        try:
            assert self.row_does_not_have_identified_cadet_including_test_cadets(row_id)
        except:
            raise Exception("Row ID can't appear more than once")

        self.append(IdentifiedCadetAtEvent.create_row_for_test_cadet(row_id=row_id))

    def cadet_id_given_row_id_ignoring_test_cadets(
        self, row_id: str, default_when_missing=arg_not_passed
    ) -> str:
        matching_idx = get_idx_of_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="row_id",
            attr_value=row_id,
            default=index_not_found,
        )

        if matching_idx is index_not_found:
            if default_when_missing is arg_not_passed:
                raise MissingData("No matching rows found for %s" % row_id)
            else:
                return default_when_missing

        matching_item = self[matching_idx]
        cadet_id = str(matching_item.cadet_id)

        if cadet_id == test_cadet_id:
            if default_when_missing is arg_not_passed:
                raise MissingData
            else:
                return default_when_missing

        return cadet_id

    def list_of_row_ids_given_cadet_id_allowing_duplicates(
        self, cadet_id: str
    ) -> List[str]:
        matching = [item.row_id for item in self if item.cadet_id == cadet_id]

        return matching
