
from dataclasses import dataclass

from app.objects.generic import GenericSkipperManObjectWithIds, GenericSkipperManObject, GenericListOfObjectsWithIds

@dataclass
class PatrolBoat(GenericSkipperManObjectWithIds):
   name: str
   id: str
   capacity: int = 3

class ListOfPatrolBoats(GenericListOfObjectsWithIds):
    def _object_class_contained(self):
        return PatrolBoat

    def add(self, patrol_boat: PatrolBoat):
        self.append(patrol_boat)

@dataclass
class VolunteerAtEventWithPatrolBoat(GenericSkipperManObject):
    volunteer_id: str
    patrol_boat_id: str

class ListOfVolunteersAtEventWithPatrolBoats(GenericListOfObjectsWithIds):
    def _object_class_contained(self):
        return VolunteerAtEventWithPatrolBoat


