from typing import Callable, Union

from app.backend.cadets.list_of_cadets import get_cadet_from_list_of_cadets_given_str_of_cadet
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import add_new_cadet_manually_to_event
from app.backend.registration_data.cadet_registration_data import get_cadet_at_event
from app.frontend.shared.add_edit_cadet_form import add_cadet_from_form_to_data
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.get_or_select_cadet_forms import get_add_or_select_existing_cadet_form, \
    see_similar_cadets_only_button, check_cadet_for_me_button, see_all_cadets_button, add_cadet_button
from app.objects.abstract_objects.abstract_buttons import cancel_menu_button, ButtonBar, HelpButton
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.cadets import Cadet
from app.objects.exceptions import missing_data


def display_add_unregistered_form(
    interface: abstractInterface,
) -> Form:

    return get_add_or_select_existing_cadet_form(
        interface=interface,
        see_all_cadets=False,
        include_final_button=False,
        header_text=header_text_for_adding_cadets,
        extra_buttons=Line([cancel_menu_button])
    )


def post_form_add_unregistered_cadet(
    interface: abstractInterface,
        calling_function: Callable
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button_pressed):
        return return_to_allocation_pages(interface=interface, calling_function=calling_function)

    if see_similar_cadets_only_button.pressed(
        last_button_pressed
    ) or check_cadet_for_me_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=False,
            header_text=header_text_for_adding_cadets,
            extra_buttons=Line([cancel_menu_button])

        )

    elif see_all_cadets_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=True,
            header_text=header_text_for_adding_cadets,
        extra_buttons=Line([cancel_menu_button])

        )

    elif add_cadet_button.pressed(last_button_pressed):
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added_to_event(interface, calling_function=calling_function)

    else:
        ## must be an existing cadet that has been selected
        # no need to reset stage
        return process_form_when_existing_cadet_to_be_added_to_event(interface, calling_function=calling_function)


def process_form_when_verified_cadet_to_be_added_to_event(
    interface: abstractInterface,
        calling_function: Callable

) -> NewForm:
    try:
        cadet = add_cadet_from_form_to_data(interface)
    except Exception as e:
        raise Exception(
            "Problem adding cadet to data code %s CONTACT SUPPORT" % str(e),
        )

    return add_cadet_to_event_if_unregistered_and_return_form(interface=interface, cadet=cadet, calling_function=calling_function)


def process_form_when_existing_cadet_to_be_added_to_event(
    interface: abstractInterface,
        calling_function: Callable
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

    return add_cadet_to_event_if_unregistered_and_return_form(interface=interface, cadet=cadet, calling_function=calling_function)


def add_cadet_to_event_if_unregistered_and_return_form(
    interface: abstractInterface,
        cadet: Cadet,
        calling_function: Callable
) -> NewForm:

    check_if_registered = is_cadet_already_registered(interface=interface, new_cadet=cadet)
    if check_if_registered:
        interface.log_error("%s is already attending the event - cannot be registered again manually" % cadet.name)
        return return_to_allocation_pages(interface=interface, calling_function=calling_function)

    return add_cadet_to_event_and_return_form(interface=interface, cadet=cadet, calling_function=calling_function)


def add_cadet_to_event_and_return_form(
    interface: abstractInterface,
        cadet: Cadet,
        calling_function: Callable
) -> NewForm:

    event = get_event_from_state(interface)

    add_new_cadet_manually_to_event(
        object_store=interface.object_store, event=event, new_cadet=cadet
    )

    interface.flush_cache_to_store()

    return return_to_allocation_pages(interface=interface, calling_function=calling_function)


def is_cadet_already_registered(interface: abstractInterface, new_cadet: Cadet):
    event = get_event_from_state(interface)
    cadet_at_event = get_cadet_at_event(object_store=interface.object_store, event=event, cadet=new_cadet, default=missing_data)

    return cadet_at_event is not missing_data


def return_to_allocation_pages(interface: abstractInterface, calling_function: Callable) -> NewForm:

    return interface.get_new_display_form_for_parent_of_function(
        calling_function
    )


header_text_for_adding_cadets = ListOfLines(["Add a new cadet or choose an existing cadet to register at event", "Do not use for paid events, unless they will also be registered in Wild Apricot."])
help_button = ButtonBar([HelpButton("manually_adding_a_sailor")])
