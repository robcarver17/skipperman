from dataclasses import dataclass

from app.objects.day_selectors import Day

from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,

)
from app.objects.utilities.generic_objects import (
    GenericSkipperManObject,
    get_class_instance_from_str_dict,
)
from app.objects.partners import (
    NO_PARTNER_REQUIRED_STR,
    NOT_ALLOCATED_STR,
)
from app.objects.utilities.transform_data import make_id_as_int_str
from app.objects.boat_classes import NO_BOAT_CLASS_ID


@dataclass
class CadetAtEventWithBoatClassAndPartnerWithIds(GenericSkipperManObject):
    cadet_id: str
    day: Day
    sail_number: str = ""
    partner_cadet_id: str = NO_PARTNER_REQUIRED_STR
    boat_class_id: str = NO_BOAT_CLASS_ID

    def __eq__(self, other):
        sail_number = make_id_as_int_str(self.sail_number)
        other_sail_number = make_id_as_int_str(other.sail_number)

        return (
            self.cadet_id == other.cadet_id
            and self.boat_class_id == other.boat_class_id
            and sail_number == other_sail_number
            and self.partner_cadet_id == other.partner_cadet_id
        )

    def clear_partner(self):
        self.partner_cadet_id = NOT_ALLOCATED_STR

    @classmethod
    def from_dict_of_str(cls, dict_with_str):
        class_instance = get_class_instance_from_str_dict(cls, dict_with_str)
        class_instance.sail_number = make_id_as_int_str(class_instance.sail_number)

        return class_instance


class ListOfCadetAtEventWithBoatClassAndPartnerWithIds(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetAtEventWithBoatClassAndPartnerWithIds

