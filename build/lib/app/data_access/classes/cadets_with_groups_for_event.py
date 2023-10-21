from app.objects.groups import ListOfCadetIdsWithGroups


class DataListOfCadetsWithGroups(object):
    def read(self, event_id: str) -> ListOfCadetIdsWithGroups:
        raise NotImplemented

    def write(
        self, event_id: str, list_of_cadets_with_groups: ListOfCadetIdsWithGroups
    ):
        raise NotImplemented
