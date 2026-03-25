from dataclasses import dataclass

from app.objects.day_selectors import Day

from app.objects.utilities.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds


@dataclass
class CadetIdWithGroup(GenericSkipperManObjectWithIds):
    cadet_id: str
    group_id: str
    day: Day


class ListOfCadetIdsWithGroups(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetIdWithGroup

    @property
    def list_of_cadet_ids(self) -> list:
        return [item.cadet_id for item in self]
