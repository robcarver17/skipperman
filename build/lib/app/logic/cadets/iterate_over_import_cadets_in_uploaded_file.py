from typing import Union

from app.backend.cadets import add_new_verified_cadet, \
    get_cadet_from_list_of_cadets
from app.backend.wa_import.import_cadets import remove_temp_file, get_current_cadet_from_temp_file, get_temp_cadet_file, \
    are_there_no_similar_cadets, does_identical_cadet_exist_in_data, replace_cadet_with_id_with_new_cadet_details
from app.logic.cadets.add_cadet import  get_cadet_from_form
from app.logic.cadets.cadet_state_storage import update_state_for_specific_cadet, get_cadet_id_selected_from_state, \
    clear_cadet_state
from app.logic.events.cadets_at_event.get_or_select_cadet_forms import get_add_or_select_existing_cadet_form
from app.logic.events.constants import DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL, SEE_SIMILAR_CADETS_ONLY_LABEL, \
    CHECK_CADET_FOR_ME_BUTTON_LABEL, SEE_ALL_CADETS_BUTTON_LABEL, FINAL_CADET_ADD_BUTTON_LABEL
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.objects.cadets import Cadet
from app.objects.constants import NoMoreData


def begin_iteration_over_rows_in_temp_cadet_file(interface: abstractInterface) -> Union[Form, NewForm]:
    cadet_id = reset_temp_cadet_file_id_to_first_value(interface)

    return process_current_cadet_id_in_temp_file(interface=interface, cadet_id =cadet_id )


def process_current_cadet_id_in_temp_file(interface: abstractInterface, cadet_id: str) -> Union[Form, NewForm]:
    current_cadet = get_current_cadet_from_temp_file(cadet_id)
    if does_identical_cadet_exist_in_data(interface=interface, cadet=current_cadet):
        print("Identical cadet to %s already exists" % str(current_cadet))
        ### next cadet
        return next_iteration_over_rows_in_temp_cadet_file(interface)

    no_similar_cadets = are_there_no_similar_cadets(interface=interface, cadet=current_cadet)

    if no_similar_cadets:
        ##### add cadet
        print("No similar cadets to %s" % str(current_cadet))
        return process_when_cadet_to_be_added(interface=interface, cadet=current_cadet)

    ### display form to choose between similar cadets
    return interface.get_new_form_given_function(display_verify_adding_cadet_from_list_form)


def next_iteration_over_rows_in_temp_cadet_file(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        cadet_id = get_next_cadet_id_and_store(interface)
    except NoMoreData:
        return finishing_processing_file(interface)

    return process_current_cadet_id_in_temp_file(interface=interface, cadet_id=cadet_id)


def process_when_cadet_to_be_added(interface: abstractInterface, cadet: Cadet)-> Form:
    add_new_verified_cadet(interface=interface, cadet=cadet)
    interface.log_error("Added new cadet %s"% str(cadet))
    interface.save_stored_items()

    return next_iteration_over_rows_in_temp_cadet_file(interface)

SKIP_CADET_BUTTON_LABEL = "Skip - do not add this cadet"

def display_verify_adding_cadet_from_list_form(interface: abstractInterface) -> Form:
    cadet_id = get_cadet_id_selected_from_state(interface)
    current_cadet = get_current_cadet_from_temp_file(cadet_id)
    return get_add_or_select_existing_cadet_form(
        cadet=current_cadet,
        interface=interface,
        header_text=provided_header_text,
        include_final_button=False,
        see_all_cadets=False,
        extra_buttons=extra_buttons
    )

provided_header_text=ListOfLines(["Looks like an imported cadet is very similar to some existing cadets. Click on the existing cadet to replace with this addition (useful if date of birth is wrong), add cadet if really new, or press skip to ignore."])
extra_buttons = Line([Button(SKIP_CADET_BUTTON_LABEL)])

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
            header_text=provided_header_text,
            extra_buttons=extra_buttons
        )

    elif last_button_pressed == SEE_ALL_CADETS_BUTTON_LABEL:
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface, include_final_button=True, see_all_cadets=True,
            header_text = provided_header_text,
            extra_buttons=extra_buttons
        )

    elif last_button_pressed == FINAL_CADET_ADD_BUTTON_LABEL:
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added(interface)

    elif last_button_pressed == SKIP_CADET_BUTTON_LABEL:
        return next_iteration_over_rows_in_temp_cadet_file(interface)

    else:
        ## must be an existing cadet that has been selected
        return replace_selected_cadet_with_new_cadet(interface)

def replace_selected_cadet_with_new_cadet(interface):
    new_cadet = get_cadet_from_form(interface)
    cadet_selected = interface.last_button_pressed()
    existing_cadet = get_cadet_from_list_of_cadets(interface=interface, cadet_selected=cadet_selected)

    replace_cadet_with_id_with_new_cadet_details(interface=interface, existing_cadet_id = existing_cadet.id, new_cadet=new_cadet)
    interface.save_stored_items()

    return next_iteration_over_rows_in_temp_cadet_file(interface)


def process_form_when_verified_cadet_to_be_added(interface: abstractInterface) -> Form:
    try:
        cadet = get_cadet_from_form(interface)
    except Exception as e:
        raise Exception(
            "Problem adding cadet to data code %s CONTACT SUPPORT" % str(e),
        )

    return process_when_cadet_to_be_added(interface=interface, cadet=cadet)



def finishing_processing_file(interface: abstractInterface)-> NewForm:
    remove_temp_file()
    interface.clear_stored_items()
    clear_cadet_state(interface)

    return interface.get_new_display_form_for_parent_of_function(display_verify_adding_cadet_from_list_form)



### STATE

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
    except IndexError:
        raise NoMoreData

    update_state_for_specific_cadet(interface=interface, cadet_id_selected=new_id)

    return new_id



