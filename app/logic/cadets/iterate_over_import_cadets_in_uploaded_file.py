from typing import Union

from app.OLD_backend.cadets import add_new_verified_cadet, get_cadet_given_cadet_as_str
from app.OLD_backend.wa_import.import_cadets import (
    remove_temp_file,
    get_temp_cadet_file,
    are_there_no_similar_cadets,
    does_identical_cadet_exist_in_data,
    replace_cadet_with_id_with_new_cadet_details,
)
from app.logic.shared.add_edit_cadet_form import get_cadet_from_form
from app.logic.shared.cadet_state import (
    clear_cadet_state,
    update_state_for_specific_cadet_id,
    get_cadet_id_selected_from_state,
)
from app.logic.shared.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
    checked_cadet_ok_button,
    see_similar_cadets_only_button,
    check_cadet_for_me_button,
    see_all_cadets_button,
    add_cadet_button,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.objects.cadets import Cadet
from app.objects.exceptions import NoMoreData


def begin_iteration_over_rows_in_temp_cadet_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    first_cadet = reset_temp_cadet_file_counter_to_first_value(interface)

    return process_current_cadet_in_temp_file(
        interface=interface, current_cadet=first_cadet
    )


def process_current_cadet_in_temp_file(
    interface: abstractInterface, current_cadet: Cadet
) -> Union[Form, NewForm]:
    if does_identical_cadet_exist_in_data(interface=interface, cadet=current_cadet):
        print("Identical cadet to %s already exists" % str(current_cadet))
        ### next cadet
        return next_iteration_over_rows_in_temp_cadet_file(interface)

    no_similar_cadets = are_there_no_similar_cadets(
        interface=interface, cadet=current_cadet
    )

    if no_similar_cadets:
        ##### add cadet
        print("No similar cadets to %s" % str(current_cadet))
        return process_when_cadet_to_be_added(interface=interface, cadet=current_cadet)

    ### display form to choose between similar cadets
    return interface.get_new_form_given_function(
        display_verify_adding_cadet_from_list_form
    )


def next_iteration_over_rows_in_temp_cadet_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    try:
        next_cadet = get_next_cadet_and_store(interface)
    except NoMoreData:
        return finishing_processing_file(interface)

    return process_current_cadet_in_temp_file(
        interface=interface, current_cadet=next_cadet
    )


def process_when_cadet_to_be_added(interface: abstractInterface, cadet: Cadet) -> Form:
    add_new_verified_cadet(data_layer=interface.data, cadet=cadet)
    interface.log_error("Added new cadet %s" % str(cadet))
    interface.flush_cache_to_store()

    return next_iteration_over_rows_in_temp_cadet_file(interface)




def display_verify_adding_cadet_from_list_form(interface: abstractInterface) -> Form:
    current_cadet = get_cadet_from_temp_file_and_state(interface)
    return get_add_or_select_existing_cadet_form(
        cadet=current_cadet,
        interface=interface,
        header_text=provided_header_text,
        include_final_button=False,
        see_all_cadets=False,
        extra_buttons=extra_buttons,
    )


provided_header_text = ListOfLines(
    [
        "Looks like an imported cadet is very similar to some existing cadets. Click on the existing cadet to replace with this addition (useful if date of birth is wrong), add cadet if really new, or press skip to ignore."
    ]
)
SKIP_CADET_BUTTON_LABEL = "Skip - do not add this cadet"
skip_cadet_button = Button(SKIP_CADET_BUTTON_LABEL)
extra_buttons = Line([skip_cadet_button])


def post_verify_adding_cadet_from_list_form(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if (
        checked_cadet_ok_button.pressed(last_button_pressed)
        or see_similar_cadets_only_button.pressed(last_button_pressed)
        or check_cadet_for_me_button.pressed(last_button_pressed)
    ):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=False,
            header_text=provided_header_text,
            extra_buttons=extra_buttons,
        )

    elif see_all_cadets_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=True,
            header_text=provided_header_text,
            extra_buttons=extra_buttons,
        )

    elif add_cadet_button.pressed(last_button_pressed):
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added(interface)

    elif skip_cadet_button.pressed(last_button_pressed):
        return next_iteration_over_rows_in_temp_cadet_file(interface)

    else:
        ## must be an existing cadet that has been selected
        return replace_selected_cadet_with_new_cadet(interface)


def replace_selected_cadet_with_new_cadet(interface):
    new_cadet = get_cadet_from_form(interface)
    cadet_selected_as_str = interface.last_button_pressed()
    existing_cadet = get_cadet_given_cadet_as_str(
        data_layer=interface.data, cadet_as_str=cadet_selected_as_str
    )

    replace_cadet_with_id_with_new_cadet_details(
        interface=interface, existing_cadet_id=existing_cadet.id, new_cadet=new_cadet
    )
    interface.flush_cache_to_store()

    return next_iteration_over_rows_in_temp_cadet_file(interface)


def process_form_when_verified_cadet_to_be_added(interface: abstractInterface) -> Form:
    try:
        cadet = get_cadet_from_form(interface)
    except Exception as e:
        raise Exception(
            "Problem adding cadet to data code %s CONTACT SUPPORT" % str(e),
        )

    return process_when_cadet_to_be_added(interface=interface, cadet=cadet)


def finishing_processing_file(interface: abstractInterface) -> NewForm:
    remove_temp_file()
    interface.flush_cache_to_store()
    clear_cadet_state(interface)

    return interface.get_new_display_form_for_parent_of_function(
        display_verify_adding_cadet_from_list_form
    )


### STATE


def reset_temp_cadet_file_counter_to_first_value(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file()
    first_cadet = list_of_cadets[0]

    ## We have to use underlying ID code, since we aren't dealing with the master list of cadets
    update_state_for_specific_cadet_id(interface=interface, cadet_id=first_cadet.id)

    return first_cadet


def get_next_cadet_and_store(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file()
    current_cadet_id = get_cadet_id_selected_from_state(interface)

    current_idx = list_of_cadets.index_of_id(current_cadet_id)
    next_idx = current_idx + 1

    try:
        next_cadet = list_of_cadets[next_idx]
    except IndexError:
        raise NoMoreData

    update_state_for_specific_cadet_id(interface=interface, cadet_id=next_cadet.id)

    return next_cadet


def get_cadet_from_temp_file_and_state(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file()
    current_cadet_id = get_cadet_id_selected_from_state(interface)
    current_idx = list_of_cadets.index_of_id(current_cadet_id)

    return list_of_cadets[current_idx]
