from typing import Union

from app.backend.events import verify_event_and_warn, list_of_previously_used_event_names, EventAndVerificationText, \
    event_and_text_if_first_time, add_new_verified_event
from app.logic.events.constants import (
    CHECK_BUTTON_LABEL,
    FINAL_ADD_BUTTON_LABEL,
)
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.events import Event, default_event, DICT_OF_NAMES_AND_ATTRIBUTES_CHECKBOX, EXAMPLES_OF_EVENTS

from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput, dateInput, checkboxInput,
intInput
)
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button, ButtonBar
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_logic_api import initial_state_form, button_error_and_back_to_initial_state_form


def display_form_view_for_add_event(interface: abstractInterface) -> Form:
    return post_form_view_for_add_event(interface=interface, first_time_displayed=True)


def get_add_event_form(
    interface: abstractInterface, first_time_displayed: bool = True
) -> Form:
    if first_time_displayed:
        return get_add_event_form_with_information_passed(interface=interface, event_and_text=event_and_text_if_first_time)
    else:
        event_and_text = process_form_when_checking_event(interface)
        return get_add_event_form_with_information_passed(interface=interface, event_and_text=event_and_text)


def get_add_event_form_with_information_passed(
        interface: abstractInterface,
    event_and_text: EventAndVerificationText,
) -> Form:

    form_entries = form_fields_for_add_event(interface=interface, event=event_and_text.event)
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

def get_heading_text(interface: abstractInterface):
    header_text = "Do not duplicate event names! (can only have one event with a specific name in a given year, so include months in training weekends eg June Training, or include a number in a series eg Feva Training 1. "
    previous_events =  list_of_previously_used_event_names(interface)
    previous_events_text = " Previously used event names: %s" % ", ".join(previous_events)

    heading = Heading(header_text+ previous_events_text, size=6, centred=False)

    return heading


def get_footer_buttons(form_is_blank: bool):
    final_submit = Button(FINAL_ADD_BUTTON_LABEL, nav_button=True)
    check_submit = Button(CHECK_BUTTON_LABEL, nav_button=True)
    cancel_button = Button(CANCEL_BUTTON_LABEL, nav_button=True)
    if form_is_blank:
        return ButtonBar([cancel_button,  check_submit])
    else:
        return ButtonBar([cancel_button, check_submit, final_submit])



def form_fields_for_add_event(interface: abstractInterface, event: Event = default_event) -> ListOfLines:
    print("event %s type %s" % (str(event), str(type(event))))
    event_name = textInput(
        input_label="Event name (do not include year, eg 'Cadet Week' not 'Cadet Week 2023')",
        input_name=EVENT_NAME,
        value=event.event_name,
    )
    heading = get_heading_text(interface)

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
    dict_of_checked = dict([(label,
                             getattr(event, get_event_attribute_given_label(label))
                             )
                            for label in list_of_possible_checkbox_labels])

    event_type = checkboxInput(
        input_label="Event contains",
        input_name=EVENT_CONTAINS,
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked
    )

    list_of_form_entries = [
        event_name,
        heading,
        start_date,
        days,
        _______________,
        event_type,
        Heading(EXAMPLES_OF_EVENTS, size=6, centred=False)
    ]

    return ListOfLines(list_of_form_entries).add_Lines()

list_of_possible_checkbox_labels = (DICT_OF_NAMES_AND_ATTRIBUTES_CHECKBOX.keys())
def get_event_attribute_given_label(label):
    return DICT_OF_NAMES_AND_ATTRIBUTES_CHECKBOX[label]

dict_of_labels = dict([(label, label) for label in list_of_possible_checkbox_labels])


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

    elif last_button_pressed == CANCEL_BUTTON_LABEL:
        return previous_form(interface)
    else:
        button_error_and_back_to_initial_state_form(interface)



def process_form_when_checking_event(
    interface: abstractInterface,
) -> EventAndVerificationText:
    try:
        event = get_event_from_form(interface)
        verify_text = verify_event_and_warn(interface=interface, event=event)
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
    duration= int(interface.value_from_form(EVENT_LENGTH_DAYS))

    list_of_contained_labels_set_to_true = interface.value_of_multiple_options_from_form(EVENT_CONTAINS)

    event = Event.from_date_length_and_name_only(
        event_name=event_name,
        start_date=start_date,
        duration=duration
    )

    add_list_of_contains_flags_to_event(event=event, list_of_contained_labels_set_to_true=list_of_contained_labels_set_to_true)

    print(event.details_as_list_of_str())

    return event

def add_list_of_contains_flags_to_event(event: Event, list_of_contained_labels_set_to_true: list):
    for event_label in list_of_possible_checkbox_labels:
        if event_label in list_of_contained_labels_set_to_true:
            setattr(event, get_event_attribute_given_label(event_label), True)
        else:
            setattr(event, get_event_attribute_given_label(event_label), False)

def process_form_when_event_verified(interface: abstractInterface) -> Form:
    try:
        event = get_event_from_form(interface)
        print("ffrom form %s" % event)
        add_new_verified_event(interface=interface, event=event)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        interface.log_error(
            "Can't add this event, reason: %s, try again or consult support" % str(e)
        )
        interface.save_stored_items()
        return initial_state_form

    return form_with_message_and_finished_button("Added event %s" % str(event), interface=interface,
                                                 function_whose_parent_go_to_on_button_press=display_form_view_for_add_event)


EVENT_NAME = "event_name"
EVENT_START_DATE = "event_start_date"
EVENT_LENGTH_DAYS = "event_length_days"
EVENT_CONTAINS = "event_contains"

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_view_for_add_event)
