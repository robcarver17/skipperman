from dataclasses import dataclass

from app.objects.utilities.exceptions import missing_data
from app.objects.utilities.generic_list_of_objects import GenericListOfObjects
from app.objects.utilities.generic_objects import GenericSkipperManObject


@dataclass
class CadetVolunteerAssociationWithIds(GenericSkipperManObject):
    cadet_id: str
    volunteer_id: str


from app.objects.utilities.generic_list_of_objects import (
    get_unique_object_with_multiple_attr_in_list,
)


class ListOfCadetVolunteerAssociationsWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetVolunteerAssociationWithIds

    def delete(self, cadet_id: str, volunteer_id: str):
        association = get_unique_object_with_multiple_attr_in_list(
            self,
            {"volunteer_id": volunteer_id, "cadet_id": cadet_id},
            default=missing_data,
        )
        if association is missing_data:
            raise Exception("Can't delete non existint association")
        self.remove(association)

    def add(self, cadet_id: str, volunteer_id: str):
        if self.connection_exists(cadet_id=cadet_id, volunteer_id=volunteer_id):
            return
        self.append(
            CadetVolunteerAssociationWithIds(
                cadet_id=cadet_id, volunteer_id=volunteer_id
            )
        )

    def connection_exists(self, cadet_id: str, volunteer_id: str):
        association = get_unique_object_with_multiple_attr_in_list(
            self,
            {"volunteer_id": volunteer_id, "cadet_id": cadet_id},
            default=missing_data,
        )

        return association is not missing_data
