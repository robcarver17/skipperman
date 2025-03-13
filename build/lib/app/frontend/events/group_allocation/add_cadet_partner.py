from typing import Union, Tuple

from app.frontend.shared.cadet_state import get_cadet_from_state, clear_cadet_state
from app.objects.abstract_objects.abstract_buttons import ButtonBar, HelpButton, cancel_menu_button
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
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
    add_cadet_button,
)
from app.frontend.shared.add_edit_cadet_form import add_cadet_from_form_to_data

from app.objects.cadets import Cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event
from app.objects.exceptions import MissingData, missing_data
from app.backend.registration_data.cadet_registration_data import get_cadet_at_event


def display_add_cadet_partner(
    interface: abstractInterface,
) -> Form:
    primary_cadet, partner_cadet = get_primary_cadet_and_partner_name(interface)
    header_text = header_text_given_cadets(primary_cadet, partner_cadet)

    return get_add_or_select_existing_cadet_form(
        cadet=partner_cadet,
        interface=interface,
        see_all_cadets=False,
        include_final_button=False,
        header_text=header_text,
        extra_buttons=Line([cancel_menu_button])
    )


def header_text_given_cadets(primary_cadet: Cadet, partner_cadet: Cadet) -> ListOfLines:
    header_text_start = "Following is specified as partner in form for %s: %s - select an existing cadet, or add a new one"
    return ListOfLines(
        [help_button, header_text_start % (primary_cadet.name, partner_cadet.name)]
    ).add_Lines()


help_button = ButtonBar([HelpButton("help_adding_partner")])


def post_form_add_cadet_partner(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    primary_cadet, partner_cadet = get_primary_cadet_and_partner_name(interface)
    header_text = header_text_given_cadets(primary_cadet, partner_cadet)

    if cancel_menu_button.pressed(last_button_pressed):
        return return_to_allocation_pages(interface)

    if see_similar_cadets_only_button.pressed(
        last_button_pressed
    ) or check_cadet_for_me_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=False,
            header_text=header_text,
        )

    elif see_all_cadets_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=True,
            header_text=header_text,
        )

    elif add_cadet_button.pressed(last_button_pressed):
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added_as_partner(interface)

    else:
        ## must be an existing cadet that has been selected
        # no need to reset stage
        return process_form_when_existing_cadet_chosen_as_partner(interface)


def process_form_when_verified_cadet_to_be_added_as_partner(
    interface: abstractInterface,
) -> NewForm:
    try:
        cadet = add_cadet_from_form_to_data(interface)
    except Exception as e:
        raise Exception(
            "Problem adding cadet to data code %s CONTACT SUPPORT" % str(e),
        )

    return add_matched_partner_cadet_with_duplicate_registration(
        interface=interface, new_cadet=cadet
    )


def process_form_when_existing_cadet_chosen_as_partner(
    interface: abstractInterface,
) -> NewForm:
    cadet_selected_as_str = interface.last_button_pressed()

    try:
        cadet = get_cadet_from_list_of_cadets_given_str_of_cadet(
            object_store=interface.object_store, cadet_selected=cadet_selected_as_str
        )
    except:
        raise Exception(
            "Cadet selected no longer exists - file corruption or someone deleted?",
        )

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
