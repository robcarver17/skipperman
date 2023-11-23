from app.interface.cadets.add_cadet import display_view_for_add_cadet
from app.interface.cadets.constants import ADD_CADET_BUTTON_LABEL, ADD_CADET_STAGE, all_sort_types, \
    VIEW_INDIVIDUAL_CADET_STAGE
from app.interface.cadets.view_cadets import display_view_of_cadets
from app.interface.cadets.view_specific_cadet import display_view_for_specific_cadet
from app.interface.flask.state_for_action import StateDataForAction


def post_view_of_cadets(state_data: StateDataForAction):
    button_pressed = state_data.last_button_pressed()
    if button_pressed == ADD_CADET_BUTTON_LABEL:
        state_data.stage = ADD_CADET_STAGE
        return display_view_for_add_cadet(state_data)
    elif button_pressed in all_sort_types:
        ## no change to stage required, just sort order
        sort_order = state_data.last_button_pressed()
        return display_view_of_cadets(state_data, sort_order=sort_order)
    else:  ## must be a cadet:
        state_data.stage = VIEW_INDIVIDUAL_CADET_STAGE
        return display_view_for_specific_cadet(state_data)