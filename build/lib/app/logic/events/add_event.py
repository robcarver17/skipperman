from dataclasses import dataclass
from typing import Union

from app.backend.events import verify_event_and_warn, add_new_verified_event
from app.logic.events.constants import (
    EVENT_NAME,
    EVENT_START_DATE,
    EVENT_END_DATE,
    EVENT_TYPE,
    CHECK_BUTTON_LABEL,
    FINAL_ADD_BUTTON_LABEL,
)

from app.objects.events import Event, default_event, list_of_event_types, EventType

from app.logic.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput, dateInput, radioInput,
)
from app.objects.abstract_objects.abstract_buttons import cancel_button, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.logic.abstract_logic_api import initial_state_form

dict_of_event_types = dict(
    [(event_type, event_type) for event_type in list_of_event_types]
)


def display_form_view_for_add_event(interface: abstractInterface) -> Form:
    return post_form_view_for_add_event(interface=interface, first_time_displayed=True)


def post_form_view_for_add_event(
    interface: abstractInterface, first_time_displayed: bool = False
) -> Union[Form, NewForm]:
    if first_time_displayed:
        ## hasn't been displayed before, will have no defaults
        return get_add_event_form(interface=interface, first_time_displayed=True)

    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed == CHECK_BUTTON_LABEL:
        ## verify results, display form again
        return get_add_event_form(interface=interface, first_time_displayed=False)

    elif last_button_pressed == FINAL_ADD_BUTTON_LABEL:
        return process_form_when_event_verified(interface)

    else:
        interface.log_error("Unknown button %s shouldn't happen" % last_button_pressed)
        return initial_state_form


@dataclass
class EventAndVerificationText:
    event: Event = (default_event,)
    verification_text: str = ("",)

    @property
    def is_default(self) -> bool:
        return self.event is default_event


event_and_text_if_first_time = EventAndVerificationText(
    event=default_event, verification_text=""
)


def get_add_event_form(
    interface: abstractInterface, first_time_displayed: bool = True
) -> Form:
    print("First time display? %s" % str(first_time_displayed))
    if first_time_displayed:
        return get_add_event_form_with_information_passed(event_and_text_if_first_time)
    else:
        event_and_text = process_form_when_checking_event(interface)
        return get_add_event_form_with_information_passed(event_and_text)


def get_add_event_form_with_information_passed(
    event_and_text: EventAndVerificationText,
) -> Form:
    print(event_and_text)
    header_text = Line("Add a new event. Do not duplicate!")
    verification_line = Line(event_and_text.verification_text)

    form_entries = form_fields_for_add_event(event=event_and_text.event)
    form_is_blank = event_and_text.is_default
    footer_buttons = get_footer_buttons(form_is_blank)

    list_of_elements_inside_form = ListOfLines(
        [
            header_text,
            form_entries,
            verification_line,
            footer_buttons,
        ]
    )

    return Form(list_of_elements_inside_form)

def get_footer_buttons(form_is_blank: bool):
    final_submit = Button(FINAL_ADD_BUTTON_LABEL)
    check_submit = Button(CHECK_BUTTON_LABEL)
    if form_is_blank:
        return Line([cancel_button,  check_submit])
    else:
        return Line([cancel_button, check_submit, final_submit])



def form_fields_for_add_event(event: Event = default_event) -> ListOfLines:
    print("event %s type %s" % (str(event), str(type(event))))
    event_name = textInput(
        input_label="Event name (do not include year, eg 'Cadet Week' not 'Cadet Week 2023')",
        input_name=EVENT_NAME,
        value=event.event_name,
    )
    start_date = dateInput(
        input_label="Start date",
        input_name=EVENT_START_DATE,
        value=event.start_date,
    )
    end_date = dateInput(
        input_label="End date",
        input_name=EVENT_END_DATE,
        value=event.end_date,
    )
    event_type = radioInput(
        input_label="Type of event",
        input_name=EVENT_TYPE,
        default_label=event.event_type_as_str,
        dict_of_options=dict_of_event_types,
    )

    list_of_form_entries = [
        event_name,
        start_date,
        end_date,
        event_type,
    ]

    return ListOfLines(list_of_form_entries)


def process_form_when_checking_event(
    interface: abstractInterface,
) -> EventAndVerificationText:
    try:
        event = get_event_from_form(interface)
        verify_text = verify_event_and_warn(event)
    except Exception as e:
        verify_text = (
            "Doesn't appear to be a valid event (wrong date time in old browser?) error code %s"
            % str(e)
        )

        event = default_event

    return EventAndVerificationText(event=event, verification_text=verify_text)


def get_event_from_form(interface) -> Event:
    event_name = interface.value_from_form(EVENT_NAME)
    start_date = interface.value_from_form(EVENT_START_DATE, value_is_date=True)
    end_date = interface.value_from_form(EVENT_END_DATE, value_is_date=True)
    event_type = EventType[interface.value_from_form(EVENT_TYPE)]

    event = Event(
        event_name=event_name,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
    )

    print("Event is %s" % str(event))

    return event


def process_form_when_event_verified(interface: abstractInterface) -> Form:
    try:
        event = get_event_from_form(interface)
        add_new_verified_event(event)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        interface.log_error(
            "Can't add this event, reason: %s, try again or consult support" % str(e)
        )
        return initial_state_form

    return form_with_message_and_finished_button(
        "Added event %s" % str(event), interface=interface
    )


