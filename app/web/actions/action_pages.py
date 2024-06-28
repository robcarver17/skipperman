from typing import Union
from app.web.actions.action_hooks import SiteActions
from app.objects.abstract_objects.abstract_form import File, Form
from app.web.html.components import (
    Html,
    html_joined_list_as_paragraphs,
)
from app.web.html.master_layout import get_master_layout
from app.web.html.process_abstract_form_to_html import (
    process_abstract_form_to_html,
)
from app.web.flask.flask_interface import get_urls_of_interest
from flask import send_file, Response


### Returns HTML for an 'action', non menu page
def generate_action_page_html(action_name: str) -> Union[Html, Response]:
    site_actions = SiteActions()
    print("getting html for %s" % action_name)

    abstract_form_for_action = site_actions.get_abstract_form_for_specific_action(
        action_name
    )

    if type(abstract_form_for_action) is File:
        print("Generating file %s" % abstract_form_for_action.path_and_filename)
        return send_file(abstract_form_for_action.path_and_filename, as_attachment=True)

    html_code_for_action_in_layout = from_abstract_to_laid_out_html(
        abstract_form_for_action=abstract_form_for_action, action_name=action_name
    )

    html_page_master_layout = get_master_layout(
        include_read_only_toggle=False, include_user_options=True
    )
    html_page_master_layout.body.append(html_code_for_action_in_layout)

    return html_page_master_layout.as_html()


def from_abstract_to_laid_out_html(
    abstract_form_for_action: Form, action_name: str
) -> Html:
    urls_of_interest = get_urls_of_interest(action_name)
    html_code_for_action = process_abstract_form_to_html(
        abstract_form_for_action, urls_of_interest=urls_of_interest
    )

    html_code_for_action_in_layout = add_standard_layout_and_buttons_to_action_code(
        html_code_for_action
    )

    return html_code_for_action_in_layout


def add_standard_layout_and_buttons_to_action_code(html_code_for_action: Html) -> Html:
    html_code_with_buttons = html_joined_list_as_paragraphs([html_code_for_action])

    return html_code_with_buttons
