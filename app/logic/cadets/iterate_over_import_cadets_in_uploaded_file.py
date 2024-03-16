import os
from typing import Union

import pandas as pd

from app.backend.data.cadets import get_list_of_all_cadets, add_new_verified_cadet
from app.backend.wa_import.load_wa_file import get_staged_adhoc_filename
from app.data_access.csv.generic_csv_data import read_object_of_type
from app.logic.cadets.cadet_state_storage import update_state_for_specific_cadet, get_cadet_id_selected_from_state
from app.logic.events.cadets_at_event.get_or_select_cadet_forms import get_add_or_select_existing_cadet_form
from app.logic.events.constants import DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL, SEE_SIMILAR_CADETS_ONLY_LABEL, \
    CHECK_CADET_FOR_ME_BUTTON_LABEL, SEE_ALL_CADETS_BUTTON_LABEL, FINAL_CADET_ADD_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.constants import NoMoreData, missing_data

FIRST_NAME_IN_WA_FILE = 'First name'
SURNAME_IN_WA_FILE = 'Last name'
DOB_IN_WA_FILE = 'Date of Birth'


def cadet_from_row_in_imported_list(cadet_row: pd.Series, id: int) -> Cadet:
    first_name = cadet_row[FIRST_NAME_IN_WA_FILE]
    surname = cadet_row[SURNAME_IN_WA_FILE]
    dob = cadet_row[DOB_IN_WA_FILE]

    return Cadet(first_name=first_name, surname=surname, date_of_birth=dob.date(), id=str(id))


def begin_iteration_over_rows_in_temp_cadet_file(interface: abstractInterface) -> Union[Form, NewForm]:
    cadet_id = reset_temp_cadet_file_id_to_first_value(interface)

    return process_current_cadet_id_in_temp_file(interface=interface, cadet_id =cadet_id )


def next_iteration_over_rows_in_temp_cadet_file(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        cadet_id = get_next_cadet_id_and_store(interface)
    except NoMoreData:
        return finishing_processing_file(interface)

    return process_current_cadet_id_in_temp_file(interface=interface, cadet_id=cadet_id)


def process_current_cadet_id_in_temp_file(interface: abstractInterface, cadet_id: str) -> Union[Form, NewForm]:
    current_cadet = get_current_cadet_from_temp_file(cadet_id)
    if does_identical_cadet_exist_in_data(current_cadet):
        ### next cadet
        return next_iteration_over_rows_in_temp_cadet_file(interface)

    no_similar_cadets = are_there_no_similar_cadets(current_cadet)

    if no_similar_cadets:
        ##### add cadet
        return process_when_cadet_to_be_added(interface=interface, cadet=current_cadet)

    ### display form to choose between similar cadets
    return display_verify_adding_cadet_from_list_form(interface=interface, cadet=current_cadet)

def process_when_cadet_to_be_added(interface: abstractInterface, cadet: Cadet)-> Form:
    print("Adding new cadet %s" % current_cadet)
    add_new_verified_cadet(current_cadet)
    return next_iteration_over_rows_in_temp_cadet_file(interface)


def display_verify_adding_cadet_from_list_form(cadet: Cadet, interface: abstractInterface) -> Form:
    return get_add_or_select_existing_cadet_form(
        cadet=cadet,
        interface=interface,
        header_text=provided_header_text,
        include_final_button=False,
        see_all_cadets=False
    )

provided_header_text="Looks like an imported cadet is very similar to some existing cadets. Click on the existing cadet to ignore this addition, or add cadet if really new."

def post_verify_adding_cadet_from_list_form(    interface: abstractInterface,
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()
    if (
        last_button_pressed == DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL
        or last_button_pressed == SEE_SIMILAR_CADETS_ONLY_LABEL
        or last_button_pressed == CHECK_CADET_FOR_ME_BUTTON_LABEL
    ):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface, include_final_button=True, see_all_cadets=False,
            header_text=provided_header_text
        )

    elif last_button_pressed == SEE_ALL_CADETS_BUTTON_LABEL:
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface, include_final_button=True, see_all_cadets=True,
            header_text = provided_header_text
        )

    elif last_button_pressed == FINAL_CADET_ADD_BUTTON_LABEL:
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added(interface)

    else:
        ## must be an existing cadet that has been selected
        # no need to reset stage
        return process_form_when_existing_cadet_chosen(interface)


def process_form_when_verified_cadet_to_be_added(interface: abstractInterface) -> Form:
    try:
        cadet = add_cadet_from_form_to_data(interface)
    except Exception as e:
        raise Exception(
            "Problem adding cadet to data code %s CONTACT SUPPORT" % str(e),
        )

    return process_row_when_cadet_matched(interface=interface, cadet=cadet)


def are_there_no_similar_cadets(cadet: Cadet):
    return len(get_similar_cadets(cadet))==0

def get_similar_cadets(cadet: Cadet):
    all_existing_cadets = get_list_of_all_cadets()
    similar_cadets = all_existing_cadets.similar_cadets(cadet)

    return similar_cadets


def does_identical_cadet_exist_in_data(cadet: Cadet):
    all_existing_cadets = get_list_of_all_cadets()
    matching = all_existing_cadets.matching_cadet(cadet, exact_match_required=True)
    no_matching = matching is missing_data

    return not no_matching


def get_current_cadet_from_temp_file(cadet_id: str) -> Cadet:
    temp_file = get_temp_cadet_file()
    return temp_file.object_with_id(cadet_id)


def get_temp_cadet_file() -> ListOfCadets:
    return read_object_of_type(ListOfCadets, temp_list_of_cadets_file_name)


def reset_temp_cadet_file_id_to_first_value(interface: abstractInterface):
    list_of_cadets = get_temp_cadet_file()
    first_id = list_of_cadets.list_of_ids[0]

    update_state_for_specific_cadet(interface=interface, cadet_id_selected=first_id)

    return first_id


def get_next_cadet_id_and_store(interface: abstractInterface):
    list_of_cadets = get_temp_cadet_file()
    list_of_ids = list_of_cadets.list_of_ids
    current_id = get_cadet_id_selected_from_state(interface)

    current_idx = list_of_ids.index(current_id)
    next_idx = current_idx+1

    try:
        new_id = list_of_ids[next_idx]
    except:
        raise NoMoreData

    update_state_for_specific_cadet(interface=interface, cadet_id_selected=new_id)

    return new_id


def finishing_processing_file(interface: abstractInterface):
    remove_temp_file()
    return interface.get_new_display_form_for_parent_of_function(display_verify_adding_cadet_from_list_form)


def remove_temp_file():
    os.remove(temp_list_of_cadets_file_name)


temp_list_of_cadets_file_name = get_staged_adhoc_filename('list_of_cadets')
