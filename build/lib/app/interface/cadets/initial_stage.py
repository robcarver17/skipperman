from app.web.cadets.initial_stage_post import post_view_of_cadets
from app.web.cadets.view_cadets import display_view_of_cadets
from app.web.flask.state_for_action import StateDataForAction

from app.web.html.html import Html

def generate_initial_stage_html_for_cadets(state_data: StateDataForAction) -> Html:
    if state_data.is_posted_form:
        return post_view_of_cadets(state_data)
    else:
        return display_view_of_cadets(state_data)


