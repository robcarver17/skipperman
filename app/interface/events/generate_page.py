from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import Html

from app.interface.events.view_events import display_view_of_events
from app.interface.events.constants import ADD_EVENT_BUTTON_LABEL, ADD_EVENT_STAGE, all_sort_types, VIEW_EVENT_STAGE
from app.interface.events.add_event import get_view_for_add_event

def generate_event_pages(state_data: StateDataForAction) -> Html:
    if state_data.is_initial_stage:
        return display_or_respond_with_view_of_events(state_data)
    elif state_data.stage==ADD_EVENT_STAGE:
        return get_view_for_add_event(state_data)
    elif state_data.stage==VIEW_EVENT_STAGE:
        # fixme
        pass

## INITIAL STAGE

def display_or_respond_with_view_of_events(state_data: StateDataForAction) -> Html:
    if state_data.is_post:
        return post_view_of_events(state_data)
    else:
        return display_view_of_events(state_data)


def post_view_of_events(state_data: StateDataForAction):
    button_pressed = state_data.last_button_pressed()
    if button_pressed== ADD_EVENT_BUTTON_LABEL:
        state_data.stage = ADD_EVENT_STAGE
        return get_view_for_add_event(state_data)
    elif button_pressed in all_sort_types:
        ## no change to stage required
        sort_by = state_data.last_button_pressed()
        return display_view_of_events(state_data=state_data, sort_by=sort_by)
    else: ## must be an event
        state_data.stage = VIEW_EVENT_STAGE
        #return post_view_of_events_with_event_selected(state_data)

"""
{
        "View events": {
            "View list of events": "view_list_of_events",
            "View specific events": "view_specific_events",
        },
        "Create events": {
            "Create new event": "create_new_event",
            "Clone existing event": "clone_existing_event",
            "Import new event data from WA .csv": "import_new_wa_event",
            "Update existing event from WA .csv": "update_existing_wa_event",
        },
        "Allocate cadets to groups": {
            "Allocate cadets not yet in groups": "allocate_unallocated_cadets",
            "Change allocation for cadets in groups": "change_allocated_cadets",
        },
    },"""