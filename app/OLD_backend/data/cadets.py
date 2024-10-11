from typing import List

from app.objects.exceptions import arg_not_passed

from app.data_access.store.data_layer import DataLayer
from app.objects.cadets import Cadet, ListOfCadets


class CadetData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api


    def get_sorted_list_of_cadets(self, sort_by: str = arg_not_passed) -> ListOfCadets:
        master_list = self.get_list_of_cadets()
        if sort_by is arg_not_passed:
            return master_list
        if sort_by == SORT_BY_SURNAME:
            return master_list.sort_by_surname()
        elif sort_by == SORT_BY_FIRSTNAME:
            return master_list.sort_by_firstname()
        elif sort_by == SORT_BY_DOB_ASC:
            return master_list.sort_by_dob_asc()
        elif sort_by == SORT_BY_DOB_DSC:
            return master_list.sort_by_dob_desc()
        else:
            return master_list

    def get_cadet_from_list_of_cadets_given_str_of_cadet(
        self, cadet_selected: str
    ) -> Cadet:
        list_of_cadets = self.get_list_of_cadets()
        list_of_cadets_as_str = get_list_of_cadets_as_str(
            list_of_cadets
        )  ## don't use stored version in case changes
        cadet_idx = list_of_cadets_as_str.index(cadet_selected)

        return list_of_cadets[cadet_idx]


    def add_cadet(self, cadet: Cadet) -> Cadet:
        list_of_cadets = self.get_list_of_cadets()
        cadet = list_of_cadets.add(cadet)
        self.save_list_of_cadets(list_of_cadets)

        return cadet


    def replace_cadet_with_id_with_new_cadet_details(
        self, existing_cadet_id: str, new_cadet: Cadet
    ):
        list_of_cadets = self.get_list_of_cadets()
        list_of_cadets.replace_cadet_with_id_with_new_cadet_details(
            existing_cadet_id=existing_cadet_id, new_cadet=new_cadet
        )
        self.save_list_of_cadets(list_of_cadets)

    def similar_cadets(self, cadet: Cadet):
        list_of_cadets = self.get_list_of_cadets()
        return list_of_cadets.similar_cadets(cadet)

    def get_matching_cadet_with_id(
        self,
        cadet: Cadet,
    ) -> Cadet:
        list_of_cadets = self.get_list_of_cadets()
        matched_cadet_with_id = list_of_cadets.matching_cadet(cadet)

        return matched_cadet_with_id

    def get_cadet_with_id(
        self,
        cadet_id: str,
    ) -> Cadet:
        list_of_cadets = self.get_list_of_cadets()

        return list_of_cadets.cadet_with_id(cadet_id)

    def reorder_list_of_cadet_ids_by_cadet_name(self, list_of_cadet_ids: List[str]):
        list_of_cadets = self.get_list_of_cadets_given_list_of_cadet_ids(
            list_of_cadet_ids
        )
        list_of_cadets.sort_by_name()

        return list_of_cadets.list_of_ids

    def get_list_of_cadet_names_given_list_of_cadet_ids(
        self, list_of_cadet_ids: List[str]
    ):
        list_of_cadets = self.get_list_of_cadets_given_list_of_cadet_ids(
            list_of_cadet_ids
        )
        return list_of_cadets.list_of_names()

    def get_list_of_cadets_given_list_of_cadet_ids(
        self, list_of_cadet_ids: List[str]
    ) -> ListOfCadets:
        list_of_cadets = self.get_list_of_cadets()
        return ListOfCadets.subset_from_list_of_ids(
            full_list=list_of_cadets, list_of_ids=list_of_cadet_ids
        )

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


SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
SORT_BY_DOB_ASC = "Sort by date of birth, ascending"
SORT_BY_DOB_DSC = "Sort by date of birth, descending"
