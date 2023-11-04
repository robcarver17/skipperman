import datetime
from typing import Tuple

from app.interface.flask.state_for_action import StateDataForAction

from app.interface.html.components import back_button_only_with_text
from app.interface.html.html import (
    Html,
    ListOfHtml,
    empty_html,
    html_bold,
    html_joined_list,
    html_joined_list_as_paragraphs,
)
from app.interface.flask.flash import html_error
from app.interface.html.forms import (
    form_html_wrapper,
    html_button,
    html_form_text_input,
    html_date_input,
    html_radio_input,
    html_as_date,
)

from app.interface.events.constants import (
    BACK_BUTTON_LABEL,
    CHECK_BUTTON_LABEL,
    CLONE_EVENT_BUTTON_LABEL,
    EVENT_NAME,
    EVENT_START_DATE,
    EVENT_END_DATE,
    EVENT_TYPE,
    FINAL_ADD_BUTTON_LABEL,
    ADD_EVENT_BUTTON_LABEL,
)

from app.interface.events.view_events import display_view_of_events
from app.logic.events.add_event import add_new_verified_event, verify_event_and_warn
from app.objects.events import Event, default_event, list_of_event_types, EventType


def get_view_for_add_event(state_data: StateDataForAction):
    ## don't need to check get/post as will always be post
    last_button_pressed = state_data.last_button_pressed()
    if last_button_pressed == ADD_EVENT_BUTTON_LABEL:
        ## hasn't been displayed before, will have no defaults
        return display_form(state_data)

    elif last_button_pressed == CLONE_EVENT_BUTTON_LABEL:
        return html_error("Cloning not implemented")

    elif last_button_pressed == CHECK_BUTTON_LABEL:
        ## verify results, display form again
        verification_text, form_values = process_form_when_checking_event(state_data)
        return display_form(
            state_data, verification_text=verification_text, form_values=form_values
        )

    elif last_button_pressed == FINAL_ADD_BUTTON_LABEL:
        return process_form_when_event_verified(state_data)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        state_data.reset_to_initial_stage()
        return display_view_of_events(state_data)

    else:
        return html_error("Uknown button pressed - shouldn't happen!")


def display_form(
    state_data: StateDataForAction,
    form_values: Event = default_event,
    verification_text: Html = empty_html,
):

    html_inside_form = get_html_inside_form(
        form_values=form_values, verification_text=verification_text
    )
    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)


def get_html_inside_form(
    form_values: Event = default_event, verification_text: Html = empty_html
):

    header_text = Html("Add a new event. Do not duplicate!")

    event_name = html_form_text_input(
        input_label="Event name (do not include year, eg 'Cadet Week' not 'Cadet Week 2023')",
        input_name=EVENT_NAME,
        value=form_values.event_name,
    )
    start_date = html_date_input(
        input_label="Start date",
        input_name=EVENT_START_DATE,
        max_date_years=2,
        min_date_years=2,
        value=form_values.start_date,
    )
    end_date = html_date_input(
        input_label="End date",
        input_name=EVENT_END_DATE,
        max_date_years=2,
        min_date_years=2,
        value=form_values.end_date,
    )
    event_type = html_radio_input(
        input_label="Type of event",
        input_name=EVENT_TYPE,
        default_label=form_values.event_type_as_str,
        dict_of_options=dict_of_event_types,
    )

    form_is_blank = form_values is default_event
    footer_buttons = get_footer_buttons(form_is_blank)

    list_of_html_inside_form = [
        header_text,
        event_name,
        start_date,
        end_date,
        event_type,
        verification_text,
        footer_buttons,
    ]
    html_inside_form = html_joined_list_as_paragraphs(list_of_html_inside_form)

    return html_inside_form


def process_form_when_checking_event(
    state_data: StateDataForAction,
) -> Tuple[Html, Event]:

    try:
        event = get_event_from_form(state_data)
        verify_text = html_bold(verify_event_and_warn(event))
    except Exception as e:
        verify_text = html_bold(
            "Doesn't appear to be a valid event (wrong date time in old browser?) error code %s"
            % str(e)
        )
        event = default_event

    return verify_text, event


def get_event_from_form(state_data: StateDataForAction) -> Event:
    event_name = state_data.value_from_form(EVENT_NAME)
    start_date = html_as_date(state_data.value_from_form(EVENT_START_DATE))
    end_date = html_as_date(state_data.value_from_form(EVENT_END_DATE))
    event_type = EventType[state_data.value_from_form(EVENT_TYPE)]

    return Event(
        event_name=event_name,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
    )


def process_form_when_event_verified(state_data: StateDataForAction):
    try:
        event = get_event_from_form(state_data)
        add_new_verified_event(event)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        return html_error("Can't add this event, reason: %s, try again" % str(e))

    state_data.clear_session_data_for_action_and_reset_stage()
    return back_button_only_with_text(
        state_data=state_data, some_text="Added event %s" % str(event)
    )


def get_footer_buttons(form_is_blank: bool):
    back = html_button(BACK_BUTTON_LABEL)
    final_submit = html_button(FINAL_ADD_BUTTON_LABEL)
    check_submit = html_button(CHECK_BUTTON_LABEL)
    clone_event = html_button(CLONE_EVENT_BUTTON_LABEL)
    if form_is_blank:
        return html_joined_list([back, clone_event, check_submit])
    else:
        return html_joined_list([back, check_submit, final_submit])


dict_of_event_types = dict(
    [(event_type, event_type) for event_type in list_of_event_types]
)
