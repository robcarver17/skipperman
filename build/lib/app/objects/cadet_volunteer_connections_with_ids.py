from dataclasses import dataclass

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject


@dataclass
class CadetVolunteerAssociationWithIds(GenericSkipperManObject):
    cadet_id: str
    volunteer_id: str


class ListOfCadetVolunteerAssociationsWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetVolunteerAssociationWithIds

    def list_of_volunteer_ids_associated_with_cadet_id(self, cadet_id: str):
        return [
            element.volunteer_id for element in self if element.cadet_id == cadet_id
        ]

    def list_of_connections_for_volunteer(self, volunteer_id: str):
        return [
            element.cadet_id for element in self if element.volunteer_id == volunteer_id
        ]

    def delete(self, cadet_id: str, volunteer_id: str):
        matching_elements_list = [
            element
            for element in self
            if element.volunteer_id == volunteer_id and element.cadet_id == cadet_id
        ]
        if len(matching_elements_list) == 0:
            return
        matching_element = matching_elements_list[
            0
        ]  ## corner case of duplicates shouldn't happen just in case
        self.remove(matching_element)

    def add(self, cadet_id: str, volunteer_id: str):
        if self.connection_exists(cadet_id=cadet_id, volunteer_id=volunteer_id):
            return
        self.append(
            CadetVolunteerAssociationWithIds(cadet_id=cadet_id, volunteer_id=volunteer_id)
        )

    def connection_exists(self, cadet_id: str, volunteer_id: str):
        exists = [
            True
            for element in self
            if element.volunteer_id == volunteer_id and element.cadet_id == cadet_id
        ]
        return any(exists)
