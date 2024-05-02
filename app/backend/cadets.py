from copy import copy

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.cadets import DEPRECATE_load_list_of_all_cadets, CadetData, SORT_BY_SURNAME, SORT_BY_FIRSTNAME, \
    SORT_BY_DOB_ASC, SORT_BY_DOB_DSC
from app.data_access.configuration.configuration import MIN_CADET_AGE, MAX_CADET_AGE
from app.objects.cadets import Cadet, ListOfCadets, is_cadet_age_surprising
from app.objects.constants import arg_not_passed

def add_new_verified_cadet(interface: abstractInterface, cadet: Cadet) -> Cadet:
    cadet_data = CadetData(interface.data)
    cadet_data.add_cadet(cadet)

    return cadet

def DEPRECATE_confirm_cadet_exists(cadet_selected):
    list_of_cadets_as_str = DEPRECATE_get_list_of_cadets_as_str()
    assert cadet_selected in list_of_cadets_as_str


def confirm_cadet_exists(interface: abstractInterface, cadet_selected: str):
    cadet_data = CadetData(interface.data)
    cadet_data.confirm_cadet_exists(cadet_selected)


def DEPRECATE_get_list_of_cadets_as_str(list_of_cadets = arg_not_passed) -> list:
    if list_of_cadets is arg_not_passed:
        list_of_cadets = DEPRECATE_get_sorted_list_of_cadets()
    return [str(cadet) for cadet in list_of_cadets]


def get_list_of_cadets_as_str_similar_to_name_first(object_with_name, from_list_of_cadets: ListOfCadets) -> list:
    list_of_cadets_similar_to_first = get_list_of_cadets_similar_to_name_first(object_with_name, from_list_of_cadets=from_list_of_cadets)
    return [str(cadet) for cadet in list_of_cadets_similar_to_first]

def get_list_of_cadets_similar_to_name_first(object_with_name, from_list_of_cadets: ListOfCadets) -> ListOfCadets:
    list_of_cadets = copy(from_list_of_cadets)

    similar_cadets = list_of_cadets.similar_surnames(object_with_name)
    similar_cadets = similar_cadets.sort_by_firstname()

    first_lot = []
    for cadet in similar_cadets:
        ## avoid double counting
        first_lot.append(list_of_cadets.pop_with_id(cadet.id))

    return ListOfCadets(first_lot+list_of_cadets)

def DEPRECATE_get_cadet_from_id(cadet_id: str) -> Cadet:
    list_of_cadets = DEPRECATE_load_list_of_all_cadets()

    return list_of_cadets.object_with_id(cadet_id)

def get_cadet_from_id(interface: abstractInterface, cadet_id: str) -> Cadet:
    list_of_cadets = load_list_of_all_cadets(interface)

    return list_of_cadets.object_with_id(cadet_id)


def DEPRECATE_get_cadet_from_list_of_cadets(cadet_selected: str) -> Cadet:
    list_of_cadets = DEPRECATE_load_list_of_all_cadets()
    list_of_cadets_as_str = DEPRECATE_get_list_of_cadets_as_str(list_of_cadets=list_of_cadets)

    cadet_idx = list_of_cadets_as_str.index(cadet_selected)
    return list_of_cadets[cadet_idx]

def get_cadet_from_list_of_cadets(interface: abstractInterface, cadet_selected: str) -> Cadet:
    cadet_data = CadetData(interface.data)
    cadet = cadet_data.get_cadet_from_list_of_cadets_given_str_of_cadet(cadet_selected)

    return cadet


def DEPRECATE_get_sorted_list_of_cadets(sort_by: str = arg_not_passed) -> ListOfCadets:
    master_list = DEPRECATE_load_list_of_all_cadets()
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


def get_sorted_list_of_cadets(interface: abstractInterface, sort_by: str = arg_not_passed) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    return cadet_data.get_sorted_list_of_cadets(sort_by)


def cadet_from_id_with_passed_list(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Cadet:
    cadet = list_of_cadets.object_with_id(cadet_id)

    return cadet



def DEPRECATED_cadet_name_from_id(cadet_id: str) -> str:
    cadet = DEPRECATED_cadet_from_id(cadet_id)

    return str(cadet)



def cadet_name_from_id(interface: abstractInterface, cadet_id: str) -> str:
    cadet = cadet_from_id(interface=interface, cadet_id=cadet_id)

    return cadet.name

def DEPRECATED_cadet_from_id(cadet_id: str) -> Cadet:
    list_of_cadets = DEPRECATE_get_sorted_list_of_cadets()

    cadet = cadet_from_id_with_passed_list(cadet_id=cadet_id,
                                           list_of_cadets=list_of_cadets)

    return cadet

def cadet_from_id(interface: abstractInterface, cadet_id: str) -> Cadet:
    cadet_data = CadetData(interface.data)
    cadet = cadet_data.get_cadet_with_id_(cadet_id)

    return cadet



LOWEST_FEASIBLE_CADET_AGE = MIN_CADET_AGE - 2
HIGHEST_FEASIBLE_CADET_AGE = MAX_CADET_AGE + 20  ## might be backfilling



def verify_cadet_and_warn(interface: abstractInterface, cadet: Cadet) -> str:
    print("Checking %s" % cadet)
    warn_text = ""
    if len(cadet.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(cadet.first_name) < 4:
        warn_text += "First name seems too short. "
    if is_cadet_age_surprising(cadet):
        warn_text += "Cadet seems awfully old or young."
    warn_text += warning_for_similar_cadets(cadet=cadet, interface=interface)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def warning_for_similar_cadets(interface: abstractInterface, cadet: Cadet) -> str:
    similar_cadets = get_list_of_similar_cadets(interface=interface, cadet=cadet)

    if len(similar_cadets) > 0:
        similar_cadets_str = ", ".join(
            [str(other_cadet) for other_cadet in similar_cadets]
        )
        ## Some similar group_allocations, let's see if it's a match
        return "Following cadets look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""


def DEPRECATE_get_list_of_similar_cadets(cadet: Cadet) -> list:
    print("Checking for similar %s" % cadet)
    existing_cadets = DEPRECATE_load_list_of_all_cadets()
    similar_cadets = existing_cadets.similar_cadets(
        cadet
    )
    print("Similar: %s" % cadet)
    return similar_cadets

def get_list_of_similar_cadets(interface: abstractInterface, cadet: Cadet) -> list:
    cadet_data = CadetData(interface.data)
    return cadet_data.similar_cadets(cadet)


def get_matching_cadet_with_id_or_missing_data(
    interface: abstractInterface,
    cadet: Cadet,
) -> Cadet:
    cadet_data = CadetData(interface.data)
    matched_cadet_with_id = cadet_data.get_matching_cadet_with_id_or_missing_data(cadet)

    return matched_cadet_with_id


def load_list_of_all_cadets(interface: abstractInterface) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    return cadet_data.get_list_of_cadets()


def modify_cadet(interface: abstractInterface, cadet_id: str, new_cadet: Cadet):
    cadet_data = CadetData(interface.data)
    cadet_data.modify_cadet(cadet_id=cadet_id, new_cadet=new_cadet)
