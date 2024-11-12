from app.data_access.store.data_access import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.cadets import CadetData, SORT_BY_FIRSTNAME
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.exceptions import arg_not_passed


def get_cadet_given_cadet_as_str(data_layer: DataLayer, cadet_as_str: str) -> Cadet:
    cadet_data = CadetData(data_layer)
    cadet = cadet_data.get_cadet_from_list_of_cadets_given_str_of_cadet(cadet_as_str)

    return cadet


def DEPRECATE_get_sorted_list_of_cadets(
    interface: abstractInterface, sort_by: str = arg_not_passed
) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    return cadet_data.get_sorted_list_of_cadets(sort_by)


def get_list_of_cadets_sorted_by_first_name(data_layer: DataLayer) -> ListOfCadets:
    return get_sorted_list_of_cadets(data_layer=data_layer, sort_by=SORT_BY_FIRSTNAME)


def get_sorted_list_of_cadets(
    data_layer: DataLayer, sort_by: str = arg_not_passed
) -> ListOfCadets:
    cadet_data = CadetData(data_layer)
    return cadet_data.get_sorted_list_of_cadets(sort_by)


def cadet_name_from_id(data_layer: DataLayer, cadet_id: str) -> str:
    cadet = get_cadet_from_id(data_layer=data_layer, cadet_id=cadet_id)

    return cadet.name


def get_cadet_from_id(data_layer: DataLayer, cadet_id: str) -> Cadet:
    cadet_data = CadetData(data_layer)
    cadet = cadet_data.get_cadet_with_id(cadet_id)

    return cadet


def get_list_of_similar_cadets(data_layer: DataLayer, cadet: Cadet) -> list:
    cadet_data = CadetData(data_layer)
    return cadet_data.similar_cadets(cadet)


def get_matching_cadet_with_id(
    data_layer: DataLayer,
    cadet: Cadet,
) -> Cadet:
    cadet_data = CadetData(data_layer)
    matched_cadet_with_id = cadet_data.get_matching_cadet_with_id(cadet)

    return matched_cadet_with_id


def load_list_of_all_cadets(data_layer: DataLayer) -> ListOfCadets:
    cadet_data = CadetData(data_layer)
    return cadet_data.get_list_of_cadets()


def modify_cadet(data_layer: DataLayer, cadet_id: str, new_cadet: Cadet):
    cadet_data = CadetData(data_layer)
    cadet_data.modify_cadet(cadet_id=cadet_id, new_cadet=new_cadet)
