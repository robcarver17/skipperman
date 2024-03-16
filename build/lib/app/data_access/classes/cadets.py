from app.objects.cadet_at_event import ListOfCadetsAtEvent, ListOfIdentifiedCadetsAtEvent
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.groups import ListOfCadetIdsWithGroups


class DataListOfCadets(object):
    def add(self, cadet: Cadet):
        list_of_cadets = self.read()
        if cadet in list_of_cadets:
            raise Exception("Cadet %s already in list of existing cadets" % str(cadet))

        cadet_id = list_of_cadets.next_id()
        cadet.id = cadet_id
        list_of_cadets.append(cadet)

        self.write(list_of_cadets)
        return cadet

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

class DataListOfCadetsAtEvent(object):
    def read(self, event_id: str) -> ListOfCadetsAtEvent:
        raise NotImplemented

    def write(self, list_of_cadets_at_event: ListOfCadetsAtEvent, event_id: str):
        raise NotImplemented


class DataListOfIdentifiedCadetsAtEvent(object):
    def read(self, event_id: str) -> ListOfIdentifiedCadetsAtEvent:
        raise NotImplemented

    def write(self, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent, event_id: str):
        raise NotImplemented
