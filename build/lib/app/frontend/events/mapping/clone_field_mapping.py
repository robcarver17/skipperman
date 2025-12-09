from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,

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
    HelpButton,
)

from app.frontend.shared.events_state import (
    get_event_from_state,
)


from app.backend.events.list_of_events import (
    get_event_from_list_of_events_given_event_description,
)

from app.backend.mapping.list_of_field_mappings import (
    get_field_mapping_for_event,
    get_list_of_events_with_field_mapping,
    save_field_mapping_for_event,
    does_event_already_have_mapping,
)
from app.objects.abstract_objects.abstract_text import bold
from app.objects.events import Event


def display_form_for_clone_event_field_mapping(interface: abstractInterface):
    current_event = get_event_from_state(interface)
    list_of_events_with_buttons = display_list_of_events_with_field_mapping_buttons(
        exclude_event=current_event, interface=interface
    )
    nav_bar = ButtonBar([cancel_menu_button, help_button])
    warning = get_warning_if_existing_mapping(interface)
    if len(list_of_events_with_buttons) == 0:
        return ListOfLines([nav_bar, Line("No other events exist with mapping setup")])
    else:
        return Form(
            ListOfLines(
            [
                nav_bar,
                Line(
                    "Choose event to clone event field mapping for %s"
                    % str(current_event),
                ),
                warning,
                _______________,
                list_of_events_with_buttons,
            ]
            )
        )


def get_warning_if_existing_mapping(interface: abstractInterface):
    event = get_event_from_state(interface)
    existing_mapping = does_event_already_have_mapping(
        object_store=interface.object_store, event=event
    )

    if existing_mapping:
        return bold(
            "**WARNING**: Will replace existing mapping - there will be no warning or request for confirmation"
        )
    else:
        return ""


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


def post_form_for_clone_event_field_mapping(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    previous_form =interface.get_new_display_form_for_parent_of_function(
            display_form_for_clone_event_field_mapping
        )
    if cancel_menu_button.pressed(last_button):
        return previous_form

    message = clone_field_mapping_for_selected_event_and_return_message(interface)

    interface.log_error(message)

    return previous_form


def clone_field_mapping_for_selected_event_and_return_message(
    interface: abstractInterface,
) -> str:
    event_description_selected = interface.last_button_pressed()
    current_event = get_event_from_state(interface)
    event = get_event_from_list_of_events_given_event_description(
        object_store=interface.object_store,
        event_description=event_description_selected,
    )

    try:
        mapping = get_field_mapping_for_event(
            object_store=interface.object_store, event=event
        )
        assert len(mapping) > 0
    except:

        return "No mapping set up for event of mapping file is corrupted - try another event"

    
    save_field_mapping_for_event(
        object_store=interface.object_store, event=current_event, mapping=mapping
    )
    interface.flush_and_clear()

    message = "Mapping copied from event %s to %s" % (
        event_description_selected,
        str(current_event),
    )

    return message


help_button = HelpButton("WA_clone_mapping_help")
