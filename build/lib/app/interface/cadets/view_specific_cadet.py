from app.data_access.data_access import data
from app.interface.cadets.constants import CADET, VIEW_INDIVIDUAL_CADET_STAGE
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import html_error, Html
from app.logic.cadets.view_cadets import get_list_of_cadets

# FIXME NOT PROPERLY IMPLEMENTED
# FIXME ADD OTHER INFORMATION ABOUT CADET HERE
# FIXME ADD DELETE / EDIT OPTIONS

def post_view_of_cadets_with_cadet_selected(state_data: StateDataForAction):
    cadet_selected = state_data.last_button_pressed()

    try:
        confirm_cadet_exists(cadet_selected)
    except:
        state_data.clear_session_data_for_action_and_reset_stage() ## on refresh will go back to view cadets
        return html_error("Cadet %s no longer in list- someone else has deleted or file corruption?" % cadet_selected)

    update_state_for_specific_cadet(state_data=state_data, cadet_selected=cadet_selected)

    return display_form_for_selected_cadet(cadet_selected, state_data)


def confirm_cadet_exists(cadet_selected):
    list_of_cadets_as_str = [str(cadet) for cadet in get_list_of_cadets(data)]
    assert cadet_selected in list_of_cadets_as_str


def update_state_for_specific_cadet(state_data: StateDataForAction, cadet_selected: str):
    state_data.set_value(CADET, cadet_selected)



def get_specific_cadet_from_state(state_data: StateDataForAction) ->str:
    return state_data.get_value(CADET)


def display_form_for_selected_cadet(cadet_selected: str, state_data: StateDataForAction):
    return Html("%s %s" % (state_data.stage,get_specific_cadet_from_state(state_data)))