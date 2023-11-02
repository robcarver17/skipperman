from app.data_access.data_access import data

from app.interface.events.constants import WA_UPLOAD_BUTTON_LABEL, WA_UPDATE_BUTTON_LABEL, WA_FIELD_MAPPING_BUTTON_LABEL, ALLOCATE_CADETS_BUTTON_LABEL, BACK_BUTTON_LABEL, WA_IMPORT_SUBSTAGE_IN_VIEW_EVENT_STAGE
from app.interface.events.utils import confirm_event_exists, update_state_for_specific_event, \
    get_event_from_list_of_events
from app.interface.events.view_events import display_view_of_events
from app.interface.events.specific_event.wa_import import display_form_wa_import

from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import html_error, Html, html_joined_list, html_joined_list_as_paragraphs
from app.interface.html.forms import html_button, form_html_wrapper

from app.logic.events.view_events import is_wa_mapping_setup_for_event, is_wa_field_mapping_setup_for_event
from app.objects.events import Event

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

    return display_form_for_selected_event(event_selected=event_selected, state_data=state_data)

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

    if last_button_pressed == WA_UPDATE_BUTTON_LABEL:
        pass
    if last_button_pressed== WA_FIELD_MAPPING_BUTTON_LABEL:
        return html_error('not implemented, have to manually hack .csv')
    if last_button_pressed == ALLOCATE_CADETS_BUTTON_LABEL:
        pass


def display_form_for_selected_event(event_selected: str, state_data: StateDataForAction):
    event = get_event_from_list_of_events(event_selected)
    html_inside_form = get_html_inside_form(event)
    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)

def get_html_inside_form(event: Event):

    event_description = Html(event.verbose_repr)
    buttons = get_event_buttons(event)

    list_of_html_inside_form = [event_description, buttons]

    html_inside_form = html_joined_list_as_paragraphs(list_of_html_inside_form)

    return html_inside_form


def get_event_buttons(event: Event):
    wa_first_import =html_button(WA_UPLOAD_BUTTON_LABEL)
    wa_update = html_button(WA_UPDATE_BUTTON_LABEL)
    wa_field_mapping = html_button(WA_FIELD_MAPPING_BUTTON_LABEL)
    cadet_allocation = html_button(ALLOCATE_CADETS_BUTTON_LABEL)
    back = html_button(BACK_BUTTON_LABEL)

    wa_import_done = is_wa_mapping_setup_for_event(data=data, event=event)
    field_mapping_done = is_wa_field_mapping_setup_for_event(data=data, event=event)

    if not wa_import_done and field_mapping_done:
        return html_joined_list([
            back,
            wa_first_import
        ])
    if not field_mapping_done and wa_import_done:
        return html_joined_list([
            back,
            wa_field_mapping ## we can use the import which just maps the event ID
        ])
    if not field_mapping_done and not wa_import_done:
        return html_joined_list([
            back,
            wa_first_import, ## we can do an import just to map the event ID, which can be used for field mapping
            wa_field_mapping
        ])

    ## both done, we can update the WA file and do cadet allocation
    return html_joined_list([
            back,
            wa_update,
            cadet_allocation
        ])

