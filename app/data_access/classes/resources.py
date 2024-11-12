from app.objects.patrol_boats import ListOfPatrolBoats
from app.objects.patrol_boats_with_volunteers_with_id import (
    ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
)
from app.objects.club_dinghies import (
    ListOfClubDinghies,
)
from app.objects.cadet_at_event_with_club_boat_with_ids import (
    ListOfCadetAtEventWithIdAndClubDinghies,
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
    def read(self, event_id: str) -> ListOfCadetAtEventWithIdAndClubDinghies:
        raise NotImplemented

    def write(
        self,
        list_of_cadets_at_event_with_club_dinghies: ListOfCadetAtEventWithIdAndClubDinghies,
        event_id: str,
    ):
        raise NotImplemented


class DataListOfVolunteersAtEventWithPatrolBoats(object):
    def read(self, event_id: str) -> ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        raise NotImplemented

    def write(
        self,
        list_of_volunteers_at_event_with_patrol_boats: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
        event_id: str,
    ):
        raise NotImplemented
