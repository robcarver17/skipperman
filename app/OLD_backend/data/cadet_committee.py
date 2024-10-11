import datetime

from app.objects.exceptions import missing_data, MissingData

from app.objects.cadets import ListOfCadets, Cadet

from app.objects.committee import ListOfCadetsWithIdOnCommittee
from app.objects.composed.committee import CadetOnCommittee, ListOfCadetsOnCommittee

from app.OLD_backend.data.cadets import CadetData

from app.data_access.store.data_layer import DataLayer

## FIX ME KEPT ONLY BECAUSE CLOTHING DEPENDENCIES
class CadetCommitteeData:
    def __init__(self, data_layer: DataLayer):
        self.data_layer = data_layer
        self.store = data_layer.store


    def get_list_of_current_cadets_on_committee(self) -> ListOfCadetsWithIdOnCommittee:
        committee = self.get_list_of_cadets_with_id_on_committee()

        return committee.currently_active()


    def get_list_of_cadets_with_id_on_committee(self) -> ListOfCadetsWithIdOnCommittee:
        return self.data_layer.get_list_of_cadets_on_committee()

