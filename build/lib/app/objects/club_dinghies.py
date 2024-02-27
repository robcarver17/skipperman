
from dataclasses import dataclass

from app.objects.constants import missing_data, arg_not_passed
from app.objects.generic import GenericSkipperManObjectWithIds, GenericSkipperManObject, GenericListOfObjectsWithIds

@dataclass
class ClubDinghy(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name


class ListOfClubDinghies(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return ClubDinghy

    def delete_given_name(self, boat_name: str):
        idx = self.idx_given_name(boat_name)
        if idx is missing_data:
            raise Exception("Can't find boat with name to delete %s" % boat_name)
        self.pop(idx)

    def idx_given_name(self, boat_name: str):
        id = [item.id for item in self if item.name == boat_name]

        if len(id)==0:
            return missing_data
        elif len(id)>1:
            raise Exception("Found more than one boat with same name should be impossible")

        return self.index_of_id(str(id[0]))

    def add(self, boat_name: str):
        boat = ClubDinghy(name=boat_name)
        try:
            assert boat_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate dinghy %s already exists" % boat_name)
        boat.id = self.next_id()

        self.append(boat)

    def list_of_names(self):
        return [boat.name for boat in self]

@dataclass
class CadetAtEventWithClubDinghy(GenericSkipperManObject):
    cadet_id: str
    club_dinghy_id: str

class ListOfCadetAtEventWithClubDinghies(GenericListOfObjectsWithIds):
    def _object_class_contained(self):
        return CadetAtEventWithClubDinghy


