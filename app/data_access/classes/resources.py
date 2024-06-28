from app.objects.patrol_boats import (
    ListOfPatrolBoats,
    ListOfVolunteersAtEventWithPatrolBoats,
)
from app.objects.club_dinghies import (
    ListOfClubDinghies,
    ListOfCadetAtEventWithClubDinghies,
)


class DataListOfClubDinghies(object):
    def read(self) -> ListOfClubDinghies:
        raise NotImplemented

    def write(self, list_of_club_dinghies: ListOfClubDinghies):
        raise NotImplemented


class DataListOfPatrolBoats(object):
    def read(self) -> ListOfPatrolBoats:
        raise NotImplemented

    def write(self, list_of_patrol_boats: ListOfPatrolBoats):
        raise NotImplemented


class DataListOfCadetAtEventWithClubDinghies(object):
    def read(self, event_id: str) -> ListOfCadetAtEventWithClubDinghies:
        raise NotImplemented

    def write(
        self,
        list_of_cadets_at_event_with_club_dinghies: ListOfCadetAtEventWithClubDinghies,
        event_id: str,
    ):
        raise NotImplemented


class DataListOfVolunteersAtEventWithPatrolBoats(object):
    def read(self, event_id: str) -> ListOfVolunteersAtEventWithPatrolBoats:
        raise NotImplemented

    def write(
        self,
        list_of_volunteers_at_event_with_patrol_boats: ListOfVolunteersAtEventWithPatrolBoats,
        event_id: str,
    ):
        raise NotImplemented
