from dataclasses import dataclass
from typing import List

from app.objects.cadets import permanent_skip_cadet_id, temporary_skip_cadet_id

from app.objects.utilities.exceptions import MissingData, missing_data
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_idx_of_unique_object_with_attr_in_list,
    index_not_found,
    get_idx_of_multiple_object_with_multiple_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.utilities.exceptions import arg_not_passed


@dataclass
class IdentifiedCadetAtEvent(GenericSkipperManObject):
    row_id: str
    cadet_id: str

    @property
    def is_skippable(self):
        return self.is_temporary_skip_cadet or self.is_permanent_skip_cadet

    @property
    def is_permanent_skip_cadet(self):
        return self.cadet_id == permanent_skip_cadet_id

    @classmethod
    def create_row_for_permanent_skip_cadet(cls, row_id: str):
        return cls(cadet_id=permanent_skip_cadet_id, row_id=row_id)

    @property
    def is_temporary_skip_cadet(self):
        return self.cadet_id == temporary_skip_cadet_id

    @classmethod
    def create_row_for_temporary_skip_cadet(cls, row_id: str):
        return cls(cadet_id=temporary_skip_cadet_id, row_id=row_id)


class ListOfIdentifiedCadetsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return IdentifiedCadetAtEvent

    def count_of_identified_rows(self):
        return len(list(set([item.row_id for item in self])))

    def count_of_permanent_skip_rows(self):
        return len([item for item in self if item.is_permanent_skip_cadet])

    def count_of_temporary_skip_rows(self):
        return len([item for item in self if item.is_temporary_skip_cadet])

    def count_of_rows_identified_as_cadets(self):
        return len([item for item in self if not item.is_skippable])

    def count_of_cadets_in_rows(self):
        cadet_ids = [item.cadet_id for item in self if not item.is_skippable]
        unique_cadet_ids = set(cadet_ids)
        return len(unique_cadet_ids)

    def count_of_duplicate_rows(self):
        count_of_cadet_ids = self.count_of_cadets_in_rows()
        count_of_identified_row = self.count_of_rows_identified_as_cadets()
        return count_of_identified_row - count_of_cadet_ids

    def delete_cadet_from_identified_data(self, cadet_id: str):
        while True:
            list_of_idx = get_idx_of_multiple_object_with_multiple_attr_in_list(
                self, dict_of_attributes={"cadet_id": cadet_id}
            )
            if len(list_of_idx) == 0:
                break
            self.pop(list_of_idx[0])

    def delete_row_from_identified_data(self, row_id: str):
        item = self.item_given_row_id(row_id)
        self.remove(item)

    def row_does_not_have_identified_cadet_including_skip_cadets(self, row_id: str):
        in_rows = row_id in self.list_of_all_row_ids()
        return not in_rows

    def row_has_identified_cadet_including_permanently_skipped_cadets_but_not_temporary(
        self, row_id: str
    ):
        return (
            row_id
            in self.list_of_row_ids_including_permanent_skip_cadets_but_excluding_temporary()
        )

    def list_of_row_ids_including_permanent_skip_cadets_but_excluding_temporary(self):
        return [item.row_id for item in self if not item.is_temporary_skip_cadet]

    def list_of_all_row_ids(self):
        return [item.row_id for item in self]

    def add_cadet_and_row_association(self, cadet_id: str, row_id: str):
        if self.row_id_is_temporary_skip(row_id):
            return self.replace_temporary_row(cadet_id=cadet_id, row_id=row_id)

        try:
            assert self.row_does_not_have_identified_cadet_including_skip_cadets(row_id)
        except:
            ## will also raise if perma skip
            raise Exception(
                "Row ID %s is already mapped to an identified cadet" % row_id
            )

        self.add_cadet_and_row_association_without_checking(
            cadet_id=cadet_id, row_id=row_id
        )

    def add_cadet_and_row_association_without_checking(
        self, cadet_id: str, row_id: str
    ):
        self.append(IdentifiedCadetAtEvent(row_id=row_id, cadet_id=cadet_id))

    def add_row_with_permanent_skip_cadet(self, row_id: str):
        if self.row_id_is_temporary_skip(row_id):
            return self.replace_temporary_row(
                cadet_id=permanent_skip_cadet_id, row_id=row_id
            )

        try:
            assert self.row_does_not_have_identified_cadet_including_skip_cadets(row_id)
        except:
            ## will raise if temporary or permanent
            raise Exception("Row ID can't appear more than once")

        self.append(
            IdentifiedCadetAtEvent.create_row_for_permanent_skip_cadet(row_id=row_id)
        )

    def add_row_with_temporary_skip_cadet(self, row_id: str):
        if self.row_id_is_temporary_skip(row_id):
            return

        try:
            assert self.row_does_not_have_identified_cadet_including_skip_cadets(row_id)
        except:
            raise Exception("Row ID can't appear more than once")

        self.append(
            IdentifiedCadetAtEvent.create_row_for_temporary_skip_cadet(row_id=row_id)
        )

    def replace_temporary_row(self, row_id: str, cadet_id: str):
        self.delete_row_from_identified_data(row_id)
        self.add_cadet_and_row_association_without_checking(
            cadet_id=cadet_id, row_id=row_id
        )

    def row_id_is_temporary_skip(self, row_id: str):
        item = self.item_given_row_id(row_id, default_when_missing=missing_data)
        if item is missing_data:
            return False
        return item.is_temporary_skip_cadet

    def cadet_id_given_row_id_ignoring_all_skipped_cadets(
        self, row_id: str, default_when_missing=arg_not_passed
    ) -> str:
        matching_item = self.item_given_row_id(
            row_id, default_when_missing=default_when_missing
        )

        if matching_item is default_when_missing:
            return default_when_missing

        cadet_id = str(matching_item.cadet_id)

        if cadet_id == permanent_skip_cadet_id or cadet_id == temporary_skip_cadet_id:
            if default_when_missing is arg_not_passed:
                raise MissingData
            else:
                return default_when_missing

        return cadet_id

    def item_given_row_id(
        self, row_id: str, default_when_missing=arg_not_passed
    ) -> IdentifiedCadetAtEvent:
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

        return matching_item

    def list_of_row_ids_given_cadet_id_allowing_duplicates(
        self, cadet_id: str
    ) -> List[str]:
        matching = [item.row_id for item in self if item.cadet_id == cadet_id]

        return matching
