from dataclasses import dataclass

from app.objects.exceptions import missing_data, arg_not_passed, MissingData
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_idx_of_unique_object_with_attr_in_list, GenericListOfObjects,
)
from app.objects.generic_objects import GenericSkipperManObjectWithIds, GenericSkipperManObject

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

    def visible_only(self):
        return ListOfClubDinghies([
            item for item in self if not item.hidden
        ])

    def replace(self, existing_club_dinghy: ClubDinghy, new_club_dinghy: ClubDinghy):
        object_idx = self.idx_given_name(existing_club_dinghy.name)
        new_club_dinghy.id = existing_club_dinghy.id
        self[object_idx] = new_club_dinghy

    def club_dinghy_with_name(
        self, boat_name: str, default=arg_not_passed
    ) -> ClubDinghy:
        if boat_name == no_club_dinghy.name:
            return no_club_dinghy

        idx = self.idx_given_name(boat_name, default=None)
        if idx is None:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

        return self[idx]

    def idx_given_name(self, boat_name: str, default=arg_not_passed):
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self, attr_name="name", attr_value=boat_name, default=default
        )

    def club_dinghy_with_id(self, dinghy_id: str, default=arg_not_passed):
        if dinghy_id == no_club_dinghy_id:
            return no_club_dinghy

        return self.object_with_id(dinghy_id, default=default)

    def add(self, boat_name: str):
        try:
            assert boat_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate dinghy %s already exists" % boat_name)
        boat = ClubDinghy(name=boat_name, hidden=False)
        boat.id = self.next_id()

        self.append(boat)

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))


no_club_dinghy_id = no_club_dinghy.id

event_id_for_generic_limit = str("generic_limit")

@dataclass
class ClubDinghyWithLimitAtEvent(GenericSkipperManObject):
    club_dinghy_id: str
    limit: int
    event_id: str =event_id_for_generic_limit


from app.objects.generic_list_of_objects import get_unique_object_with_multiple_attr_in_list

class ListOfClubDinghyLimits(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return ClubDinghyWithLimitAtEvent

    def get_general_limit_for_club_dinghy_id(self, club_dinghy_id: str):
        return self.get_limit_for_event_id_and_club_dinghy_id(event_id=event_id_for_generic_limit, club_dinghy_id=club_dinghy_id)

    def get_limit_for_event_id_and_club_dinghy_id(self, event_id: str, club_dinghy_id: str, default = arg_not_passed):
        limit_object = get_unique_object_with_multiple_attr_in_list(
            self,
            dict_of_attributes={
                'club_dinghy_id':club_dinghy_id,
                'event_id':event_id
            },
            default=missing_data
        )
        if limit_object is missing_data:
            if default is arg_not_passed:
                raise Exception("Missing limit")
            else:
                return default

        return limit_object.limit

    def update_general_limit_for_club_dinghy_id(self, club_dinghy_id: str, limit: int):
        self.update_limit_for_event_id_and_club_dinghy_id(event_id=event_id_for_generic_limit,
                                                          club_dinghy_id=club_dinghy_id,
                                                          limit=limit)

    def update_limit_for_event_id_and_club_dinghy_id(self, event_id: str, club_dinghy_id: str, limit:int):
        existing_limit = get_unique_object_with_multiple_attr_in_list(
            self,
            dict_of_attributes={
                'club_dinghy_id':club_dinghy_id,
                'event_id':event_id
            },
            default=missing_data
        )
        if existing_limit is missing_data:
            self.append(
                ClubDinghyWithLimitAtEvent(
                    event_id=event_id,
                    club_dinghy_id=club_dinghy_id,
                    limit=limit
                )
            )
        else:
            existing_limit.limit = limit

    def unique_list_of_event_ids(self):
        return list(set([limit_in_list.event_id for limit_in_list in self]))


