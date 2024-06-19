from app.web.flask.security import get_access_group_for_current_user, authenticated_user
from app.web.html.components import (
    Html,
    menu_item_for_action,
)
from app.web.html.components import (
    html_container_wrapper,
)
from app.web.html.master_layout import get_master_layout
from app.web.flask.session_data_for_action import (
    clear_session_data_for_all_actions,
)
from app.web.menu_define import menu_definition, menu_security_dict



### Returns HTML for a menu page
def generate_menu_page_html() -> str:
    ## hide if logged out EXCEPT public
    if authenticated_user():
        html_code_for_menu = generate_menu_html()
    else:
        html_code_for_menu = ""

    html_page_master_layout= get_master_layout(include_read_only_toggle=True,
                                               include_user_options=True,
                                               include_main_menu_help=True)
    html_page_master_layout.body.append(html_code_for_menu)

    return html_page_master_layout.as_html()


def generate_menu_html() -> Html:
    filtered_menu_definition = filter_menu_for_user_permissions(menu_definition)
    button_text = ""
    for label, action_name in filtered_menu_definition.items():
        button_text+= menu_item_for_action(label=label, action_name=action_name)

    return html_container_wrapper.wrap_around(button_text)


def filter_menu_for_user_permissions(menu_definition: dict):
    new_menu = dict([
        (url_ref, url) for url_ref, url in menu_definition.items()
        if can_action_be_seen(url)
    ])

    return new_menu

def can_action_be_seen(action_name):
    list_of_allowed_groups = menu_security_dict.get(action_name, None)
    if list_of_allowed_groups is None:
        raise Exception("menu_security_dict doesn't include %s" % action_name)

    group = get_access_group_for_current_user()
    print("is %s in %s" % (group.name, str(list_of_allowed_groups)))
    return group in list_of_allowed_groups
