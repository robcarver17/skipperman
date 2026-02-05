from dataclasses import dataclass

from app.objects.utilities.exceptions import missing_data, arg_not_passed, MissingData
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_idx_of_unique_object_with_attr_in_list,
    GenericListOfObjects,
)
from app.objects.utilities.generic_objects import (
    GenericSkipperManObjectWithIds,
    GenericSkipperManObject,
)

NO_CLUB_DINGHY_ID = str(-9999)
NO_CLUB_DINGHY_NAME = ""


@dataclass
class ClubDinghy(GenericSkipperManObjectWithIds):
    name: str
    hidden: bool
    id: str = arg_not_passed

    def __hash__(self):
        return hash(self.name) + hash(str(self.hidden)) * 10000

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


    def club_dinghy_with_id(self, dinghy_id: str, default=arg_not_passed):
        if dinghy_id == no_club_dinghy_id:
            return no_club_dinghy

        return self.object_with_id(dinghy_id, default=default)


no_club_dinghy_id = no_club_dinghy.id

OLD_event_id_for_generic_limit = "generic_limit"
event_id_for_generic_limit = str("-99994")

@dataclass
class ClubDinghyWithLimitAtEvent(GenericSkipperManObject):
    club_dinghy_id: str
    limit: int
    event_id: str = event_id_for_generic_limit




class ListOfClubDinghyLimits(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return ClubDinghyWithLimitAtEvent



@dataclass
class ClubDinghyAndGenericLimit:
    club_dinghy: ClubDinghy
    limit: int

    def __repr__(self):
        return self.club_dinghy.name

    @property
    def hidden(self):
        return self.club_dinghy.hidden