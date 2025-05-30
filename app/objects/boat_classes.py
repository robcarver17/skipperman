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

    def boat_with_id(self, id: str):
        if id == NO_BOAT_CLASS_ID:
            return no_boat_class

        index = self.index_of_id(id)

        return self[index]

    def boat_class_given_name(
        self, boat_class_name: str, default=arg_not_passed
    ) -> BoatClass:
        if boat_class_name == no_boat_class.name:
            return no_boat_class
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_value=boat_class_name,
            attr_name="name",
            default=default,
        )

    def replace(self, existing_boat_class: BoatClass, new_boat_class: BoatClass):
        object_idx = self.idx_given_name(existing_boat_class.name)
        new_boat_class.id = existing_boat_class.id
        self[object_idx] = new_boat_class

    def idx_given_name(self, boat_name: str, default=arg_not_passed):
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self, attr_value=boat_name, attr_name="name", default=default
        )

    def add(self, boat_name: str):
        try:
            assert boat_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate dinghy %s already exists" % boat_name)
        boat = BoatClass(name=boat_name, hidden=False)
        boat.id = self.next_id()

        self.append(boat)

    def check_for_duplicated_names(self):
        list_of_names = [role.name for role in self]
        assert len(list_of_names) == len(set(list_of_names))


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
