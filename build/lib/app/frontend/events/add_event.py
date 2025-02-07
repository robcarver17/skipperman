from typing import Union

from app.backend.events.list_of_events import (
    list_of_previously_used_event_names,
    add_new_verified_event,
)
from app.backend.events.add_events import (
    verify_event_and_warn,
    EventAndVerificationText,
    event_and_text_if_first_time,
)
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.events import (
    Event,
    default_event,
)

from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    dateInput,
    intInput,
    listInput,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.frontend.form_handler import (
    initial_state_form,
    button_error_and_back_to_initial_state_form,
)


def display_form_view_for_add_event(interface: abstractInterface) -> Form:
    return get_add_event_form(interface=interface, first_time_displayed=True)


def get_add_event_form(
    interface: abstractInterface, first_time_displayed: bool = True
) -> Form:
    if first_time_displayed:
        return get_add_event_form_with_information_passed(
            interface=interface, event_and_text=event_and_text_if_first_time
        )
    else:
        event_and_text = process_form_when_checking_event(interface)
        return get_add_event_form_with_information_passed(
            interface=interface, event_and_text=event_and_text
        )


def get_add_event_form_with_information_passed(
    interface: abstractInterface,
    event_and_text: EventAndVerificationText,
) -> Form:
    form_entries = form_fields_for_add_event(
        interface=interface, event=event_and_text.event
    )
    form_is_blank = event_and_text.is_default
    verification_line = Line(event_and_text.verification_text)
    footer_buttons = get_footer_buttons(form_is_blank)
    list_of_elements_inside_form = ListOfLines(
        [
            Heading("Add a new event", centred=True, size=4),
            _______________,
            form_entries,
            verification_line,
            footer_buttons,
        ]
    )

    return Form(list_of_elements_inside_form)

help_button = HelpButton("add_new_event_help")


def get_heading_text():
    header_text = "Do not duplicate event names! (can only have one event with a specific name in a given year, so include months in training weekends eg June Training, or include a number in a series eg Feva Training 1. "

    heading = Heading(header_text, size=6, centred=False)

    return heading


def get_footer_buttons(form_is_blank: bool):
    if form_is_blank:
        return ButtonBar([cancel_menu_button, check_submit_button, help_button])
    else:
        return ButtonBar(
            [cancel_menu_button, check_submit_button, final_submit_button, help_button]
        )




def form_fields_for_add_event(
    interface: abstractInterface, event: Event = default_event
) -> ListOfLines:
    previous_events = list_of_previously_used_event_names(interface.object_store)
    event_name = listInput(
        input_label="Event name (do not include year, eg 'Cadet Week' not 'Cadet Week 2023')",
        input_name=EVENT_NAME,
        default_option=event.event_name,
        list_of_options=previous_events,
    )
    heading = get_heading_text()

    start_date = dateInput(
        input_label="Start date",
        input_name=EVENT_START_DATE,
        value=event.start_date,
    )
    days = intInput(
        input_label="Length in days",
        input_name=EVENT_LENGTH_DAYS,
        value=event.duration,
    )

    list_of_form_entries = [
        event_name,
        heading,
        start_date,
        days,
        _______________,
    ]

    return ListOfLines(list_of_form_entries).add_Lines()


def post_form_view_for_add_event(
    interface: abstractInterface, first_time_displayed: bool = False
) -> Union[Form, NewForm]:
    if first_time_displayed:
        ## hasn't been displayed before, will have no defaults
        return get_add_event_form(interface=interface, first_time_displayed=True)

    last_button_pressed = interface.last_button_pressed()

    if check_submit_button.pressed(last_button_pressed):
        ## verify results, display form again
        return get_add_event_form(interface=interface, first_time_displayed=False)

    elif final_submit_button.pressed(last_button_pressed):
        return process_form_when_event_verified(interface)

    elif cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)


def process_form_when_checking_event(
    interface: abstractInterface,
) -> EventAndVerificationText:
    try:
        event = get_event_from_form(interface)
        verify_text = verify_event_and_warn(
            object_store=interface.object_store, event=event
        )
    except Exception as e:
        verify_text = (
            "Doesn't appear to be a valid event: error %s"
            % str(e)
        )

        event = default_event

    return EventAndVerificationText(event=event, verification_text=verify_text)


def get_event_from_form(interface) -> Event:
    event_name = interface.value_from_form(EVENT_NAME)
    start_date = interface.value_from_form(EVENT_START_DATE, value_is_date=True)
    duration = int(interface.value_from_form(EVENT_LENGTH_DAYS))

    event = Event.from_date_length_and_name_only(
        event_name=event_name, start_date=start_date, duration=duration
    )

    return event


def process_form_when_event_verified(interface: abstractInterface) -> Form:
    try:
        event = get_event_from_form(interface)
        print("ffrom form %s" % event)
        add_new_verified_event(interface.object_store, event=event)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        interface.log_error(
            "Can't add this event, reason: %s, try again or consult support" % str(e)
        )
        return initial_state_form

    interface.flush_cache_to_store()

    return form_with_message_and_finished_button(
        "Added event %s" % str(event),
        interface=interface,
        function_whose_parent_go_to_on_button_press=display_form_view_for_add_event,
    )


EVENT_NAME = "event_name"
EVENT_START_DATE = "event_start_date"
EVENT_LENGTH_DAYS = "event_length_days"
EVENT_CONTAINS = "event_contains"


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_for_add_event
    )


CHECK_BUTTON_LABEL = "Check details entered"
FINAL_ADD_BUTTON_LABEL = "Yes - these details are correct - add to data"

final_submit_button = Button(FINAL_ADD_BUTTON_LABEL, nav_button=True)
check_submit_button = Button(CHECK_BUTTON_LABEL, nav_button=True)
