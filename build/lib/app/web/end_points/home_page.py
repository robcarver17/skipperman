from typing import List

from app.web.flask.session_data_for_action import (
    clear_all_action_state_data_from_session,
)
from app.web.html.url_define import (
    MAIN_HELP_PAGE, get_top_level_url,
)

from app.objects.abstract_objects.abstract_lines import ListOfLines, Line

from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_buttons import (
    HelpButton,
    ButtonBar,
    ActionOptionButton,
)

from app.web.html.process_abstract_form_to_html import (
    process_abstract_objects_to_html,
)

from app.web.flask.security import get_access_group_for_current_user, authenticated_user
from app.web.html.html_components import Html
from app.web.html.master_layout import get_master_layout
from app.frontend.menu_define import menu_definition
from app.web.flask.security import allow_user_to_make_snapshots


### Returns HTML for a menu page
def generate_home_page_html() -> str:
    ## hide if logged out EXCEPT public
    if authenticated_user():
        html_code_for_menu = generate_menu_html()
    else:
        html_code_for_menu = ""

    include_backup_option = allow_user_to_make_snapshots()
    html_page_master_layout = get_master_layout(
        include_read_only_toggle=True,
        include_user_options=True,
        include_backup_option=include_backup_option,
    )
    html_page_master_layout.body.append(html_code_for_menu)

    return html_page_master_layout.as_html()

def generate_menu_html() -> Html:

    menu_as_form = get_menu_as_abstract_objects()
    menu_as_html = process_abstract_objects_to_html(
        menu_as_form
    )

    return menu_as_html

def get_menu_as_abstract_objects() -> Form:
    nav_bar = get_nav_bar_for_main_menu()
    buttons = get_menu_buttons_for_actions()

    return Form(ListOfLines([nav_bar, buttons]).add_Lines())


def get_nav_bar_for_main_menu() -> ButtonBar:
    navbar = ButtonBar([HelpButton(MAIN_HELP_PAGE, from_main_menu=True)])

    return navbar


def get_menu_buttons_for_actions() -> Line:
    filtered_menu_definition = filter_menu_for_user_permissions(menu_definition)
    list_of_buttons = get_menu_buttons_from_filtered_menu(filtered_menu_definition)

    return Line(list_of_buttons)

def filter_menu_for_user_permissions(menu_definition: dict) -> dict:
    """
    new_menu = dict(
        [
            (menu_option, action_name)
            for menu_option, action_name in menu_definition.items()
            if can_action_be_seen(action_name)
        ]
    )
    """
    return menu_definition

def get_menu_buttons_from_filtered_menu(
    filtered_menu_definition: dict,
) -> List[ActionOptionButton]:
    list_of_buttons = []
    for label, option_name in filtered_menu_definition.items():
        list_of_buttons.append(
            ActionOptionButton(label=label, url=get_top_level_url(option_name))
        )

    return list_of_buttons
