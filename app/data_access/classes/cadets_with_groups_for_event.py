from app.objects.groups import ListOfCadetIdsWithGroups


class DataListOfCadetsWithGroups(object):
    def read_groups_for_event(self, event_id: str) -> ListOfCadetIdsWithGroups:
        raise NotImplemented

    def write_groups_for_event(
        self, event_id: str, list_of_cadets_with_groups: ListOfCadetIdsWithGroups
    ):
        raise NotImplemented

    def read_last_groups(self) -> ListOfCadetIdsWithGroups:
        raise NotImplemented

    def write_last_groups(
        self, list_of_cadets_with_groups: ListOfCadetIdsWithGroups
    ):
        raise NotImplemented
