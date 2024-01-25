from app.web.events.add_event import display_view_for_add_event
from app.web.events.constants import ADD_EVENT_BUTTON_LABEL, ADD_EVENT_STAGE, all_sort_types, VIEW_EVENT_STAGE
from app.web.events.specific_event.view_specific_event import display_view_for_specific_event
from app.web.events.view_events import display_view_of_events
from app.web.flask.state_for_action import StateDataForAction


def post_view_of_events(state_data: StateDataForAction):
    button_pressed = state_data.last_button_pressed()
    if button_pressed == ADD_EVENT_BUTTON_LABEL:
        state_data.stage = ADD_EVENT_STAGE
        return display_view_for_add_event(state_data)
    elif button_pressed in all_sort_types:
        ## no change to stage required
        sort_by = state_data.last_button_pressed()
        return display_view_of_events(state_data=state_data, sort_by=sort_by)
    else:  ## must be an event
        state_data.stage = VIEW_EVENT_STAGE
        return display_view_for_specific_event(state_data)