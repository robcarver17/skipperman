from app.data_access.data_access import data
from app.interface.events.constants import WA_UPLOAD_BUTTON_LABEL, WA_FIELD_MAPPING_BUTTON_LABEL, \
    ALLOCATE_CADETS_BUTTON_LABEL, BACK_BUTTON_LABEL
from app.interface.events.utils import get_event_from_state
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.forms import form_html_wrapper, html_button
from app.interface.html.html import Html, html_joined_list_as_paragraphs, html_joined_list
from app.logic.events.view_events import is_wa_mapping_setup_for_event, is_wa_field_mapping_setup_for_event
from app.objects.events import Event


def display_form_for_selected_event(state_data: StateDataForAction):
    event = get_event_from_state(state_data)
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
    wa_import =html_button(WA_UPLOAD_BUTTON_LABEL)
    wa_field_mapping = html_button(WA_FIELD_MAPPING_BUTTON_LABEL)
    cadet_allocation = html_button(ALLOCATE_CADETS_BUTTON_LABEL)
    back = html_button(BACK_BUTTON_LABEL)

    wa_import_done = is_wa_mapping_setup_for_event(data=data, event=event)
    field_mapping_done = is_wa_field_mapping_setup_for_event(data=data, event=event)

    if not wa_import_done and field_mapping_done:
        return html_joined_list([
            back,
            wa_import
        ])
    if not field_mapping_done and wa_import_done:
        return html_joined_list([
            back,
            wa_field_mapping ## we can use the import which just maps the event ID
        ])
    if not field_mapping_done and not wa_import_done:
        return html_joined_list([
            back,
            wa_import, ## we can do an import just to map the event ID, which can be used for field mapping
            wa_field_mapping
        ])

    ## both done, we can update the WA file and do cadet allocation
    return html_joined_list([
            back,
            wa_import, ## as an update
            cadet_allocation
        ])