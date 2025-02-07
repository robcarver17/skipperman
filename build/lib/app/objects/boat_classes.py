from dataclasses import dataclass

from app.objects.exceptions import missing_data, arg_not_passed, MultipleMatches, MissingData
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)

from app.objects.generic_objects import GenericSkipperManObjectWithIds

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
        if id ==NO_BOAT_CLASS_ID:
            return no_boat_class

        index = self.index_of_id(id)

        return self[index]

    def boat_class_given_name(self, boat_class_name: str, default= missing_data):
        if boat_class_name == no_boat_class.name:
            return no_boat_class
        idx = self.idx_given_name(boat_class_name, default=None)
        if idx is None:
            return default

        return self[idx]

    def replace(self, existing_boat_class: BoatClass, new_boat_class: BoatClass):
        object_idx = self.idx_given_name(existing_boat_class.name)
        new_boat_class.id = existing_boat_class.id
        self[object_idx] = new_boat_class

    def idx_given_name(self, boat_name: str, default=arg_not_passed):
        id = [item.id for item in self if item.name == boat_name]

        if len(id) == 0:
            if default is arg_not_passed:
                raise MissingData()
            else:
                return default
        elif len(id) > 1:
            raise MultipleMatches(
                "Found more than one boat with same name should be impossible"
            )

        return self.index_of_id(str(id[0]))

    def add(self, boat_name: str):
        try:
            assert boat_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate dinghy %s already exists" % boat_name)
        boat = BoatClass(name=boat_name, hidden=False)
        boat.id = self.next_id()

        self.append(boat)

    def list_of_names(self):
        return [boat.name for boat in self]

    def check_for_duplicated_names(self):
        list_of_names = [role.name for role in self]
        assert len(list_of_names) == len(set(list_of_names))
