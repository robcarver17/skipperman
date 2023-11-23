from app.data_access.configuration.configuration import WILD_APRICOT_FILE_TYPES
from app.interface.events.constants import WA_FILE, UPLOAD_FILE_BUTTON_LABEL
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.forms import form_html_wrapper, html_file_input, html_button, BACK_BUTTON_LABEL
from app.interface.html.html import Html, html_joined_list_as_paragraphs, html_joined_list
from app.objects.events import Event


def get_form_for_wa_upload(event: Event, state_data: StateDataForAction):
    html_inside_form = html_inside_form_for_wa_file_upload(
        "Select exported WA file for event %s" % str(event)
    )
    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)


def html_inside_form_for_wa_file_upload(display_str: str):
    prompt = Html(display_str)
    buttons = get_upload_buttons()
    input_field = html_file_input(WA_FILE, accept=WILD_APRICOT_FILE_TYPES)

    list_of_html_inside_form = [prompt, input_field, buttons]
    html_inside_form = html_joined_list_as_paragraphs(list_of_html_inside_form)

    return html_inside_form


def get_upload_buttons():
    back = html_button(BACK_BUTTON_LABEL)
    upload = html_button(UPLOAD_FILE_BUTTON_LABEL)

    return html_joined_list([back, upload])