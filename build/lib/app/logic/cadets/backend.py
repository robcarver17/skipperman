from app.data_access.configuration.configuration import MIN_CADET_AGE, MAX_CADET_AGE, SIMILARITY_LEVEL_TO_WARN_NAME, \
    SIMILARITY_LEVEL_TO_WARN_DATE
from app.data_access.data import data
from app.logic.cadets.constants import CADET
from app.logic.abstract_interface import abstractInterface
from app.objects.cadets import Cadet, ListOfCadets, is_cadet_age_surprising
from app.objects.constants import arg_not_passed


def confirm_cadet_exists(cadet_selected):
    list_of_cadets_as_str = get_list_of_cadets_as_str()
    assert cadet_selected in list_of_cadets_as_str


def get_list_of_cadets_as_str(list_of_cadets = arg_not_passed) -> list:
    if list_of_cadets is arg_not_passed:
        list_of_cadets = get_list_of_cadets()
    return [str(cadet) for cadet in list_of_cadets]


def update_state_for_specific_cadet(interface: abstractInterface, cadet_selected: str):
    interface.set_persistent_value(key=CADET, value=cadet_selected)


def get_cadet_from_state(interface: abstractInterface) -> Cadet:
    cadet_selected = get_cadet_selected_from_state(interface)

    return get_cadet_from_list_of_cadets(cadet_selected)


def get_cadet_selected_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(CADET)


def get_cadet_from_list_of_cadets(cadet_selected: str) -> Cadet:
    list_of_cadets = get_list_of_cadets()
    list_of_cadets_as_str = get_list_of_cadets_as_str(list_of_cadets=list_of_cadets)

    cadet_idx = list_of_cadets_as_str.index(cadet_selected)
    return list_of_cadets[cadet_idx]


def get_list_of_cadets(sort_by: str = arg_not_passed) -> ListOfCadets:
    master_list = data.data_list_of_cadets.read()
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

def get_cadet_from_id(id: str, list_of_cadets: ListOfCadets):
    return list_of_cadets.object_with_id(id)


def cadet_name_from_id(cadet_id: str) -> str:
    cadet = cadet_from_id(cadet_id)

    return str(cadet)


def cadet_from_id(cadet_id: str) -> Cadet:
    list_of_cadets = get_list_of_cadets()

    cadet = cadet_from_id_with_passed_list(cadet_id=cadet_id,
                                           list_of_cadets=list_of_cadets)

    return cadet


def cadet_from_id_with_passed_list(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Cadet:
    cadet = list_of_cadets.object_with_id(cadet_id)

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
        return "Following group_allocations look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""


def list_of_similar_cadets(cadet: Cadet) -> list:
    print("Checking for similar %s" % cadet)
    existing_cadets = data.data_list_of_cadets.read()
    similar_cadets = existing_cadets.similar_cadets(
        cadet,
        name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME,
        dob_threshold=SIMILARITY_LEVEL_TO_WARN_DATE,
    )

    return similar_cadets


def add_new_verified_cadet(cadet: Cadet):
    data.data_list_of_cadets.add(cadet)


def delete_a_cadet(cadet: Cadet):
    all_cadets = data.data_list_of_cadets.read()
    all_cadets.pop_with_id(cadet.id)
    data.data_list_of_cadets.write(all_cadets)