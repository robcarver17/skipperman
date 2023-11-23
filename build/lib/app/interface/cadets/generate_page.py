from app.interface.cadets.add_cadet import display_view_for_add_cadet
from app.interface.cadets.constants import (
    ADD_CADET_BUTTON_LABEL,
    all_sort_types,
    VIEW_INDIVIDUAL_CADET_STAGE,
    ADD_CADET_STAGE,
)
from app.interface.cadets.initial_stage import generate_initial_stage_html_for_cadets
from app.interface.flask.state_for_action import StateDataForAction

from app.interface.html.html import Html
from app.interface.flask.flash import html_error


def generate_cadet_pages(state_data: StateDataForAction) -> Html:
    stage = state_data.stage
    print("Stage is %s generating page" % stage)
    print("Last button pressed %s" % str(state_data.last_button_pressed()))
    print("Is post %s" % str(state_data.is_posted_form))

    if state_data.is_initial_stage:
        return generate_initial_stage_html_for_cadets(state_data)
    elif stage == VIEW_INDIVIDUAL_CADET_STAGE:
        return html_error("Not implemented")
    elif stage == ADD_CADET_STAGE:
        return display_view_for_add_cadet(state_data)
    else:
        return html_error(
            "Stage %s not recognised something has gone horribly wrong"
            % state_data.stage
        )




