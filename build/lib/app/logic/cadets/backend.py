from app.data_access.data import data
from app.logic.cadets.constants import CADET
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.objects.cadets import Cadet, ListOfCadets
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
