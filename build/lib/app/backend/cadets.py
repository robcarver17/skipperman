from copy import copy

from app.backend.data.cadets import get_list_of_all_cadets
from app.data_access.configuration.configuration import MIN_CADET_AGE, MAX_CADET_AGE, SIMILARITY_LEVEL_TO_WARN_NAME, \
    SIMILARITY_LEVEL_TO_WARN_DATE
from app.objects.cadets import Cadet, ListOfCadets, is_cadet_age_surprising
from app.objects.constants import arg_not_passed


def confirm_cadet_exists(cadet_selected):
    list_of_cadets_as_str = get_list_of_cadets_as_str()
    assert cadet_selected in list_of_cadets_as_str


def get_list_of_cadets_as_str(list_of_cadets = arg_not_passed) -> list:
    if list_of_cadets is arg_not_passed:
        list_of_cadets = get_sorted_list_of_cadets()
    return [str(cadet) for cadet in list_of_cadets]


def get_list_of_cadets_as_str_similar_to_name_first(object_with_name, from_list_of_cadets: ListOfCadets = arg_not_passed) -> list:
    list_of_cadets_similar_to_first = get_list_of_cadets_similar_to_name_first(object_with_name, from_list_of_cadets=from_list_of_cadets)
    return [str(cadet) for cadet in list_of_cadets_similar_to_first]

def get_list_of_cadets_similar_to_name_first(object_with_name, from_list_of_cadets: ListOfCadets = arg_not_passed) -> ListOfCadets:
    if from_list_of_cadets is arg_not_passed:
        from_list_of_cadets = get_sorted_list_of_cadets(sort_by=SORT_BY_SURNAME)

    list_of_cadets = copy(from_list_of_cadets)

    similar_cadets = list_of_cadets.similar_surnames(object_with_name)
    similar_cadets = similar_cadets.sort_by_firstname()

    first_lot = []
    for cadet in similar_cadets:
        ## avoid double counting
        first_lot.append(list_of_cadets.pop_with_id(cadet.id))

    return ListOfCadets(first_lot+list_of_cadets)

def get_cadet_from_id(cadet_id: str) -> Cadet:
    list_of_cadets = get_list_of_all_cadets()

    return list_of_cadets.object_with_id(cadet_id)


def get_cadet_from_list_of_cadets(cadet_selected: str) -> Cadet:
    list_of_cadets = get_list_of_all_cadets()
    list_of_cadets_as_str = get_list_of_cadets_as_str(list_of_cadets=list_of_cadets)

    cadet_idx = list_of_cadets_as_str.index(cadet_selected)
    return list_of_cadets[cadet_idx]


def get_sorted_list_of_cadets(sort_by: str = arg_not_passed) -> ListOfCadets:
    master_list = get_list_of_all_cadets()
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


SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
SORT_BY_DOB_ASC = "Sort by date of birth, ascending"
SORT_BY_DOB_DSC = "Sort by date of birth, descending"


def cadet_from_id_with_passed_list(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Cadet:
    cadet = list_of_cadets.object_with_id(cadet_id)

    return cadet



def cadet_name_from_id(cadet_id: str) -> str:
    cadet = cadet_from_id(cadet_id)

    return str(cadet)


def cadet_from_id(cadet_id: str) -> Cadet:
    list_of_cadets = get_sorted_list_of_cadets()

    cadet = cadet_from_id_with_passed_list(cadet_id=cadet_id,
                                           list_of_cadets=list_of_cadets)

    return cadet



LOWEST_FEASIBLE_CADET_AGE = MIN_CADET_AGE - 2
HIGHEST_FEASIBLE_CADET_AGE = MAX_CADET_AGE + 20  ## might be backfilling


def verify_cadet_and_warn(cadet: Cadet) -> str:
    print("Checking %s" % cadet)
    warn_text = ""
    if len(cadet.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(cadet.first_name) < 4:
        warn_text += "First name seems too short. "
    if is_cadet_age_surprising(cadet):
        warn_text += "Cadet seems awfully old or young."
    warn_text += warning_for_similar_cadets(cadet=cadet)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text



def warning_for_similar_cadets(cadet: Cadet) -> str:
    similar_cadets = list_of_similar_cadets(cadet)

    if len(similar_cadets) > 0:
        similar_cadets_str = ", ".join(
            [str(other_cadet) for other_cadet in similar_cadets]
        )
        ## Some similar group_allocations, let's see if it's a match
        return "Following cadets look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""


def list_of_similar_cadets(cadet: Cadet) -> list:
    print("Checking for similar %s" % cadet)
    existing_cadets = get_list_of_all_cadets()
    similar_cadets = existing_cadets.similar_cadets(
        cadet,
        name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME,
        dob_threshold=SIMILARITY_LEVEL_TO_WARN_DATE,
    )

    return similar_cadets


