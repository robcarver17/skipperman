from dataclasses import dataclass

from app.objects.utilities.exceptions import missing_data
from app.objects.utilities.generic_list_of_objects import GenericListOfObjects
from app.objects.utilities.generic_objects import GenericSkipperManObject


@dataclass
class CadetVolunteerAssociationWithIds(GenericSkipperManObject):
    cadet_id: str
    volunteer_id: str


class ListOfCadetVolunteerAssociationsWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetVolunteerAssociationWithIds

