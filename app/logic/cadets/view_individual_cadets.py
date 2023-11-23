from typing import Union
from app.logic.abstract_form import Form, NewForm, Line, ListOfLines, form_with_message_and_finished_button
from app.data_access.data import data
from app.logic.abstract_logic_api import initial_state_form
from app.logic.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import INITIAL_STATE
from app.logic.cadets.view_cadets import get_list_of_cadets

from app.objects.cadets import Cadet

# FIXME NOT PROPERLY IMPLEMENTED
# FIXME ADD OTHER INFORMATION ABOUT CADET HERE
# FIXME ADD DELETE / EDIT OPTIONS

CADET= "Selected_Cadet"

def display_form_view_individual_cadet(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    cadet_selected = interface.last_button_pressed()
    try:
        confirm_cadet_exists(cadet_selected)
    except:
        interface.log_error(
            "Cadet %s no longer in list- someone else has deleted or file corruption?"
            % cadet_selected
        )
        return initial_state_form

    update_state_for_specific_cadet(
        interface=interface, cadet_selected=cadet_selected
    )

    return display_form_for_selected_cadet(cadet_selected=cadet_selected)


def post_form_view_individual_cadet(interface: abstractInterface) -> Union[Form, NewForm]:
    ## placeholder, not currently used
    pass


def confirm_cadet_exists(cadet_selected):
    list_of_cadets_as_str = [str(cadet) for cadet in get_list_of_cadets()]
    assert cadet_selected in list_of_cadets_as_str


def update_state_for_specific_cadet(
    interface: abstractInterface, cadet_selected: str
):
    interface.set_persistent_value(key=CADET, value=cadet_selected)


def get_specific_cadet_from_state(interface:abstractInterface) -> str:
    return interface.get_persistent_value(CADET)


def display_form_for_selected_cadet(
    cadet_selected: str,
) -> Form:
    return form_with_message_and_finished_button(cadet_selected)


def get_cadet_from_list_of_cadets(cadet_selected: str) -> Cadet:
    list_of_cadets = get_list_of_cadets()
    list_of_cadets_as_str = [str(cadet) for cadet in list_of_cadets]

    cadet_idx = list_of_cadets_as_str.index(cadet_selected)
    return list_of_cadets[cadet_idx]


