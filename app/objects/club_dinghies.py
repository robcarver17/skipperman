from dataclasses import dataclass

from app.objects.exceptions import missing_data, arg_not_passed, MissingData
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds, get_idx_of_unique_object_with_attr_in_list,
)
from app.objects.generic_objects import GenericSkipperManObjectWithIds


NO_CLUB_DINGHY_ID = str(-9999)
NO_CLUB_DINGHY_NAME = ''

@dataclass
class ClubDinghy(GenericSkipperManObjectWithIds):
    name: str
    hidden: bool
    id: str = arg_not_passed

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.hidden == other.hidden

    @classmethod
    def create_empty(cls):
        return cls(NO_CLUB_DINGHY_NAME, hidden=False, id=NO_CLUB_DINGHY_ID)


no_club_dinghy = ClubDinghy.create_empty()


class ListOfClubDinghies(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return ClubDinghy


    def replace(self, existing_club_dinghy: ClubDinghy, new_club_dinghy: ClubDinghy):
        object_idx = self.idx_given_name(existing_club_dinghy.name)
        new_club_dinghy.id = existing_club_dinghy.id
        self[object_idx] = new_club_dinghy


    def club_dinghy_with_name(self, boat_name: str,  default=arg_not_passed) -> ClubDinghy:
        idx = self.idx_given_name(boat_name, default=None)
        if idx is None:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

        return self[idx]


    def idx_given_name(self, boat_name: str, default=arg_not_passed):
        return  get_idx_of_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='name',
            attr_value=boat_name,
            default=default
        )


    def add(self, boat_name: str):
        try:
            assert boat_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate dinghy %s already exists" % boat_name)
        boat = ClubDinghy(name=boat_name, hidden=False)
        boat.id = self.next_id()

        self.append(boat)

    def list_of_names(self):
        return [boat.name for boat in self]

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))
