from app.web.events.initial_stage_post import post_view_of_events
from app.web.events.view_events import display_view_of_events
from app.web.flask.state_for_action import StateDataForAction
from app.web.html.html import Html


def generate_initial_stage_html_for_events(state_data: StateDataForAction) -> Html:
    if state_data.is_posted_form:
        return post_view_of_events(state_data)
    else:
        return display_view_of_events(state_data)