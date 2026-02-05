from typing import Callable, Union

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    add_new_cadet_manually_to_event,
)
from app.backend.registration_data.cadet_registration_data import get_cadet_at_event
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
    ParametersForGetOrSelectCadetForm,
    generic_post_response_to_add_or_select_cadet,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_text import bold
from app.objects.cadets import Cadet, default_cadet
from app.objects.utilities.exceptions import missing_data


def display_add_unregistered_form(
    interface: abstractInterface,
) -> Form:
    return get_add_or_select_existing_cadet_form(
        interface=interface, cadet=default_cadet, parameters=get_or_select_parameters
    )


def post_form_add_unregistered_cadet(
    interface: abstractInterface, calling_function: Callable
) -> Union[Form, NewForm]:
    result = generic_post_response_to_add_or_select_cadet(
        interface=interface, parameters=get_or_select_parameters
    )
    if result.is_form:
        return result.form

    elif result.is_button:
        if result.button_pressed == cancel_button:
            return return_to_allocation_pages(
                interface=interface, calling_function=calling_function
            )
        else:
            return button_error_and_back_to_initial_state_form(interface)

    elif result.is_cadet:
        cadet = result.cadet
        return add_cadet_to_event_if_unregistered_and_return_form(
            interface=interface, cadet=cadet, calling_function=calling_function
        )


def add_cadet_to_event_if_unregistered_and_return_form(
    interface: abstractInterface, cadet: Cadet, calling_function: Callable
) -> NewForm:
    check_if_registered = is_cadet_already_registered(
        interface=interface, new_cadet=cadet
    )
    if check_if_registered:
        interface.log_error(
            "%s is already attending the event - cannot be registered again manually"
            % cadet.name
        )
        return return_to_allocation_pages(
            interface=interface, calling_function=calling_function
        )

    return add_cadet_to_event_and_return_form(
        interface=interface, cadet=cadet, calling_function=calling_function
    )


def add_cadet_to_event_and_return_form(
    interface: abstractInterface, cadet: Cadet, calling_function: Callable
) -> NewForm:
    event = get_event_from_state(interface)

    
    add_new_cadet_manually_to_event(
        interface=interface, event=event, new_cadet=cadet
    )

    interface.clear()

    return return_to_allocation_pages(
        interface=interface, calling_function=calling_function
    )


def is_cadet_already_registered(interface: abstractInterface, new_cadet: Cadet):
    event = get_event_from_state(interface)
    cadet_at_event = get_cadet_at_event(
        object_store=interface.object_store,
        event=event,
        cadet=new_cadet,
        default=missing_data,
    )

    return cadet_at_event is not missing_data


def return_to_allocation_pages(
    interface: abstractInterface, calling_function: Callable
) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(calling_function)


cancel_button = Button("Cancel")
header_text_for_adding_cadets = ListOfLines(
    [
        "Add a new cadet or choose an existing cadet to register at event",
        bold(
            "DO NOT USE for paid events, unless they will DEFINITELY BE REGISTERED or HAVE BEEN registered in Wild Apricot."
        ),
    ]
).add_Lines()

get_or_select_parameters = parameters = ParametersForGetOrSelectCadetForm(
    header_text=header_text_for_adding_cadets,
    help_string="manually_adding_a_sailor",
    extra_buttons=[cancel_button],
)
