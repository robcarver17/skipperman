from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    Button,
    ButtonBar,
    CANCEL_BUTTON_LABEL,
)

from app.frontend.shared.events_state import (
    get_event_from_state,
)

from app.frontend.form_handler import initial_state_form

from app.OLD_backend.events import (
    DEPRECATE_get_sorted_list_of_events,
    get_event_from_list_of_events_given_event_description,
)
from app.backend.events.list_of_events import confirm_event_exists_given_description_REFACTOR
from app.OLD_backend.wa_import.map_wa_fields import (
    is_wa_field_mapping_setup_for_event,
    get_field_mapping_for_event,
    DEPRECATE_write_field_mapping_for_event,
)
from app.objects.events import ListOfEvents, SORT_BY_START_DSC, Event


def display_form_for_clone_event_field_mapping(interface: abstractInterface):
    current_event = get_event_from_state(interface)
    list_of_events_with_buttons = display_list_of_events_with_field_mapping_buttons(
        exclude_event=current_event, interface=interface
    )
    if len(list_of_events_with_buttons) == 0:
        return ListOfLines(["No other events exist with mapping setup"])
    else:
        return ListOfLines(
            [
                ButtonBar([cancel_menu_button]),
                Line(
                    "Choose event to clone event field mapping for %s"
                    % str(current_event)
                ),
                _______________,
                list_of_events_with_buttons,
            ]
        )


def display_list_of_events_with_field_mapping_buttons(
    interface: abstractInterface, exclude_event: Event
) -> ListOfLines:
    list_of_events = get_list_of_events_with_field_mapping(
        interface=interface, exclude_event=exclude_event
    )
    list_of_event_descriptions = list_of_events.list_of_event_descriptions
    list_with_buttons = [
        Line(Button(event_description))
        for event_description in list_of_event_descriptions
    ]

    return ListOfLines(list_with_buttons)


def get_list_of_events_with_field_mapping(
    interface: abstractInterface, exclude_event: Event
) -> ListOfEvents:
    list_of_events = DEPRECATE_get_sorted_list_of_events(
        interface=interface, sort_by=SORT_BY_START_DSC
    )
    list_of_events = [
        event
        for event in list_of_events
        if is_wa_field_mapping_setup_for_event(interface=interface, event=event)
    ]
    list_of_events = [
        event for event in list_of_events if not event.id == exclude_event.id
    ]

    return ListOfEvents(list_of_events)


def post_form_for_clone_event_field_mapping(interface: abstractInterface):
    if interface.last_button_pressed() == CANCEL_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(
            display_form_for_clone_event_field_mapping
        )

    event_description_selected = interface.last_button_pressed()
    current_event = get_event_from_state(interface)
    try:
        confirm_event_exists_given_description_REFACTOR(
            interface=interface, event_description=event_description_selected
        )
    except:
        interface.log_error(
            "Event %s no longer in list- someone else has deleted or file corruption?"
            % event_description_selected
        )
        return initial_state_form

    event = get_event_from_list_of_events_given_event_description(
        interface=interface, event_description=event_description_selected
    )
    try:
        mapping = get_field_mapping_for_event(interface=interface, event=event)
        assert len(mapping) > 0
    except:
        interface.log_error(
            "Event %s has no mapping set up, or mapping file is corrupted - choose another event"
            % event_description_selected
        )
        return initial_state_form

    DEPRECATE_write_field_mapping_for_event(
        interface=interface, event=current_event, new_mapping=mapping
    )
    interface._save_data_store_cache()

    return form_with_message_and_finished_button(
        "Mapping copied from event %s to %s"
        % (event_description_selected, str(current_event)),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_for_clone_event_field_mapping,
    )
