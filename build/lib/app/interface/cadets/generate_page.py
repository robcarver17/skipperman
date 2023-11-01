from app.interface.cadets.add_cadet import get_view_for_add_cadet
from app.interface.cadets.constants import ADD_CADET_BUTTON_LABEL, all_sort_types, VIEW_INDIVIDUAL_CADET_STAGE, ADD_CADET_STAGE
from app.interface.cadets.view_cadets import display_view_of_cadets
from app.interface.cadets.view_specific_cadet import post_view_of_cadets_with_cadet_selected
from app.interface.flask.state_for_action import StateDataForAction

from app.interface.html.html import Html


def generate_cadet_pages(state_data: StateDataForAction) -> Html:
    if state_data.is_initial_stage:
        return display_or_respond_with_view_of_cadets(state_data)
    elif state_data.stage== VIEW_INDIVIDUAL_CADET_STAGE:
        pass
    elif state_data.stage== ADD_CADET_STAGE:
        return get_view_for_add_cadet(state_data)

## INITIAL STAGE

def display_or_respond_with_view_of_cadets(state_data: StateDataForAction) -> Html:
    if state_data.is_post:
        return post_view_of_cadets(state_data)
    else:
        return display_view_of_cadets(state_data)


def post_view_of_cadets(state_data: StateDataForAction):
    button_pressed = state_data.last_button_pressed()
    if button_pressed== ADD_CADET_BUTTON_LABEL:
        state_data.stage = ADD_CADET_STAGE
        return get_view_for_add_cadet(state_data)
    elif button_pressed in all_sort_types:
        ## no change to stage required
        sort_order = state_data.last_button_pressed()
        return display_view_of_cadets(state_data, sort_order=sort_order)
    else: ## must be a cadet:
        state_data.stage = VIEW_INDIVIDUAL_CADET_STAGE
        return post_view_of_cadets_with_cadet_selected(state_data)

