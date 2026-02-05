from dataclasses import dataclass

from app.objects.cadets import Cadet
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_idx_of_unique_object_with_attr_in_list,
    get_unique_object_with_attr_in_list,
)

from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds
from app.objects.partners import (
    no_cadet_partner_required,
    valid_partnership_given_partner_cadet,
)

NO_BOAT_CLASS_NAME = ""


NO_BOAT_CLASS_ID = str(-9999)


@dataclass
class BoatClass(GenericSkipperManObjectWithIds):
    name: str
    hidden: bool
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.hidden == other.hidden

    def __hash__(self):
        return hash(self.name)

    @classmethod
    def create_empty(cls):
        return cls(NO_BOAT_CLASS_NAME, False, NO_BOAT_CLASS_ID)


no_boat_class = BoatClass.create_empty()


class ListOfBoatClasses(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return BoatClass

    def get_boat_with_name(self, boat_class_name: str, default = arg_not_passed):
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='name',
            attr_value=boat_class_name,
            default=default
        )

    def boat_with_id(self, id: str):
        if id == NO_BOAT_CLASS_ID:
            return no_boat_class

        index = self.index_of_id(id)

        return self[index]

@dataclass
class BoatClassAndPartnerAtEventOnDay:
    boat_class: BoatClass
    sail_number: str
    partner_cadet: Cadet = no_cadet_partner_required

    @property
    def has_partner(self) -> bool:
        return valid_partnership_given_partner_cadet(self.partner_cadet)

    @classmethod
    def create_empty(cls):
        return cls(
            boat_class=no_boat_class,
            sail_number="",
            partner_cadet=no_cadet_partner_required,
        )


no_boat_class_partner_or_sail_number = BoatClassAndPartnerAtEventOnDay.create_empty()
