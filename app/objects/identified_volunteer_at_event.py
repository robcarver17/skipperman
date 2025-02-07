from dataclasses import dataclass
from typing import List

from app.objects.exceptions import arg_not_passed, MissingData
from app.objects.generic_list_of_objects import GenericListOfObjects

from app.objects.generic_objects import GenericSkipperManObject
from app.objects.exceptions import MultipleMatches

NO_VOLUNTEER_ALLOCATED_ID = "NO_volunteer_allocated" ## DO not change


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
    def is_allocated(self):
        return not self.is_not_allocated

    @property
    def is_not_allocated(self):
        return self.volunteer_id == NO_VOLUNTEER_ALLOCATED_ID

    @classmethod
    def identified_as_processed_not_allocated(cls, row_id: str, volunteer_index: int):
        return cls(
            row_id=row_id,
            volunteer_index=volunteer_index,
            volunteer_id=NO_VOLUNTEER_ALLOCATED_ID,
        )

    @property
    def row_and_index(self):
        return RowIDAndIndex(row_id=self.row_id, volunteer_index=self.volunteer_index)


class ListOfIdentifiedVolunteersAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return IdentifiedVolunteerAtEvent

    def list_of_identified_volunteers_with_volunteer_id(
        self, volunteer_id: str
    ) -> "ListOfIdentifiedVolunteersAtEvent":
        items = [
            item
            for item in self
            if item.volunteer_id == volunteer_id
            if item.is_allocated
        ]
        return ListOfIdentifiedVolunteersAtEvent(items)


    def identified_as_processed_not_allocated(self, row_id: str, volunteer_index: int):
        row_and_index = RowIDAndIndex(row_id=row_id, volunteer_index=volunteer_index)
        try:
            assert self.row_and_index_not_in_list_of_rows_and_indices(row_id=row_id, volunteer_index=volunteer_index)
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.append(
            IdentifiedVolunteerAtEvent.identified_as_processed_not_allocated(
                row_id=row_id, volunteer_index=volunteer_index
            )
        )

    def add_identified_volunteer(self, row_id: str, volunteer_id: str, volunteer_index: int):
        try:
            assert self.row_and_index_not_in_list_of_rows_and_indices(row_id=row_id, volunteer_index=volunteer_index)
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.append(
            IdentifiedVolunteerAtEvent(
                row_id=row_id,
                volunteer_index=volunteer_index,
                volunteer_id=volunteer_id,
            )
        )

    def row_and_index_not_in_list_of_rows_and_indices(self,  row_id: str, volunteer_index: int) -> bool:
        return not self.row_and_index_in_list_of_rows_and_indices(row_id=row_id, volunteer_index=volunteer_index)

    def row_and_index_in_list_of_rows_and_indices(self,  row_id: str, volunteer_index: int) -> bool:
        row_and_index = RowIDAndIndex(row_id=row_id, volunteer_index=volunteer_index)
        return row_and_index in self.list_of_row_ids_and_indices()

    def unique_list_of_allocated_volunteer_ids(self):
        volunteer_ids = self.list_of_volunteer_ids()
        return list(set(volunteer_ids))

    def list_of_volunteer_ids(self):
        volunteer_ids = [item.volunteer_id for item in self if item.is_allocated]
        return volunteer_ids

    def list_of_row_ids_and_indices(self) -> List[RowIDAndIndex]:
        return [item.row_and_index for item in self]
