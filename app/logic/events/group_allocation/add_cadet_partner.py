from typing import Union, Tuple

from app.objects.abstract_objects.abstract_lines import ListOfLines

from app.logic.events.group_allocation.store_state import get_day_from_state_or_none
from app.backend.wa_import.convert_helm_crew_data import (
    from_partner_name_to_cadet,
    add_matched_partner_cadet_with_duplicate_registration_to_wa_mapped_data,
    get_registered_two_handed_partner_name_for_cadet_at_event,
)
from app.logic.events.cadets_at_event.track_cadet_id_in_state_when_importing import (
    get_current_cadet_id_at_event,
    clear_cadet_id_at_event,
)
from app.backend.cadets import (
    DEPRECATE_get_cadet_from_id,
    confirm_cadet_exists,
    DEPRECATE_get_cadet_given_cadet_as_str,
)

from app.logic.events.events_in_state import get_event_from_state
from app.logic.cadets.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
    DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL,
    CHECK_CADET_FOR_ME_BUTTON_LABEL,
    FINAL_CADET_ADD_BUTTON_LABEL,
    SEE_ALL_CADETS_BUTTON_LABEL,
    SEE_SIMILAR_CADETS_ONLY_LABEL,
)
from app.logic.cadets.add_cadet import add_cadet_from_form_to_data

from app.objects.cadets import Cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface


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
    )


def header_text_given_cadets(primary_cadet: Cadet, partner_cadet: Cadet) -> ListOfLines:
    header_text_start = "Following is specified as partner in form for %s: %s - select an existing cadet, or add a new one (don't forget to get their date of birth correct if BSC member)"
    return ListOfLines([header_text_start % (primary_cadet.name, partner_cadet.name)])


def post_form_add_cadet_partner(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    primary_cadet, partner_cadet = get_primary_cadet_and_partner_name(interface)
    header_text = header_text_given_cadets(primary_cadet, partner_cadet)

    if (
        last_button_pressed == DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL
        or last_button_pressed == SEE_SIMILAR_CADETS_ONLY_LABEL
        or last_button_pressed == CHECK_CADET_FOR_ME_BUTTON_LABEL
    ):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=False,
            header_text=header_text,
        )

    elif last_button_pressed == SEE_ALL_CADETS_BUTTON_LABEL:
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=True,
            header_text=header_text,
        )

    elif last_button_pressed == FINAL_CADET_ADD_BUTTON_LABEL:
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
    cadet_selected = interface.last_button_pressed()

    try:
        confirm_cadet_exists(interface=interface, cadet_selected=cadet_selected)
    except:
        raise Exception(
            "Cadet selected no longer exists - file corruption or someone deleted?",
        )

    cadet = DEPRECATE_get_cadet_given_cadet_as_str(
        cadet_selected=cadet_selected, interface=interface
    )

    return add_matched_partner_cadet_with_duplicate_registration(
        interface=interface, new_cadet=cadet
    )


def add_matched_partner_cadet_with_duplicate_registration(
    interface: abstractInterface, new_cadet: Cadet
) -> NewForm:
    primary_cadet, __ = get_primary_cadet_and_partner_name(interface)
    event = get_event_from_state(interface)
    day_or_none_if_all_days = get_day_from_state_or_none(interface)
    add_matched_partner_cadet_with_duplicate_registration_to_wa_mapped_data(
        interface=interface,
        event=event,
        day_or_none_if_all_days=day_or_none_if_all_days,
        original_cadet=primary_cadet,
        new_cadet=new_cadet,
    )
    interface.flush_cache_to_store()

    clear_cadet_id_at_event(interface)

    return return_to_allocation_pages(interface)


def return_to_allocation_pages(interface: abstractInterface) -> NewForm:
    clear_cadet_id_at_event(interface)

    return interface.get_new_display_form_for_parent_of_function(
        post_form_add_cadet_partner
    )


def get_primary_cadet_and_partner_name(
    interface: abstractInterface,
) -> Tuple[Cadet, Cadet]:
    event = get_event_from_state(interface)
    cadet_id = get_current_cadet_id_at_event(interface)
    primary_cadet = DEPRECATE_get_cadet_from_id(cadet_id=cadet_id, interface=interface)
    partner_name = get_registered_two_handed_partner_name_for_cadet_at_event(
        interface=interface, cadet=primary_cadet, event=event
    )
    partner_cadet = from_partner_name_to_cadet(partner_name)

    return primary_cadet, partner_cadet
