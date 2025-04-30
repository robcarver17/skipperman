from dataclasses import dataclass
from typing import List

from app.objects.utilities.exceptions import missing_data
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_idx_of_multiple_object_with_multiple_attr_in_list, get_unique_object_with_multiple_attr_in_list,
    get_idx_of_unique_object_with_multiple_attr_in_list,
)

from app.objects.utilities.generic_objects import GenericSkipperManObject

PERMANENT_SKIP_VOLUNTEER_ID = "NO_volunteer_allocated"  ## DO not change
SKIP_FOR_NOW_VOLUNTEER_ID = "SKip_for_now" ## do not change

@dataclass
class RowIDAndIndex:
    row_id: str
    volunteer_index: int


@dataclass
class IdentifiedVolunteerAtEvent(GenericSkipperManObject):
    row_id: str
    volunteer_index: int
    volunteer_id: str

    @property
    def not_skipped(self):
        return not self.skipped

    @property
    def skipped(self):
        return self.is_permanent_skip or self.is_temporary_skip

    @property
    def is_permanent_skip(self):
        return self.volunteer_id == PERMANENT_SKIP_VOLUNTEER_ID

    @property
    def is_temporary_skip(self):
        return self.volunteer_id == SKIP_FOR_NOW_VOLUNTEER_ID

    @classmethod
    def permanently_skipped(cls, row_id: str, volunteer_index: int):
        return cls(
            row_id=row_id,
            volunteer_index=volunteer_index,
            volunteer_id=PERMANENT_SKIP_VOLUNTEER_ID,
        )

    @classmethod
    def temporarily_skipped(cls, row_id: str, volunteer_index: int):
        return cls(
            row_id=row_id,
            volunteer_index=volunteer_index,
            volunteer_id=SKIP_FOR_NOW_VOLUNTEER_ID
        )

    @property
    def row_and_index(self):
        return RowIDAndIndex(row_id=self.row_id, volunteer_index=self.volunteer_index)



class ListOfIdentifiedVolunteersAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return IdentifiedVolunteerAtEvent

    def count_of_identified_row_and_index_including_skipped(self):
        return len(self)

    def count_of_permanent_skip_row_and_index(self):
        return len([item for item in self if item.is_permanent_skip])

    def count_of_temporary_skip_row_and_index(self):
        return len([item for item in self if item.is_temporary_skip])

    def count_of_row_and_index_identified_as_volunteer(self):
        return len([item for item in self if item.not_skipped])

    def number_of_unique_volunteers_identified(self):
        return len(self.unique_list_of_allocated_volunteer_ids())

    def list_of_identified_volunteers_with_volunteer_id_excluding_skipped(
        self, volunteer_id: str
    ) -> "ListOfIdentifiedVolunteersAtEvent":
        items = [
            item
            for item in self
            if item.volunteer_id == volunteer_id
            if item.not_skipped
        ]
        return ListOfIdentifiedVolunteersAtEvent(items)

    def add_permanently_skipped_volunteer(self, row_id: str, volunteer_index: int):
        if self.is_temporary_skip(volunteer_index=volunteer_index, row_id=row_id):
            return self.replace_temporary_skip(row_id=row_id, volunteer_index=volunteer_index, volunteer_id=PERMANENT_SKIP_VOLUNTEER_ID)

        try:
            assert self.row_and_index_not_in_list_of_rows_and_indices(
                row_id=row_id, volunteer_index=volunteer_index
            )
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.add_identified_volunteer_without_checking(
            row_id=row_id,
            volunteer_index=volunteer_index,
            volunteer_id=PERMANENT_SKIP_VOLUNTEER_ID
        )

    def add_temporarily_skipped_volunteer(self, row_id: str, volunteer_index: int):
        if self.is_temporary_skip(volunteer_index=volunteer_index, row_id=row_id):
            return

        try:
            assert self.row_and_index_not_in_list_of_rows_and_indices(
                row_id=row_id, volunteer_index=volunteer_index
            )
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.add_identified_volunteer_without_checking(
            row_id=row_id,
            volunteer_index=volunteer_index,
            volunteer_id=SKIP_FOR_NOW_VOLUNTEER_ID
        )


    def add_identified_volunteer(
        self, row_id: str, volunteer_id: str, volunteer_index: int
    ):
        if self.is_temporary_skip(volunteer_index=volunteer_index, row_id=row_id):
            return self.replace_temporary_skip(row_id=row_id, volunteer_index=volunteer_index, volunteer_id=volunteer_id)

        try:
            assert self.row_and_index_not_in_list_of_rows_and_indices(
                row_id=row_id, volunteer_index=volunteer_index
            )
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.add_identified_volunteer_without_checking(
            row_id=row_id, volunteer_index=volunteer_index, volunteer_id=volunteer_id
        )

    def add_identified_volunteer_without_checking(self, row_id: str, volunteer_id: str, volunteer_index: int
    ):
        self.append(
            IdentifiedVolunteerAtEvent(
                row_id=row_id,
                volunteer_index=volunteer_index,
                volunteer_id=volunteer_id,
            )
        )


    def is_temporary_skip(self, row_id: str, volunteer_index: int):
        item = get_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes=dict(row_id=row_id, volunteer_index=volunteer_index),
            default=missing_data
        )
        if item is missing_data:
            return False

        return item.is_temporary_skip

    def replace_temporary_skip(self,row_id: str, volunteer_index: int, volunteer_id:str):
        self.delete_specific_item(row_id=row_id, volunteer_index=volunteer_index)
        self.add_identified_volunteer_without_checking(
            row_id=row_id, volunteer_index=volunteer_index, volunteer_id=volunteer_id
        )

    def delete_specific_item(self,row_id: str, volunteer_index: int):
        idx = get_idx_of_unique_object_with_multiple_attr_in_list( some_list=self,
            dict_of_attributes=dict(row_id=row_id, volunteer_index=volunteer_index)
        )
        self.pop(idx)

    def delete_all_rows_with_volunteer_id(self, volunteer_id: str):
        while True:
            idx_list = get_idx_of_multiple_object_with_multiple_attr_in_list(self,
                                                                             dict_of_attributes={
                                                                                 'volunteer_id':volunteer_id
                                                                             })
            if len(idx_list)==0:
                break

            self.pop(idx_list[0])

    def row_and_index_not_in_list_of_rows_and_indices(
        self, row_id: str, volunteer_index: int
    ) -> bool:
        return not self.row_and_index_in_list_of_rows_and_indices(
            row_id=row_id, volunteer_index=volunteer_index
        )

    def row_and_index_in_list_of_rows_and_indices(
        self, row_id: str, volunteer_index: int
    ) -> bool:
        row_and_index = RowIDAndIndex(row_id=row_id, volunteer_index=volunteer_index)
        return row_and_index in self.list_of_row_ids_and_indices()

    def row_and_index_in_list_and_identified_or_permanent_skip_but_not_temporarily_skipped(self, row_id: str, volunteer_index: int):
        idx = get_idx_of_unique_object_with_multiple_attr_in_list( some_list=self,
            dict_of_attributes=dict(row_id=row_id, volunteer_index=volunteer_index),
                                                                   default=missing_data
        )
        if idx is missing_data:
            return False

        item = self[idx]
        if item.is_temporary_skip:
            return False

        return True


    def unique_list_of_allocated_volunteer_ids(self):
        volunteer_ids = self.list_of_volunteer_ids_excluding_skipped()
        return list(set(volunteer_ids))

    def list_of_row_and_index_temporary_skip(self) -> List[RowIDAndIndex]:
        return [item.row_and_index for item in self if item.is_temporary_skip]

    def list_of_volunteer_ids_excluding_skipped(self):
        volunteer_ids = [item.volunteer_id for item in self if item.not_skipped]
        return volunteer_ids

    def list_of_row_ids_and_indices(self) -> List[RowIDAndIndex]:
        return [item.row_and_index for item in self]
