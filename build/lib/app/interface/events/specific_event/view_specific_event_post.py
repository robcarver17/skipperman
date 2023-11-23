from app.interface.events.WA.wa_import import display_view_for_specific_event_wa_import
from app.interface.events.WA.wa_update import display_form_wa_update
from app.interface.events.WA.wa_upload import display_view_for_specific_event_wa_upload
from app.interface.events.constants import WA_UPLOAD_BUTTON_LABEL, \
    WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE, WA_FIELD_MAPPING_BUTTON_LABEL, WA_IMPORT_BUTTON_LABEL, \
    WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE, WA_UPDATE_BUTTON_LABEL, WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE, \
    ALLOCATE_CADETS_BUTTON_LABEL
from app.interface.html.forms import BACK_BUTTON_LABEL
from app.interface.events.view_events import display_view_of_events
from app.interface.flask.flash import html_error
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import Html


def post_view_of_selected_event(state_data: StateDataForAction) -> Html:
    ## Called by post on view events form, so both stage and event name are set
    ## don't need to check get/post as will always be post

    last_button_pressed = state_data.last_button_pressed()
    if last_button_pressed == BACK_BUTTON_LABEL:
        ## Back to general view events
        state_data.clear_session_data_for_action_and_reset_stage()
        return display_view_of_events(state_data)

    elif last_button_pressed == WA_UPLOAD_BUTTON_LABEL:
        state_data.stage = WA_UPLOAD_SUBSTAGE_IN_VIEW_EVENT_STAGE
        return display_view_for_specific_event_wa_upload(state_data)

    elif last_button_pressed == WA_FIELD_MAPPING_BUTTON_LABEL:
        return html_error("not implemented, have to manually hack .csv")

    elif last_button_pressed == WA_IMPORT_BUTTON_LABEL:
        state_data.stage = WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE
        return display_view_for_specific_event_wa_import(state_data)

    elif last_button_pressed == WA_UPDATE_BUTTON_LABEL:
        state_data.stage = WA_UPDATE_SUBSTAGE_IN_VIEW_EVENT_STAGE
        return display_form_wa_update(state_data)

    elif last_button_pressed == ALLOCATE_CADETS_BUTTON_LABEL:
        return html_error("not implemented")

    else:
        return html_error("Don't recognise button %s" % last_button_pressed)