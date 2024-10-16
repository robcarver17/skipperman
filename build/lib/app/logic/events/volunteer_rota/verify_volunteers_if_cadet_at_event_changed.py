from typing import Union

from app.OLD_backend.wa_import.update_cadets_at_event import has_cadet_at_event_changed, mark_cadet_at_event_as_unchanged
from app.OLD_backend.volunteers.volunteer_allocation import are_any_volunteers_associated_with_cadet_at_event, \
    is_current_cadet_active_at_event
from app.frontend.events.volunteer_rota.form_elements_verify_volunteers_if_cadet_at_event_changed import *
from app.frontend.events.volunteer_rota.form_elements_verify_volunteers_if_cadet_at_event_changed import \
    get_list_of_volunteer_names_relating_to_changed_cadet

from app.frontend.events.volunteer_rota.rota_state import get_and_save_next_cadet_id_in_event_data, get_current_cadet_id_for_rota_at_event
from app.frontend.shared.events_state import get_event_from_state
from app.objects.exceptions import NoMoreData
from app.frontend.events.volunteer_rota.ENTRY1_display_main_rota_page import display_form_view_for_volunteer_rota

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.events import Event


# VOLUNTEER_ROTA_INITIALISE_LOOP_IN_VIEW_EVENT_STAGE
def display_form_volunteer_rota_check(interface: abstractInterface)-> NewForm:
    #clear_cadet_id_for_rota_at_event(interface)

    #return next_cadet_in_loop(interface)

    interface.log_error("Auto check of volunteer rota availability changes not working - needs fixing at some point")
    return goto_main_rota_form(interface)


# VOLUNTEER_ROTA_CHECK_LOOP_IN_VIEW_EVENT_STAGE
def next_cadet_in_loop(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        cadet_id = get_and_save_next_cadet_id_in_event_data(interface)
    except NoMoreData:
        ## main volunteer rota form
        return goto_main_rota_form(interface)

    return check_cadet_in_loop(interface=interface, cadet_id=cadet_id)

def goto_main_rota_form(interface:abstractInterface)-> NewForm:
    return interface.get_new_form_given_function(display_form_view_for_volunteer_rota)


def check_cadet_in_loop(interface: abstractInterface, cadet_id: str) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    cadet_has_changed = has_cadet_at_event_changed(interface=interface, cadet_id=cadet_id, event=event)

    if not cadet_has_changed:
        return next_cadet_in_loop(interface)

    return check_changed_cadet_in_loop(interface=interface, cadet_id=cadet_id, event=event)

def check_changed_cadet_in_loop(interface: abstractInterface, cadet_id: str, event: Event) -> Union[Form, NewForm]:
    current_cadet_is_active = is_current_cadet_active_at_event(interface=interface, cadet_id=cadet_id, event=event)
    any_volunteers_associated_with_cadet_at_event = are_any_volunteers_associated_with_cadet_at_event(
        interface=interface,
        cadet_id=cadet_id, event=event
                                                                                                          )

    current_cadet_is_inactive= not current_cadet_is_active

    if current_cadet_is_active and any_volunteers_associated_with_cadet_at_event:
        ## Just an availability change OR going back to active status so worth checking
        return display_form_volunteer_rota_check_changed_cadet_when_availability_changed(
            cadet_id=cadet_id,
            event=event,
            interface=interface
        )
    elif current_cadet_is_active and not any_volunteers_associated_with_cadet_at_event:
        ## status has changed from deleted/cancelled, and now we want to check to see if we have volunteers
        return flag_active_cadet_without_volunteers_and_loop_to_next_cadet(interface)

    elif current_cadet_is_inactive and any_volunteers_associated_with_cadet_at_event:
        ## status has changed to deleted/cancelled and we want to see if we will continue having volunteers
        return display_form_volunteer_rota_check_changed_cadet_when_status_changed_to_deleted_or_cancelled(
            cadet_id=cadet_id,
            event=event,
            interface=interface
        )
    elif current_cadet_is_inactive and not any_volunteers_associated_with_cadet_at_event:
        ## Status has changed to deleted/cancelled and no volunteers to worry about
        return next_cadet_in_loop(interface)
    else:
        raise Exception("Shouldn't get here")




def flag_active_cadet_without_volunteers_and_loop_to_next_cadet(interface: abstractInterface) -> Form:
    cadet_id = get_current_cadet_id_for_rota_at_event(interface)
    cadet_name = cadet_name_from_id(interface=interface, cadet_id=cadet_id)
    list_of_volunteer_names_relating_to_changed_cadet = get_list_of_volunteer_names_relating_to_changed_cadet(interface)
    if len(list_of_volunteer_names_relating_to_changed_cadet)>0:
        list_of_volunteer_names_relating_to_changed_cadet = ", ".join(list_of_volunteer_names_relating_to_changed_cadet)
        interface.log_error("Cadet %s has active registration but no volunteers added - consider manually adding volunteers: %s " %
                            (cadet_name, list_of_volunteer_names_relating_to_changed_cadet))

    event = get_event_from_state(interface)
    mark_cadet_at_event_as_unchanged(interface=interface, cadet_id=cadet_id, event=event)
    interface._save_data_store_cache()

    return next_cadet_in_loop(interface)


def post_form_volunteer_rota_check(interface: abstractInterface)-> NewForm:
    cadet_id=get_current_cadet_id_for_rota_at_event(interface)
    event = get_event_from_state(interface)

    update_type = get_type_of_form_displayed_for_volunteer_update(interface)

    if update_type==UPDATE_AVAILABLE:
        ## Just an availability change
        return post_form_volunteer_rota_check_changed_cadet_when_availability_changed(
            interface=interface,
            cadet_id=cadet_id,
            event=event
        )
    elif update_type==UPDATE_WHEN_DELETED_OR_CANCELLED:
        ## status has changed to deleted/cancelled and we want to see if we will continue having volunteers
        return post_form_volunteer_rota_check_changed_cadet_when_status_changed_to_deleted_or_cancelled(
            interface=interface,
            cadet_id=cadet_id,
            event=event
        )
    else:
        ## should never have got here, but oh well
        raise Exception("Bit weird, update type is %s for cadet id %s" % (update_type, cadet_id))


def post_form_volunteer_rota_check_changed_cadet_when_availability_changed(
        interface: abstractInterface,
        cadet_id: str,
        event: Event
) -> NewForm:
    dict_of_relevant_volunteers_with_ids = get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(interface=interface,
         cadet_id=cadet_id, event=event)
    for volunteer_id in list(dict_of_relevant_volunteers_with_ids.values()):
        modify_specific_volunteer_availability_when_cadet_changed(interface=interface, volunteer_id=volunteer_id)

    mark_cadet_at_event_as_unchanged(cadet_id=cadet_id, event=event, interface=interface)
    interface._save_data_store_cache()

    return next_cadet_in_loop(interface)


def post_form_volunteer_rota_check_changed_cadet_when_status_changed_to_deleted_or_cancelled(
        interface: abstractInterface,
        cadet_id: str,
        event: Event
) -> NewForm:
    dict_of_relevant_volunteers_with_ids = get_dict_of_relevant_volunteer_names_and_association_cadets_with_id_values(
        interface=interface,
         cadet_id=cadet_id, event=event)
    for volunteer_id in list(dict_of_relevant_volunteers_with_ids.values()):
        modify_specific_volunteer_linkage_at_event_when_cadet_changed(interface=interface, volunteer_id=volunteer_id, cadet_id=cadet_id)

    mark_cadet_at_event_as_unchanged(cadet_id=cadet_id, event=event, interface=interface)
    interface._save_data_store_cache()

    return next_cadet_in_loop(interface)


