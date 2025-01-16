from dataclasses import dataclass
from typing import List

from app.objects.exceptions import missing_data
from app.objects.generic_list_of_objects import GenericListOfObjects

from app.objects.generic_objects import GenericSkipperManObject
from app.objects.volunteers import NO_VOLUNTEER_ALLOCATED


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
        return self.volunteer_id == NO_VOLUNTEER_ALLOCATED

    @classmethod
    def identified_as_processed_not_allocated(cls, row_id: str, volunteer_index: int):
        return cls(
            row_id=row_id,
            volunteer_index=volunteer_index,
            volunteer_id=NO_VOLUNTEER_ALLOCATED,
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

    def unique_list_of_volunteer_ids(self):
        volunteer_ids = self.list_of_volunteer_ids()
        return list(set(volunteer_ids))

    def list_of_volunteer_ids(self):
        volunteer_ids = [item.volunteer_id for item in self if item.is_allocated]
        return volunteer_ids

    def list_of_volunteer_ids_including_unallocated(self):
        volunteer_ids = [item.volunteer_id for item in self]
        return volunteer_ids

    def list_of_row_ids_and_indices(self) -> List[RowIDAndIndex]:
        return [item.row_and_index for item in self]

    def identified_as_processed_not_allocated(self, row_id: str, volunteer_index: int):
        row_and_index = RowIDAndIndex(row_id=row_id, volunteer_index=volunteer_index)
        try:
            assert row_and_index not in self.list_of_row_ids_and_indices()
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.append(
            IdentifiedVolunteerAtEvent.identified_as_processed_not_allocated(
                row_id=row_id, volunteer_index=volunteer_index
            )
        )

    def add(self, row_id: str, volunteer_id: str, volunteer_index: int):
        row_and_index = RowIDAndIndex(row_id=row_id, volunteer_index=volunteer_index)
        try:
            assert row_and_index not in self.list_of_row_ids_and_indices()
        except:
            raise Exception("Row ID and index can't appear more than once")

        self.append(
            IdentifiedVolunteerAtEvent(
                row_id=row_id,
                volunteer_index=volunteer_index,
                volunteer_id=volunteer_id,
            )
        )

    def volunteer_id_given_row_id_and_index(
        self, row_id: str, volunteer_index: int
    ) -> str:
        matching = [
            item
            for item in self
            if item.row_id == row_id and item.volunteer_index == volunteer_index
        ]
        if len(matching) == 0:
            return missing_data
        elif len(matching) > 1:
            raise Exception("Can't have same row_id and volunteer index more than once")

        matching_item = matching[0]

        return matching_item.volunteer_id

    def list_of_volunteer_ids_given_list_of_row_ids_excluding_unallocated(
        self, list_of_row_ids: List[str]
    ) -> List[str]:
        list_of_volunteer_ids = []
        for row_id in list_of_row_ids:
            list_of_volunteer_ids += (
                self.list_of_volunteer_ids_given_row_id_excluding_unallocated(row_id)
            )

        return list_of_volunteer_ids

    def list_of_volunteer_ids_given_row_id_excluding_unallocated(
        self, row_id: str
    ) -> List[str]:
        matching = [
            item.volunteer_id
            for item in self
            if item.row_id == row_id and item.is_allocated
        ]

        return matching
