from app.objects.patrol_boats import ListOfPatrolBoats, ListOfPatrolBoatLabelsAtEvents
from app.objects.patrol_boats_with_volunteers_with_id import (
    ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
)
from app.objects.club_dinghies import (
    ListOfClubDinghies,
    ListOfClubDinghyLimits,
)
from app.objects.volunteers_and_cades_at_event_with_club_boat_with_ids import (
    ListOfCadetAtEventWithIdAndClubDinghies,
)

from app.objects.volunteers_and_cades_at_event_with_club_boat_with_ids import (
    ListOfVolunteerAtEventWithIdAndClubDinghies,
)


class DataListOfClubDinghies(object):
    def read(self) -> ListOfClubDinghies:
        raise NotImplemented

    def write(self, list_of_club_dinghies: ListOfClubDinghies):
        raise NotImplemented


class DataListOfClubDinghyLimits(object):
    def read(self) -> ListOfClubDinghyLimits:
        raise NotImplemented

    def write(self, list_of_club_dinghies: ListOfClubDinghyLimits):
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


class DataListOfVolunteersAtEventWithClubDinghies(object):
    def read(self, event_id: str) -> ListOfVolunteerAtEventWithIdAndClubDinghies:
        raise NotImplemented

    def write(
        self,
        list_of_volunteers_at_event_with_club_dinghies: ListOfVolunteerAtEventWithIdAndClubDinghies,
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


class DataListOfPatrolBoatLabelsAtEvent(object):
    def read(self) -> ListOfPatrolBoatLabelsAtEvents:
        raise NotImplemented

    def write(self, list_of_patrol_boat_labels: ListOfPatrolBoatLabelsAtEvents):
        raise NotImplemented
