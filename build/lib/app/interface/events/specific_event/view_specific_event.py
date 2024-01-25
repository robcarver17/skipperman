from app.web.events.specific_event.form_for_specific_event import (
    get_selected_event_form,
)
from app.web.events.utils import (
    confirm_event_exists,
    update_state_for_specific_event,
)

from app.web.flask.state_for_action import StateDataForAction
from app.web.flask.flash import html_error



def display_view_for_specific_event(state_data: StateDataForAction):
    ## Called by post on view events form
    event_selected = state_data.last_button_pressed()

    try:
        confirm_event_exists(event_selected)
    except:
        state_data.reset_to_initial_stage()  ## on refresh will go back to view cadets
        return html_error(
            "Event %s no longer in list- someone else has deleted or file corruption?"
            % event_selected
        )

    ## so whilst we are in this stage, we know which event we are talking about
    update_state_for_specific_event(
        state_data=state_data, event_selected=event_selected
    )

    return get_selected_event_form(state_data=state_data)


