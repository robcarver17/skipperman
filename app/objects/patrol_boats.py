from dataclasses import dataclass

from app.objects.utilities.exceptions import (
    arg_not_passed,
)
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_unique_object_with_attr_in_list,
    get_idx_of_unique_object_with_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds

NO_BOAT = "NO_BOAT"
NO_BOAT_ID = str(-9999)


@dataclass
class PatrolBoat(GenericSkipperManObjectWithIds):
    name: str
    hidden: bool
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name and self.hidden == other.hidden

    @property
    def is_empty(self):
        return self.name == NO_BOAT

    @classmethod
    def create_empty(cls):
        return cls(NO_BOAT, hidden=False, id=NO_BOAT_ID)


no_patrol_boat = PatrolBoat.create_empty()


class ListOfPatrolBoats(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return PatrolBoat

    def sort_from_other_list_of_boats(self, other_list_of_boats: "ListOfPatrolBoats"):
        return self.subset_from_list_of_ids_retaining_order(
            other_list_of_boats.list_of_ids
        )

    def replace(self, existing_patrol_boat: PatrolBoat, new_patrol_boat: PatrolBoat):
        object_idx = self.idx_given_name(existing_patrol_boat.name)
        new_patrol_boat.id = existing_patrol_boat.id
        self[object_idx] = new_patrol_boat

    def boat_given_id(self, patrol_boat_id: str, default=arg_not_passed):
        if patrol_boat_id == no_patrol_boat.id:
            return no_patrol_boat

        return self.object_with_id(patrol_boat_id, default=default)

    def boat_given_name(
        self, patrol_boat_name: str, default=arg_not_passed
    ) -> PatrolBoat:
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="name",
            attr_value=patrol_boat_name,
            default=default,
        )

    def idx_given_name(self, patrol_boat_name: str, default=arg_not_passed) -> int:
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="name",
            attr_value=patrol_boat_name,
            default=default,
        )

    def add(self, patrol_boat_name: str):
        try:
            assert patrol_boat_name not in self.list_of_names()
        except:
            raise Exception(
                "Can't add duplicate patrol boat %s already exists" % patrol_boat_name
            )
        patrol_boat = PatrolBoat(name=patrol_boat_name, hidden=False)
        patrol_boat.id = self.next_id()

        self.append(patrol_boat)

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))
