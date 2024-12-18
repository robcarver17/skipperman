from dataclasses import dataclass

from app.objects.exceptions import missing_data, arg_not_passed
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)

from app.objects.generic_objects import GenericSkipperManObjectWithIds


@dataclass
class BoatClass(GenericSkipperManObjectWithIds):
    name: str
    hidden: bool
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.hidden == other.hidden


class ListOfBoatClasses(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return BoatClass

    def replace(self, existing_boat: BoatClass, new_boat: BoatClass):
        object_idx = self.idx_given_name(existing_boat.name)
        new_boat.id = existing_boat.id
        self[object_idx] = new_boat

    def id_given_name(self, name: str) -> str:
        ids = [item.id for item in self if item.name == name]

        if len(ids) == 0:
            return missing_data
        elif len(ids) > 1:
            raise Exception(
                "Found more than one boat with same name should be impossible"
            )

        return ids[0]

    def name_given_id(self, id: str) -> str:
        names = [item.name for item in self if item.id == id]

        if len(names) == 0:
            return missing_data
        elif len(names) > 1:
            raise Exception(
                "Found more than one boat with same ID should be impossible"
            )

        return names[0]

    def delete_given_name(self, boat_name: str):
        idx = self.idx_given_name(boat_name)
        if idx is missing_data:
            raise Exception("Can't find boat with name to delete %s" % boat_name)
        self.pop(idx)

    def idx_given_name(self, boat_name: str):
        id = [item.id for item in self if item.name == boat_name]

        if len(id) == 0:
            return missing_data
        elif len(id) > 1:
            raise Exception(
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