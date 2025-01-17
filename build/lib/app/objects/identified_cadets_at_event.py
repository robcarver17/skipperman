from dataclasses import dataclass
from typing import List

from app.objects.cadets import Cadet, SKIP_TEST_CADET_ID

from app.objects.exceptions import missing_data, MissingData
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.exceptions import MultipleMatches


@dataclass
class IdentifiedCadetAtEvent(GenericSkipperManObject):
    row_id: str
    cadet_id: str

    @property
    def is_test_cadet(self):
        return self.cadet_id == SKIP_TEST_CADET_ID

    @classmethod
    def create_row_for_test_cadet(cls, row_id: str):
        return cls(cadet_id=SKIP_TEST_CADET_ID, row_id=row_id)


class ListOfIdentifiedCadetsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return IdentifiedCadetAtEvent

    def __add__(self, other: IdentifiedCadetAtEvent):
        self.add(row_id=other.row_id, cadet_id=other.cadet_id)

    def row_has_identified_cadet_including_test_cadets(self, row_id: str):
        return row_id in self.list_of_row_ids_including_test_cadets()

    def list_of_row_ids_including_test_cadets(self):
        return [item.row_id for item in self]

    def add_cadet_and_row_association(self, cadet: Cadet, row_id: str):
        self.add(cadet_id=cadet.id, row_id=row_id)

    def add(self, row_id: str, cadet_id: str):
        try:
            assert row_id not in self.list_of_row_ids_including_test_cadets()
        except:
            raise Exception("Row ID can't appear more than once")

        self.append(IdentifiedCadetAtEvent(row_id=row_id, cadet_id=cadet_id))

    def add_row_with_test_cadet_as_skipping(self, row_id: str):
        try:
            assert row_id not in self.list_of_row_ids_including_test_cadets()
        except:
            raise Exception("Row ID can't appear more than once")

        self.append(IdentifiedCadetAtEvent.create_row_for_test_cadet(row_id=row_id))

    def cadet_id_given_row_id(self, row_id: str) -> str:
        matching = [item for item in self if item.row_id == row_id]
        if len(matching) == 0:
            raise MissingData
        elif len(matching) > 1:
            raise MultipleMatches("Can't have same row_id more than once")

        matching_item = matching[0]
        cadet_id = str(matching_item.cadet_id)

        if cadet_id == SKIP_TEST_CADET_ID:
            raise MissingData

        return cadet_id

    def list_of_row_ids_given_cadet_id_allowing_duplicates(
        self, cadet_id: str
    ) -> List[str]:
        matching = [item.row_id for item in self if item.cadet_id == cadet_id]

        return matching
