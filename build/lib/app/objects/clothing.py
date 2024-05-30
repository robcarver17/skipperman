from dataclasses import dataclass

from app.objects.generic import GenericSkipperManObject, GenericListOfObjects
UNALLOCATED_COLOUR = ""

@dataclass
class CadetWithClothingAtEvent(GenericSkipperManObject):
    cadet_id:str
    size: str
    colour: str = UNALLOCATED_COLOUR


class ListOfCadetsWithClothingAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetWithClothingAtEvent

    def add_new_cadet_with_clothing_size_and_optionally_colour(self, cadet_id: str, size: str, colour: str = UNALLOCATED_COLOUR):
        assert cadet_id not in self.list_of_cadet_ids()
        self.append(CadetWithClothingAtEvent(cadet_id=cadet_id,
                                             size=size,
                                             colour=colour))

    def list_of_cadet_ids(self):
        return [object.cadet_id for object in self]

    def change_colour_group_for_cadet(self, cadet_id: str, colour: str):
        object = self.object_with_cadet_id(cadet_id)
        object.colour = colour

    def change_clothing_size_for_cadet(self, cadet_id: str, size: str):
        object = self.object_with_cadet_id(cadet_id)
        object.size=size

    def object_with_cadet_id(self, cadet_id) -> CadetWithClothingAtEvent:
        list_of_ids = self.list_of_cadet_ids()
        idx = list_of_ids.index(cadet_id)

        return self[idx]