from app.objects.generic import GenericSkipperManObject, GenericListOfObjects
UNALLOCATED_COLOUR = ""

class CadetWithClothingAtEvent:
    cadet_id:str
    size: str
    colour: str = UNALLOCATED_COLOUR


class ListOfCadetsWithClothingAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return CadetWithClothingAtEvent


