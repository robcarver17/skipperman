from copy import copy
from typing import List

from app.frontend.menu_define import menu_definition, menu_security_dict
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    HelpButton,
    ActionOptionButton,
    ActionLink,
)
from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line, MainMenuBar
from app.web.flask.security import get_access_group_for_current_user
from app.web.html.url_define import MAIN_HELP_PAGE, get_action_first_page_url


def get_menu_as_abstract_objects() -> Form:
    nav_bar = get_nav_bar_for_main_menu()
    buttons = get_large_tiled_menu_buttons_for_actions()

    return Form(ListOfLines([nav_bar, buttons]).add_Lines())


def get_nav_bar_for_main_menu() -> ButtonBar:
    navbar = ButtonBar([HelpButton(MAIN_HELP_PAGE, from_main_menu=True)])

    return navbar


def get_button_bar_of_menu_buttons_for_actions(main_menu_bar: MainMenuBar):
    filtered_menu_definition = copy(filter_menu_for_user_permissions(menu_definition))
    try:
        filtered_menu_definition.pop(main_menu_bar.exclude_action)
    except:
        pass

    list_of_buttons = get_button_bar_menu_from_filtered_menu(
        filtered_menu_definition, open_new_window=main_menu_bar.open_new_window
    )

    return list_of_buttons


def get_large_tiled_menu_buttons_for_actions() -> Line:
    filtered_menu_definition = filter_menu_for_user_permissions(menu_definition)
    list_of_buttons = get_large_tiled_menu_buttons_from_filtered_menu(
        filtered_menu_definition
    )

    return Line(list_of_buttons)


def get_large_tiled_menu_buttons_from_filtered_menu(
    filtered_menu_definition: dict,
) -> List[ActionOptionButton]:
    list_of_buttons = []
    for label, action_name in filtered_menu_definition.items():
        list_of_buttons.append(
            ActionOptionButton(
                label=label,
                url=get_action_first_page_url(action_name),
            )
        )

    return list_of_buttons


def get_button_bar_menu_from_filtered_menu(
    filtered_menu_definition: dict, open_new_window: bool
) -> ButtonBar:
    list_of_buttons = []
    for label, action_name in filtered_menu_definition.items():
        list_of_buttons.append(
            ActionLink(
                action_name=action_name,
                action_label=label,
                open_new_window=open_new_window,
                on_submenu_bar=True,
            )
        )

    return ButtonBar(list_of_buttons)


def filter_menu_for_user_permissions(menu_definition: dict) -> dict:
    new_menu = dict(
        [
            (menu_option, action_name)
            for menu_option, action_name in menu_definition.items()
            if can_action_be_seen(action_name)
        ]
    )

    return new_menu


def can_action_be_seen(action_name: str) -> bool:
    list_of_allowed_groups = menu_security_dict.get(action_name, None)
    if list_of_allowed_groups is None:
        raise Exception("menu_security_dict doesn't include %s" % action_name)

    group = get_access_group_for_current_user()
    return group in list_of_allowed_groups
