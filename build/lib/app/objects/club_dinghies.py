
from dataclasses import dataclass

from app.objects.generic import GenericSkipperManObjectWithIds, GenericSkipperManObject, GenericListOfObjectsWithIds

@dataclass
class ClubDinghy(GenericSkipperManObjectWithIds):
   name: str
   id: str
   capacity: int = 1
   number_available: int = 0

class ListOfClubDinghies(GenericListOfObjectsWithIds):
    def _object_class_contained(self):
        return ClubDinghy

    def add(self, club_dinghy: ClubDinghy):
        self.append(club_dinghy)

@dataclass
class CadetAtEventWithClubDinghy(GenericSkipperManObject):
    cadet_id: str
    club_dinghy_id: str

class ListOfCadetAtEventWithClubDinghies(GenericListOfObjectsWithIds):
    def _object_class_contained(self):
        return CadetAtEventWithClubDinghy


