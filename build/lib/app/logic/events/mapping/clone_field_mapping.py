from app.backend.read_and_write_mapping_files import (
    get_field_mapping_for_event,
    write_field_mapping_for_event,
)
from app.logic.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.logic.events.view_events import display_list_of_events_with_buttons
from app.objects.abstract_objects.abstract_form import (
    Form,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import cancel_button
from app.logic.events.events_in_state import get_event_from_state, get_event_from_list_of_events, confirm_event_exists
from app.logic.abstract_logic_api import initial_state_form


def display_form_for_clone_event_field_mapping(interface: abstractInterface):
    list_of_events_with_buttons = display_list_of_events_with_buttons()

    contents_of_form = ListOfLines(
        [
            cancel_button,
            "Choose event to clone",
            _______________,
            list_of_events_with_buttons,
        ]
    )

    return Form(contents_of_form)


def post_form_for_clone_event_field_mapping(interface: abstractInterface):
    event_name_selected = interface.last_button_pressed()
    current_event = get_event_from_state(interface)
    try:
        confirm_event_exists(event_name_selected)
    except:
        interface.log_error(
            "Event %s no longer in list- someone else has deleted or file corruption?"
            % event_name_selected
        )
        return initial_state_form

    event = get_event_from_list_of_events(event_name_selected)
    try:
        mapping = get_field_mapping_for_event(event=event)
        assert len(mapping)>0
    except:
        interface.log_error(
            "Event %s has no mapping set up, or mapping file is corrupted - choose another event"
            % event_name_selected
        )
        return initial_state_form

    write_field_mapping_for_event(event=current_event, new_mapping=mapping)

    return form_with_message_and_finished_button(
        "Mapping copied from event %s to %s"
        % (event_name_selected, str(current_event)),
        interface=interface,
    )
