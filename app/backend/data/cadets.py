from typing import List

from app.data_access.storage_layer.api import DataLayer
from app.data_access.data import DEPRECATED_data
from app.objects.cadets import Cadet, ListOfCadets


class CadetData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def get_cadet_from_list_of_cadets_given_str_of_cadet(self, cadet_selected:str) -> Cadet:
        list_of_cadets = self.get_list_of_cadets()
        list_of_cadets_as_str = get_list_of_cadets_as_str(list_of_cadets) ## don't use stored version in case changes
        cadet_idx = list_of_cadets_as_str.index(cadet_selected)

        return list_of_cadets[cadet_idx]


    def confirm_cadet_exists(self, cadet_selected: str):
        list_of_cadets_as_str = self.get_list_of_cadets_as_str()
        assert cadet_selected in list_of_cadets_as_str

    def get_list_of_cadets_as_str(self) -> List[str]:
        list_of_cadets = self.get_list_of_cadets()
        return get_list_of_cadets_as_str(list_of_cadets)

    def add_cadet(self, cadet: Cadet) -> Cadet:
        list_of_cadets = self.get_list_of_cadets()
        cadet = list_of_cadets.add(cadet)
        self.save_list_of_cadets(list_of_cadets)

        return cadet

    def similar_cadets(self, cadet: Cadet):
        list_of_cadets = self.get_list_of_cadets()
        return list_of_cadets.similar_cadets(cadet)

    def get_matching_cadet_with_id_or_missing_data(self,
            cadet: Cadet,
    ) -> Cadet:
        list_of_cadets = self.get_list_of_cadets()
        matched_cadet_with_id = list_of_cadets.matching_cadet(cadet)

        return matched_cadet_with_id

    def get_cadet_with_id_(self,
            cadet_id: str,
    ) -> Cadet:
        list_of_cadets = self.get_list_of_cadets()

        return list_of_cadets.cadet_with_id(cadet_id)

    def reorder_list_of_cadet_ids_by_cadet_name(self, list_of_cadet_ids: List[str]):
        list_of_cadets = self.get_list_of_cadets_given_list_of_cadet_ids(list_of_cadet_ids)
        list_of_cadets.sort_by_name()

        return list_of_cadets.list_of_ids

    def get_list_of_cadet_names_given_list_of_cadet_ids(self,  list_of_cadet_ids: List[str]):
        list_of_cadets = self.get_list_of_cadets_given_list_of_cadet_ids(list_of_cadet_ids)
        return list_of_cadets.list_of_names()

    def get_list_of_cadets_given_list_of_cadet_ids(self, list_of_cadet_ids: List[str]) -> ListOfCadets:
        list_of_cadets = self.get_list_of_cadets()
        return ListOfCadets.subset_from_list_of_ids(full_list=list_of_cadets, list_of_ids=list_of_cadet_ids)

    def modify_cadet(self, cadet_id: str, new_cadet: Cadet):
        list_of_cadets = self.get_list_of_cadets()
        new_cadet.id = cadet_id
        list_of_cadets.replace_with_new_object(new_cadet)
        self.data_api.save_list_of_cadets(list_of_cadets)

    def get_list_of_cadets(self) -> ListOfCadets:
        list_of_cadets = self.data_api.get_list_of_cadets()
        return list_of_cadets

    def save_list_of_cadets(self, list_of_cadets: ListOfCadets):
        self.data_api.save_list_of_cadets(list_of_cadets)


def get_list_of_cadets_as_str(list_of_cadets: ListOfCadets) -> List[str]:
    return [str(cadet) for cadet in list_of_cadets]


### OLD BELOW TO DELETE

def delete_a_cadet(cadet: Cadet):
    all_cadets = DEPRECATE_load_list_of_all_cadets()
    all_cadets.pop_with_id(cadet.id)
    save_list_of_cadets(list_of_cadets=all_cadets)


def DEPRECATE_add_new_verified_cadet(cadet: Cadet) -> Cadet:
    all_cadets = DEPRECATE_load_list_of_all_cadets()
    cadet_with_id = all_cadets.add(cadet)
    save_list_of_cadets(all_cadets)
    return cadet_with_id


def save_list_of_cadets(list_of_cadets: ListOfCadets):
    DEPRECATED_data.data_list_of_cadets.write(list_of_cadets)


def DEPRECATE_load_list_of_all_cadets() -> ListOfCadets:
    return DEPRECATED_data.data_list_of_cadets.read()


