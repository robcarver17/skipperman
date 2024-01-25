from typing import Union
from app.web.action_hooks import SiteActions
from app.objects.abstract_objects.abstract_form import File, Form
from app.web.html.html import (
    Html,
    html_joined_list_as_paragraphs,
)
from app.web.html.master_layout import master_layout_html
from app.web.html.process_abstract_form_to_html import (
    process_abstract_form_to_html,
)
from app.web.flask.flash import get_html_of_flashed_messages
from app.web.flask.interface import flaskInterface
from flask import send_file, Response


### Returns HTML for an 'action', non menu page
def generate_action_page_html(action_name: str) -> Union[Html, Response]:
    site_actions = SiteActions()
    print("getting html for %s" % action_name)

    abstract_form_for_action = site_actions.get_abstract_form_for_specific_action(
        action_name
    )

    if type(abstract_form_for_action) is File:
        return send_file(abstract_form_for_action.path_and_filename, as_attachment=True)

    html_code_for_action_in_layout = from_abstract_to_laid_out_html(
        abstract_form_for_action=abstract_form_for_action, action_name=action_name
    )

    return html_code_for_action_in_layout


def from_abstract_to_laid_out_html(
    abstract_form_for_action: Form, action_name: str
) -> Html:
    interface = flaskInterface(action_name)
    html_code_for_action = process_abstract_form_to_html(
        abstract_form_for_action, interface=interface
    )

    html_code_for_action_in_layout = add_standard_layout_and_buttons_to_action_code(
        html_code_for_action
    )

    return html_code_for_action_in_layout


def add_standard_layout_and_buttons_to_action_code(html_code_for_action: Html) -> Html:
    flash_html = get_html_of_flashed_messages()
    html_code_with_buttons = html_joined_list_as_paragraphs(
        [flash_html, html_code_for_action]
    )
    html_code_for_action_in_layout = master_layout_html.wrap_around(
        html_code_with_buttons
    )

    return html_code_for_action_in_layout
