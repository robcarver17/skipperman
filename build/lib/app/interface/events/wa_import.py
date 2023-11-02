from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import html_error, Html, html_joined_list_as_paragraphs, html_joined_list
from app.interface.html.forms import form_html_wrapper, html_file_input, html_button

from app.interface.events.utils import get_event_from_state
from app.interface.events.constants import WA_FILE, BACK_BUTTON_LABEL, UPLOAD_FILE_LABEL, VIEW_EVENT_STAGE
from app.interface.events.specific_event.view_specific_event import view_of_events_with_event_selected

from app.logic.events.view_events import is_wa_mapping_setup_for_event

from app.objects.events import Event

from app.data_access.data_access import data
from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES


def display_form_first_wa_import(state_data: StateDataForAction):
    ## no need to check post as always will be
    event = get_event_from_state(state_data)

    event_already_exists = is_wa_mapping_setup_for_event(data=data, event=event)
    if event_already_exists:
        return html_error("Event %s has already had it's first import from WA; try returning to menu and continuing" % str(event))

    return get_form_first_wa_import_for_event(event=event, state_data=state_data)


def post_response_to_first_wa_import(state_data: StateDataForAction):
    ## no need to check post as always will be. Sent here from generate_page
    # get the event from the state
    button_pressed = state_data.last_button_pressed()
    if button_pressed == BACK_BUTTON_LABEL:
        ## revert to view specific event
        ## update stage only, keep event stored
        state_data.stage=VIEW_EVENT_STAGE
        return view_of_events_with_event_selected(state_data)
    elif button_pressed == UPLOAD_FILE_LABEL:
        pass
    else:
        return html_error('Weird button pressed!')
    event = get_event_from_state(state_data)
    ## check button pressed (can only be upload or back)
    file = state_data.uploaded_file(WA_FILE)
    return Html("event %s filename %s" % (event, file.filename))
    ## save file
    """
    current_filename = file.filename
    if file.filename == '':
        flash('No selected file')
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in WILD_APRICOT_FILE_TYPES:
            problem!

    new_filename=""
    file.save(new_filename)

    ## process file (reload from filename)
    """

def get_form_first_wa_import_for_event(event: Event, state_data: StateDataForAction):
    html_inside_form = html_inside_form_for_wa_file_import("Select exported WA file for event %s" % str(event))
    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)

def html_inside_form_for_wa_file_import(display_str: str):
    prompt = Html(display_str)
    buttons = get_upload_buttons()
    input_field = html_file_input(WA_FILE, accept=WILD_APRICOT_FILE_TYPES)

    list_of_html_inside_form = [prompt, input_field, buttons]
    html_inside_form = html_joined_list_as_paragraphs(list_of_html_inside_form)

    return html_inside_form


def get_upload_buttons():
    back = html_button(BACK_BUTTON_LABEL)
    upload = html_button(UPLOAD_FILE_LABEL)

    return html_joined_list([
        back,
        upload
    ])
