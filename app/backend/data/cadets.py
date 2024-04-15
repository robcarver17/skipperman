from typing import List

from app.data_access.storage_layer.api import DataApi
from app.data_access.data import data
from app.objects.cadets import Cadet, ListOfCadets

class CadetData():
    def __init__(self, data_api: DataApi):
        self.data_api = data_api

    def reorder_list_of_cadet_ids_by_cadet_name(self, list_of_cadet_ids: List[str]):
        list_of_cadets = self.get_list_of_cadets_given_list_of_cadet_ids(list_of_cadet_ids)
        list_of_cadets.sort_by_name()

        return list_of_cadets.list_of_ids

    def get_list_of_cadet_names_given_list_of_cadet_ids(self,  list_of_cadet_ids: List[str]):
        list_of_cadets = self.get_list_of_cadets_given_list_of_cadet_ids(list_of_cadet_ids)
        return list_of_cadets.list_of_names()

    def get_list_of_cadets_given_list_of_cadet_ids(self, list_of_cadet_ids: List[str]) -> ListOfCadets:
        list_of_cadets = self.data_api.list_of_cadets
        return ListOfCadets.subset_from_list_of_ids(full_list=list_of_cadets, list_of_ids=list_of_cadet_ids)


### OLD BELOW TO DELETE

def delete_a_cadet(cadet: Cadet):
    all_cadets = load_list_of_all_cadets()
    all_cadets.pop_with_id(cadet.id)
    save_list_of_cadets(list_of_cadets=all_cadets)


def add_new_verified_cadet(cadet: Cadet) -> Cadet:
    all_cadets = load_list_of_all_cadets()
    cadet_with_id = all_cadets.add(cadet)
    save_list_of_cadets(all_cadets)
    return cadet_with_id

def save_list_of_cadets(list_of_cadets: ListOfCadets):
    data.data_list_of_cadets.write(list_of_cadets)


def load_list_of_all_cadets() -> ListOfCadets:
    return data.data_list_of_cadets.read()
