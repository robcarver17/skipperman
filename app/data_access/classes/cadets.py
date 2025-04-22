from app.objects.attendance import ListOfRawAttendanceItemsForSpecificCadet
from app.objects.cadet_with_id_at_event import ListOfCadetsWithIDAtEvent
from app.objects.identified_cadets_at_event import ListOfIdentifiedCadetsAtEvent
from app.objects.cadets import ListOfCadets
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups
from app.objects.committee import ListOfCadetsWithIdOnCommittee
from app.objects.group_notes_at_event import ListOfGroupNotesAtEventWithIds

class DataListOfCadets(object):
    def read(self) -> ListOfCadets:
        raise NotImplemented

    def write(self, list_of_cadets: ListOfCadets):
        raise NotImplemented


class DataListOfCadetsWithGroups(object):
    def read_groups_for_event(self, event_id: str) -> ListOfCadetIdsWithGroups:
        raise NotImplemented

    def write_groups_for_event(
        self, event_id: str, list_of_cadets_with_groups: ListOfCadetIdsWithGroups
    ):
        raise NotImplemented

class DataListOfGroupNotesAtEvent(object):
    def read_all_notes(self) -> ListOfGroupNotesAtEventWithIds:
        raise NotImplemented

    def write_notes(self, list_of_group_notes_with_ids: ListOfGroupNotesAtEventWithIds):
        raise NotImplemented

class DataListOfCadetsAtEvent(object):
    def read(self, event_id: str) -> ListOfCadetsWithIDAtEvent:
        raise NotImplemented

    def write(self, list_of_cadets_at_event: ListOfCadetsWithIDAtEvent, event_id: str):
        raise NotImplemented


class DataListOfIdentifiedCadetsAtEvent(object):
    def read(self, event_id: str) -> ListOfIdentifiedCadetsAtEvent:
        raise NotImplemented

    def write(
        self, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent, event_id: str
    ):
        raise NotImplemented


class DataListOfCadetsOnCommitte(object):
    def read(self) -> ListOfCadetsWithIdOnCommittee:
        raise NotImplemented

    def write(self, list_of_cadets: ListOfCadetsWithIdOnCommittee):
        raise NotImplemented

class DataAttendanceAtEventsForSpecificCadet(object):
    def read_attendance_for_cadet_id(self, cadet_id: str) -> ListOfRawAttendanceItemsForSpecificCadet:
        raise NotImplemented

    def write_attendance_for_cadet_id(
        self, list_of_attendance: ListOfRawAttendanceItemsForSpecificCadet, cadet_id:str
    ):
        raise NotImplemented
