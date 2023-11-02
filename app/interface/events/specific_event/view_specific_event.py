from app.interface.events.constants import WA_UPLOAD_BUTTON_LABEL, WA_FIELD_MAPPING_BUTTON_LABEL, ALLOCATE_CADETS_BUTTON_LABEL, BACK_BUTTON_LABEL, WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE
from app.interface.events.specific_event.form_for_specific_event import display_form_for_selected_event
from app.interface.events.utils import confirm_event_exists, update_state_for_specific_event
from app.interface.events.view_events import display_view_of_events
from app.interface.events.specific_event.wa_import import display_form_wa_import

from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import html_error, Html


## read once to avoid chance of changes

def view_of_events_with_event_selected(state_data: StateDataForAction):
    ## Called by post on view events form
    event_selected = state_data.last_button_pressed()

    try:
        confirm_event_exists(event_selected)
    except:
        state_data.reset_to_initial_stage() ## on refresh will go back to view cadets
        return html_error("Event %s no longer in list- someone else has deleted or file corruption?" % event_selected)

    ## so whilst we are in this stage, we know which event we are talking about
    update_state_for_specific_event(state_data=state_data, event_selected=event_selected)

    return display_form_for_selected_event(state_data=state_data)

def post_action_on_selected_event(state_data: StateDataForAction) -> Html:
    ## Called by post on view events form, so both stage and event name are set
    ## don't need to check get/post as will always be post

    last_button_pressed = state_data.last_button_pressed()
    if last_button_pressed== BACK_BUTTON_LABEL:
        ## Back to general view events
        state_data.clear_session_data_for_action_and_reset_stage()
        return display_view_of_events(state_data)

    if last_button_pressed == WA_UPLOAD_BUTTON_LABEL:
        state_data.stage = WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE
        return display_form_wa_import(state_data)

    if last_button_pressed== WA_FIELD_MAPPING_BUTTON_LABEL:
        return html_error('not implemented, have to manually hack .csv')
    if last_button_pressed == ALLOCATE_CADETS_BUTTON_LABEL:
        return html_error('not implemented')


