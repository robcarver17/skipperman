import datetime
from copy import copy

from app.objects.volunteers import Volunteer

from app.data_access.store.data_access import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.cadets import CadetData, SORT_BY_SURNAME, SORT_BY_FIRSTNAME
from app.objects.cadets import Cadet, ListOfCadets, is_cadet_age_surprising
from app.objects.exceptions import arg_not_passed


def add_new_verified_cadet(data_layer: DataLayer, cadet: Cadet) -> Cadet:
    cadet_data = CadetData(data_layer)
    cadet_data.add_cadet(cadet)

    return cadet



def get_list_of_cadets_with_those_with_name_similar_to_volunteer_with_listed_first(
    volunteer: Volunteer, from_list_of_cadets: ListOfCadets
) -> ListOfCadets:
    volunteer_as_pseudo_cadet = Cadet(first_name=volunteer.first_name, surname=volunteer.surname, date_of_birth=datetime.date(1970,1,1)) ## so matching works

    similar_cadets = from_list_of_cadets.similar_surnames(volunteer_as_pseudo_cadet)
    similar_cadets = similar_cadets.sort_by_firstname()

    reamining_list_of_cadets = copy(from_list_of_cadets)
    list_of_similar_cadets_to_insert_at_front_of_list = []
    for cadet in similar_cadets:
        ## avoid double counting
        list_of_similar_cadets_to_insert_at_front_of_list.append(reamining_list_of_cadets.pop_with_id(cadet.id))

    return ListOfCadets(list_of_similar_cadets_to_insert_at_front_of_list + reamining_list_of_cadets)



def get_cadet_given_cadet_as_str(data_layer: DataLayer, cadet_as_str: str) -> Cadet:
    cadet_data = CadetData(data_layer)
    cadet = cadet_data.get_cadet_from_list_of_cadets_given_str_of_cadet(cadet_as_str)

    return cadet


def DEPRECATE_get_sorted_list_of_cadets(
    interface: abstractInterface, sort_by: str = arg_not_passed
) -> ListOfCadets:
    cadet_data = CadetData(interface.data)
    return cadet_data.get_sorted_list_of_cadets(sort_by)


def get_list_of_cadets_sorted_by_surname(
    data_layer: DataLayer
) -> ListOfCadets:
    return get_sorted_list_of_cadets(data_layer=data_layer, sort_by=SORT_BY_SURNAME)


def get_list_of_cadets_sorted_by_first_name(
    data_layer: DataLayer
) -> ListOfCadets:
    return get_sorted_list_of_cadets(data_layer=data_layer, sort_by=SORT_BY_FIRSTNAME)

def get_sorted_list_of_cadets(
    data_layer: DataLayer, sort_by: str = arg_not_passed
) -> ListOfCadets:
    cadet_data = CadetData(data_layer)
    return cadet_data.get_sorted_list_of_cadets(sort_by)



def cadet_name_from_id(data_layer: DataLayer, cadet_id: str) -> str:
    cadet = get_cadet_from_id(
        data_layer=data_layer, cadet_id=cadet_id
    )

    return cadet.name




def get_cadet_from_id(data_layer: DataLayer, cadet_id: str) -> Cadet:
    cadet_data = CadetData(data_layer)
    cadet = cadet_data.get_cadet_with_id(cadet_id)

    return cadet


def verify_cadet_and_return_warnings(data_layer: DataLayer, cadet: Cadet) -> str:
    print("Checking %s" % cadet)
    warn_text = ""
    if len(cadet.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(cadet.first_name) < 4:
        warn_text += "First name seems too short. "
    if is_cadet_age_surprising(cadet):
        warn_text += "Cadet seems awfully old or young."
    warn_text += warning_for_similar_cadets(cadet=cadet, data_layer=data_layer)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def warning_for_similar_cadets(data_layer: DataLayer,  cadet: Cadet) -> str:
    similar_cadets = get_list_of_similar_cadets(data_layer=data_layer, cadet=cadet)

    if len(similar_cadets) > 0:
        similar_cadets_str = ", ".join(
            [str(other_cadet) for other_cadet in similar_cadets]
        )
        return "Following cadets look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""


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


