from app.interface.events.constants import (
    WA_UPLOAD_BUTTON_LABEL,
    WA_FIELD_MAPPING_BUTTON_LABEL,
    ALLOCATE_CADETS_BUTTON_LABEL,
    WA_IMPORT_BUTTON_LABEL,
    WA_UPDATE_BUTTON_LABEL,
)

from app.interface.events.utils import get_event_from_state
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.flask.flash import flash_error
from app.interface.html.forms import form_html_wrapper, html_button, BACK_BUTTON_LABEL
from app.interface.html.html import (
    Html,
    html_joined_list_as_paragraphs,
    html_joined_list,
)
from app.logic.events.view_events import (
    is_wa_mapping_setup_for_event,
    is_wa_field_mapping_setup_for_event,
)
from app.logic.events.backend.load_wa_file import does_raw_event_file_exist
from app.objects.events import Event


def get_selected_event_form(state_data: StateDataForAction):
    event = get_event_from_state(state_data)
    html_inside_form = get_html_inside_view_event_form(event)
    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)


def get_html_inside_view_event_form(event: Event):

    event_description = Html(event.verbose_repr)
    buttons = get_event_buttons(event)

    list_of_html_inside_form = [event_description, buttons]

    html_inside_form = html_joined_list_as_paragraphs(list_of_html_inside_form)

    return html_inside_form


def get_event_buttons(event: Event):
    wa_initial_upload = html_button(
        WA_UPLOAD_BUTTON_LABEL
    )  ## uploads and creates staging file
    wa_field_mapping = html_button(
        WA_FIELD_MAPPING_BUTTON_LABEL
    )  ## does field mapping from staged file
    wa_import = html_button(WA_IMPORT_BUTTON_LABEL)  ## does import_wa given a staged file
    wa_update = html_button(
        WA_UPDATE_BUTTON_LABEL
    )  ## does upload and import_wa, assuming no staged file

    cadet_allocation = html_button(ALLOCATE_CADETS_BUTTON_LABEL)

    back = html_button(BACK_BUTTON_LABEL)

    wa_import_done = is_wa_mapping_setup_for_event(event=event)
    field_mapping_done = is_wa_field_mapping_setup_for_event(event=event)
    raw_event_file_exists = does_raw_event_file_exist(event.id)

    if not wa_import_done and not field_mapping_done and not raw_event_file_exists:
        return html_joined_list([back, wa_initial_upload])

    if wa_import_done and not field_mapping_done and not raw_event_file_exists:
        ## something went wrong getting the raw event file, try again
        return html_joined_list([back, wa_initial_upload])

    if not wa_import_done and field_mapping_done and not raw_event_file_exists:
        ## probably done mapping manually, need to do initial upload
        return html_joined_list([back, wa_initial_upload])

    if wa_import_done and not field_mapping_done and raw_event_file_exists:
        return html_joined_list([back, wa_field_mapping])

    if wa_import_done and field_mapping_done and raw_event_file_exists:
        return html_joined_list([back, wa_import])

    ## both done, we can update the WA file and do cadet allocation
    if wa_import_done and field_mapping_done and not raw_event_file_exists:
        return html_joined_list([back, wa_update, cadet_allocation])

    flash_error(
        "Something went wrong; contact support [wa_import_done=%s, field_mapping_done=%s, raw_event_file_exists=%s]"
        % (str(wa_import_done), str(field_mapping_done), str(raw_event_file_exists))
    )
    return back
