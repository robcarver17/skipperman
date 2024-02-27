
from dataclasses import dataclass
from typing import List

from app.objects.constants import missing_data, arg_not_passed
from app.objects.generic import GenericSkipperManObjectWithIds, GenericSkipperManObject, GenericListOfObjectsWithIds

@dataclass
class PatrolBoat(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)



class ListOfPatrolBoats(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return PatrolBoat

    def delete_given_name(self, patrol_boat_name: str):
        idx = self.idx_given_name(patrol_boat_name)
        if idx is missing_data:
            raise Exception("Can't find patrol boat with name to delete %s" % patrol_boat_name)
        self.pop(idx)

    def idx_given_name(self, patrol_boat_name: str):
        id = [item.id for item in self if item.name == patrol_boat_name]

        if len(id)==0:
            return missing_data
        elif len(id)>1:
            raise Exception("Found more than one patrol boat with same name should be impossible")

        return self.index_of_id(str(id[0]))

    def add(self, patrol_boat_name: str):
        patrol_boat = PatrolBoat(name=patrol_boat_name)
        try:
            assert patrol_boat_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate patrol boat %s already exists" % patrol_boat_name)
        patrol_boat.id = self.next_id()

        self.append(patrol_boat)

    def list_of_names(self):
        return [patrol_boat.name for patrol_boat in self]

@dataclass
class VolunteerAtEventWithPatrolBoat(GenericSkipperManObject):
    volunteer_id: str
    patrol_boat_id: str

    @classmethod
    def create_unallocated_boat(cls, patrol_boat_id: str):
        return cls(volunteer_id="", patrol_boat_id=patrol_boat_id)

    @property
    def is_empty(self):
        return self.volunteer_id==""

class ListOfVolunteersAtEventWithPatrolBoats(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return VolunteerAtEventWithPatrolBoat

    def add_unallocated_boat(self, patrol_boat_id: str):
        self.append(VolunteerAtEventWithPatrolBoat.create_unallocated_boat(patrol_boat_id=patrol_boat_id))

    def add_volunteer_with_boat(self, volunteer_id: str, patrol_boat_id: str):
        pass

    def list_of_boats_at_event_including_unallocated(self, list_of_patrol_boats: ListOfPatrolBoats):
        ## sorted according to order of list of patrol boats
        list_of_boat_ids_at_event_including_unallocated = self.list_of_boat_ids_at_event_including_unallocated()
        list_of_boats = [boat for boat in list_of_patrol_boats if boat.id in list_of_boat_ids_at_event_including_unallocated]

        return ListOfPatrolBoats(list_of_boats)

    def list_of_boat_ids_at_event_including_unallocated(self) -> List[str]:
        all_ids = [item.patrol_boat_id for item in self]
        return list(set(all_ids))

