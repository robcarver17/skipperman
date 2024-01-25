from app.web.events.constants import EVENT
from app.web.flask.state_for_action import StateDataForAction
from app.objects.events import Event
from app.logic.events.events_in_state import get_list_of_events
from app.web.html.forms import html_button
from app.web.html.html import Html


def confirm_event_exists(event_selected):
    list_of_events = get_list_of_events()
    list_of_events_as_str = [str(event) for event in list_of_events]
    assert event_selected in list_of_events_as_str


def update_state_for_specific_event(
    state_data: StateDataForAction, event_selected: str
):
    state_data.set_value(EVENT, event_selected)


def get_event_from_state(state_data: StateDataForAction) -> Event:
    return get_event_from_list_of_events(get_specific_event_str_from_state(state_data))


def get_specific_event_str_from_state(state_data: StateDataForAction) -> str:
    return state_data.get_value(EVENT)


def get_event_from_list_of_events(event_selected: str) -> Event:
    list_of_events = get_list_of_events()
    list_of_events_as_str = [str(event) for event in list_of_events]

    event_idx = list_of_events_as_str.index(event_selected)
    return list_of_events[event_idx]



def row_of_form_for_event_with_buttons(event) -> Html:
    return html_button(str(event))
