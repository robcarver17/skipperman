from dataclasses import dataclass

from app.objects.exceptions import arg_not_passed, missing_data, MissingData, MultipleMatches
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.generic_objects import GenericSkipperManObjectWithIds

NO_BOAT = "NO_BOAT"


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
        return cls(NO_BOAT, hidden=False)

no_patrol_boat = PatrolBoat.create_empty()

class ListOfPatrolBoats(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return PatrolBoat

    def sort_from_other_list_of_boats(self, other_list_of_boats: "ListOfPatrolBoats"):
        return ListOfPatrolBoats([boat for boat in other_list_of_boats if boat in self])

    def replace(self, existing_patrol_boat: PatrolBoat, new_patrol_boat: PatrolBoat):
        object_idx = self.idx_given_name(existing_patrol_boat.name)
        new_patrol_boat.id = existing_patrol_boat.id
        self[object_idx] = new_patrol_boat

    def boat_given_name(self, patrol_boat_name: str) -> PatrolBoat:
        matching = [item for item in self if item.name == patrol_boat_name]

        if len(matching) == 0:
            raise MissingData
        elif len(matching) > 1:
            raise MultipleMatches(
                "Found more than one patrol boat with same name should be impossible"
            )

        return matching[0]

    def idx_given_name(self, patrol_boat_name: str) -> int:
        boat = self.boat_given_name(patrol_boat_name)
        return self.index(boat)

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

    def list_of_names(self):
        return [patrol_boat.name for patrol_boat in self]

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))
