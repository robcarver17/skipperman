from typing import Union, Tuple

from app.frontend.shared.cadet_state import get_cadet_from_state, clear_cadet_state
from app.objects.abstract_objects.abstract_buttons import  cancel_menu_button
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.backend.cadets.list_of_cadets import (
    get_cadet_from_list_of_cadets_given_str_of_cadet,
)

from app.frontend.events.group_allocation.store_state import get_day_from_state_or_none
from app.backend.cadets_at_event.add_unregistered_partner_cadet import (
    from_partner_name_to_cadet,
    add_unregistered_partner_cadet,
    get_registered_two_handed_partner_name_for_cadet_at_event,
)

from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
    see_similar_cadets_only_button,
    check_cadet_for_me_button,
    see_all_cadets_button,
    add_cadet_button, ParametersForGetOrSelectCadetForm, generic_post_response_to_add_or_select_cadet,
)
from app.frontend.shared.add_edit_cadet_form import add_cadet_from_form_to_data

from app.objects.cadets import Cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.exceptions import MissingData, missing_data
from app.backend.registration_data.cadet_registration_data import get_cadet_at_event


def display_add_cadet_partner(
    interface: abstractInterface,
) -> Form:
    primary_cadet, partner_cadet = get_primary_cadet_and_partner_name(interface)
    parameters = get_parameters_for_form_given_cadets(
        primary_cadet=primary_cadet,
        partner_cadet=partner_cadet
    )
    return get_add_or_select_existing_cadet_form(
        cadet=partner_cadet,
        interface=interface,
        parameters=parameters
    )


def header_text_given_cadets(primary_cadet: Cadet, partner_cadet: Cadet) -> ListOfLines:
    header_text_start = "Following is specified as partner in form for %s: %s - select an existing cadet, or add a new one"
    return ListOfLines(
        [header_text_start % (primary_cadet.name, partner_cadet.name)]
    ).add_Lines()

def get_parameters_for_form_given_cadets(primary_cadet: Cadet, partner_cadet: Cadet):
    header_text = header_text_given_cadets(primary_cadet, partner_cadet)
    parameters = ParametersForGetOrSelectCadetForm(
        help_string='help_adding_partner',
        header_text=header_text,
        cancel_button=True
    )

    return parameters

def post_form_add_cadet_partner(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    primary_cadet, partner_cadet = get_primary_cadet_and_partner_name(interface)
    parameters = get_parameters_for_form_given_cadets(
        primary_cadet=primary_cadet,
        partner_cadet=partner_cadet
    )
    result = generic_post_response_to_add_or_select_cadet(
        interface=interface,
        parameters=parameters
    )
    if result.is_form:
        return result.form

    elif result.cancel:
        return return_to_allocation_pages(interface)


    elif result.is_cadet:
        cadet = result.cadet
        assert type(cadet) is Cadet
        return process_form_when_cadet_chosen_as_partner(
            interface=interface,
            cadet=cadet
        )
    else:
        raise Exception("Can't handle result %s" % str(result))



def process_form_when_cadet_chosen_as_partner(
    interface: abstractInterface,
        cadet: Cadet
) -> NewForm:

    check_if_registered = is_cadet_already_registered(interface=interface, new_cadet=cadet)
    if check_if_registered:
        interface.log_error("%s is already attending the event - add them as a two handed partner from the dropdown" % cadet.name)
        return return_to_allocation_pages(interface)

    return add_matched_partner_cadet_with_duplicate_registration(
        interface=interface, new_cadet=cadet
    )


def add_matched_partner_cadet_with_duplicate_registration(
    interface: abstractInterface, new_cadet: Cadet
) -> NewForm:

    primary_cadet, __ = get_primary_cadet_and_partner_name(interface)
    event = get_event_from_state(interface)
    day_or_none_if_all_days = get_day_from_state_or_none(interface)
    try:
        add_unregistered_partner_cadet(
            object_store=interface.object_store,
            event=event,
            day_or_none_if_all_days=day_or_none_if_all_days,
            original_cadet=primary_cadet,
            new_cadet=new_cadet,
        )
        interface.flush_cache_to_store()
    except MissingData:
        interface.log_error(
            "Can't add new partner cadet- old event data has probably been cleaned"
        )

    return return_to_allocation_pages(interface)

def is_cadet_already_registered(interface: abstractInterface, new_cadet: Cadet):
    event = get_event_from_state(interface)
    cadet_at_event = get_cadet_at_event(object_store=interface.object_store, event=event, cadet=new_cadet, default=missing_data)

    return cadet_at_event is not missing_data

def return_to_allocation_pages(interface: abstractInterface) -> NewForm:
    clear_cadet_state(interface)

    return interface.get_new_display_form_for_parent_of_function(
        post_form_add_cadet_partner
    )


def get_primary_cadet_and_partner_name(
    interface: abstractInterface,
) -> Tuple[Cadet, Cadet]:
    event = get_event_from_state(interface)
    primary_cadet = get_cadet_from_state(interface)
    partner_name = get_registered_two_handed_partner_name_for_cadet_at_event(
        object_store=interface.object_store, cadet=primary_cadet, event=event
    )
    partner_cadet = from_partner_name_to_cadet(partner_name)

    return primary_cadet, partner_cadet
