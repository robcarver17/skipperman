from app.interface.action_hooks import SiteActions
from app.interface.html.html import (
    Html,
    html_joined_list_as_paragraphs,
    html_joined_list_as_lines,
)
from app.interface.html.master_layout import master_layout_html
from app.interface.flask.flash import get_html_of_flashed_messages


### Returns HTML for an 'action', non menu page
def generate_action_page_html(action_option: str) -> Html:
    html_code_for_action = action_html_inner_code(action_option)
    html_code_for_action_in_layout = add_standard_layout_and_buttons_to_action_code(
        html_code_for_action
    )

    return html_code_for_action_in_layout


def action_html_inner_code(action_name: str) -> Html:
    html_actions = SiteActions()
    print("getting html for %s" % action_name)
    html_code_for_action = html_actions.get_html_for_action(action_name=action_name)

    return html_code_for_action


def add_standard_layout_and_buttons_to_action_code(html_code_for_action: Html) -> Html:
    flash_html = get_html_of_flashed_messages()
    html_code_with_buttons = html_joined_list_as_paragraphs(
        [ flash_html, html_code_for_action]
    )
    html_code_for_action_in_layout = master_layout_html.wrap_around(
        html_code_with_buttons
    )

    return html_code_for_action_in_layout
