from typing import Union

from app.backend.cadets.add_edit_cadet import add_new_verified_cadet

from app.backend.cadets.iterate_over_membership_list import set_all_current_members_to_temporary_unconfirmed, \
    confirm_cadet_is_member, \
    set_all_temporary_unconfirmed_members_to_lapsed_and_return_list,  \
    set_all_user_unconfirmed_members_to_non_members_and_return_list
from app.backend.cadets.import_membership_list import remove_temp_file_with_list_of_cadet_members, \
    get_temp_cadet_file_list_of_memberships
from app.backend.cadets.list_of_cadets import are_there_no_similar_cadets, \
    get_cadet_from_list_of_cadets_given_str_of_cadet, get_matching_cadet
from app.frontend.shared.add_edit_cadet_form import get_cadet_from_form

from app.frontend.shared.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
    see_similar_cadets_only_button,
    check_cadet_for_me_button,
    see_all_cadets_button,
    add_cadet_button,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines

from app.objects.cadets import Cadet
from app.objects.membership_status import current_member, system_unconfirmed_member, describe_status
from app.objects.exceptions import NoMoreData, MissingData


def begin_iteration_over_rows_in_temp_cadet_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    set_all_current_members_to_temporary_unconfirmed(object_store=interface.object_store)
    first_cadet = reset_temp_cadet_file_counter_to_first_value(interface)

    return process_current_cadet_in_temp_file(
        interface=interface, current_cadet=first_cadet
    )


def process_current_cadet_in_temp_file(
    interface: abstractInterface, current_cadet: Cadet
) -> Union[Form, NewForm]:
    object_store = interface.object_store
    try:
        cadet_in_data = get_matching_cadet(object_store=object_store, cadet=current_cadet, exact_match_required=True)
        print("Identical cadet to %s already exists " % str(cadet_in_data))
        mark_existing_cadet_as_member_and_log(interface=interface, cadet=cadet_in_data)
        return next_iteration_over_rows_in_temp_cadet_file(interface)

    except MissingData:
        print("No exact matching cadet found for %s" % current_cadet)
        return process_current_cadet_in_temp_file_when_no_exact_match(interface=interface, current_cadet=current_cadet)

def process_current_cadet_in_temp_file_when_no_exact_match(
        interface: abstractInterface, current_cadet: Cadet
) -> Union[Form, NewForm]:

    no_similar_cadets = are_there_no_similar_cadets(
        object_store=interface.object_store, cadet=current_cadet
    )

    if no_similar_cadets:
        ##### add cadet
        print("No similar cadets to %s" % str(current_cadet))
        current_cadet.membership_status = current_member  ## should be set already, but just in case
        return process_when_cadet_to_be_added_from_membership_list(interface=interface, cadet=current_cadet)

    ### display form to choose between similar cadets
    return interface.get_new_form_given_function(
        display_verify_adding_cadet_from_list_form
    )

def mark_existing_cadet_as_member_and_log(interface: abstractInterface, cadet: Cadet):
    if cadet.membership_status == system_unconfirmed_member:
        ## don't log, too much spam otherwise
        print("Cadet %s was member, still member" % str(cadet))
    else:
        ## genuine change in state
        interface.log_error("Cadet %s was %s, confirming as member" % (cadet.name, describe_status(cadet.membership_status)))

    confirm_cadet_is_member(object_store=interface.object_store, cadet=cadet)


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


def process_when_cadet_to_be_added_from_membership_list(interface: abstractInterface, cadet: Cadet) -> Form:
    add_new_verified_cadet(object_store=interface.object_store, cadet=cadet)
    interface.log_error("Added new cadet from membership list %s" % str(cadet))
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
    )


provided_header_text = ListOfLines(
    [
        "Looks like a cadet in the membership list is very similar to some existing cadets. Click on the existing cadet that matches this one (this will verify they are a member), or add cadet if really a new member,"
    ]
)


def post_verify_adding_cadet_from_list_form(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if (
        see_similar_cadets_only_button.pressed(last_button_pressed)
        or check_cadet_for_me_button.pressed(last_button_pressed)
    ):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=False,
            header_text=provided_header_text,
        )

    elif see_all_cadets_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=True,
            header_text=provided_header_text,
        )

    elif add_cadet_button.pressed(last_button_pressed):
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added(interface)

    else:
        ## must be an existing cadet that has been selected
        return confirm_selected_cadet_is_member(interface)


def confirm_selected_cadet_is_member(interface):

    cadet_selected_as_str = interface.last_button_pressed()
    existing_cadet = get_cadet_from_list_of_cadets_given_str_of_cadet(
        object_store=interface.object_store, cadet_selected=cadet_selected_as_str
    )

    mark_existing_cadet_as_member_and_log(interface=interface, cadet=existing_cadet)

    interface.flush_cache_to_store()

    return next_iteration_over_rows_in_temp_cadet_file(interface)


def process_form_when_verified_cadet_to_be_added(interface: abstractInterface) -> Form:
    try:
        cadet = get_cadet_from_form(interface)
    except Exception as e:
        raise Exception(
            "Problem adding cadet to data code %s CONTACT SUPPORT" % str(e),
        )

    return process_when_cadet_to_be_added_from_membership_list(interface=interface, cadet=cadet)



### STATE


def reset_temp_cadet_file_counter_to_first_value(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file_list_of_memberships()
    first_cadet = list_of_cadets[0]

    ## We have to use underlying ID code, since we aren't dealing with the master list of cadets
    update_state_for_specific_cadet_id_in_temporary_file(interface=interface, cadet_id=first_cadet.id)

    return first_cadet


def get_next_cadet_and_store(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file_list_of_memberships()
    current_cadet_id = get_cadet_id_in_temporary_file_from_state(interface=interface)

    current_idx = list_of_cadets.index_of_id(current_cadet_id)
    next_idx = current_idx + 1

    try:
        next_cadet = list_of_cadets[next_idx]
    except IndexError:
        raise NoMoreData

    update_state_for_specific_cadet_id_in_temporary_file(interface=interface, cadet_id=next_cadet.id)

    return next_cadet


def get_cadet_id_in_temporary_file_from_state(interface: abstractInterface):
    return interface.get_persistent_value(TEMP_CADET_ID)

def update_state_for_specific_cadet_id_in_temporary_file(interface: abstractInterface, cadet_id: str):
    interface.set_persistent_value(key=TEMP_CADET_ID, value=cadet_id)

def clear_state_for_specific_cadet_id_in_temporary_file(interface: abstractInterface):
    interface.clear_persistent_value(TEMP_CADET_ID)


def get_cadet_from_temp_file_and_state(interface: abstractInterface) -> Cadet:
    list_of_cadets = get_temp_cadet_file_list_of_memberships()
    current_cadet_id = get_cadet_id_in_temporary_file_from_state(interface=interface)
    current_idx = list_of_cadets.index_of_id(current_cadet_id)

    return list_of_cadets[current_idx]

TEMP_CADET_ID = "temp_cadet_id"

## FINISHED

def finishing_processing_file(interface: abstractInterface) -> NewForm:
    remove_temp_file_with_list_of_cadet_members()
    set_all_unconfirmed_members_to_lapsed_and_log(interface)

    interface.flush_cache_to_store()
    clear_state_for_specific_cadet_id_in_temporary_file(interface)

    return interface.get_new_display_form_for_parent_of_function(
        display_verify_adding_cadet_from_list_form
    )

def set_all_unconfirmed_members_to_lapsed_and_log(interface: abstractInterface):
    lapsed_members = set_all_temporary_unconfirmed_members_to_lapsed_and_return_list(object_store=interface.object_store)
    for cadet in lapsed_members:
        interface.log_error("Cadet %s is not in membership list and has been marked as lapsed: no longer a cadet member" % cadet)

    not_members =set_all_user_unconfirmed_members_to_non_members_and_return_list(object_store=interface.object_store)
    for cadet in not_members:
        interface.log_error("Cadet %s is not in membership list and has been marked as a non member" % cadet)
