from objects.groups import ListOfCadetsWithGroups


class DataListOfCadetsWithGroups(object):
    def read(self, event_id: str) -> ListOfCadetsWithGroups:
        raise NotImplemented

    def write(self, event_id: str, list_of_cadets_with_groups: ListOfCadetsWithGroups):
        raise NotImplemented
