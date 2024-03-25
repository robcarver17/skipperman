from app.web.flask.flash import get_html_of_flashed_messages
from app.web.flask.security import get_access_group_for_current_user, get_username, authenticated_user
from app.web.html.login_and_out import login_link_html_code, logout_link_html_code
from app.web.html.url import HOME, INDEX_URL, get_menu_url, get_action_url
from app.web.html.html import (
    Html,
    html_link,
    html_link_in_list_item,
    html_link_with_nested_list,
    HtmlWrapper,
    ListOfHtml,
)
from app.web.html.html import (
    html_container_wrapper,
    html_strong_wraper,
    html_nav_wrapper,
    html_unordered_list_menu_class_wrapper,
)
from app.web.html.master_layout import master_layout_html
from app.web.flask.session_data_for_action import (
    clear_session_data_for_all_actions,
)
from app.web.menu_define import menu_definition, menu_security_dict



### Returns HTML for a menu page
def generate_menu_page_html(menu_option: str = HOME) -> str:
    ## We do this so on subsequently entering a particular action we have no state saved
    clear_session_data_for_all_actions()


    ## hide if logged out EXCEPT public
    if authenticated_user():
        html_code_for_menu = generate_menu_html(menu_option)
    else:
        html_code_for_menu = "Login to see options"


    login_or_out_code = login_or_out()
    messages = get_html_of_flashed_messages()

    html_code_for_menu_inside_layout = master_layout_html.wrap_around(
        messages+html_code_for_menu+login_or_out_code
    )
    return html_code_for_menu_inside_layout


def generate_menu_html(menu_option: str = HOME) -> Html:
    logged_in_as =html_container_wrapper.wrap_around("Logged in as %s" % get_username())
    inner_html_menu_code = generate_menu_inner_html(menu_option)

    return logged_in_as+ menu_layout_html_wrapper.wrap_around(inner_html_menu_code)


def generate_menu_inner_html(menu_option: str) -> Html:
    return parse_menu_option_into_html(menu_option, menu_definition)


## recursive menu generator
LEVEL_SEPERATOR = "-"  ## used


def parse_menu_option_into_html(
    menu_option: str,
    current_menu_definition: dict,
    breadcrumbs: str = "",
    top_level: bool = True,
) -> Html:
    menu_option_as_list = menu_option.split(LEVEL_SEPERATOR)
    first_part_of_menu_option = menu_option_as_list[0]
    list_of_html_to_return = ListOfHtml()
    if top_level:
        ## include home
        list_of_html_to_return.append(html_link(string=HOME, url=INDEX_URL))

    for name_of_option, contents_of_option in current_menu_definition.items():
        # cycle through shared at this level
        if type(contents_of_option) is str:
            ## Nothing inside this, must be an action: return an action rather than menu link
            if can_action_be_seen(contents_of_option):
                link_this_option = get_action_url(contents_of_option)
                html_this_option = html_link_in_list_item(
                    string=name_of_option, url=link_this_option
                )
            else:
                html_this_option=""
        else:
            ## it's a dict, so we have submenus
            option_with_underscores = name_of_option.replace(" ", "_")
            link_this_menu = get_menu_url(breadcrumbs + option_with_underscores)

            if first_part_of_menu_option == option_with_underscores:
                ## we are in this submenu so need to expand
                sub_menu_as_list = menu_option_as_list[1:]
                sub_menu_option = LEVEL_SEPERATOR.join(sub_menu_as_list)
                breadcrumbs_to_prefix_submenu_names = (
                    breadcrumbs + option_with_underscores + LEVEL_SEPERATOR
                )
                sub_menu_definition = current_menu_definition[name_of_option]

                sub_menu_html = parse_menu_option_into_html(
                    menu_option=sub_menu_option,
                    current_menu_definition=sub_menu_definition,
                    breadcrumbs=breadcrumbs_to_prefix_submenu_names,
                    top_level=False,
                )
                html_this_option = html_link_with_nested_list(
                    url=link_this_menu,
                    string=name_of_option,
                    nested_list_to_wrap=sub_menu_html,
                )
            else:
                ## no sub menus to be expanded, include : so visually can be expanded
                html_this_option = html_link_in_list_item(
                    url=link_this_menu, string=name_of_option + ":"
                )

        list_of_html_to_return.append(html_this_option)

    html_to_return = list_of_html_to_return.join_as_paragraphs()

    return html_to_return


menu_layout_html_wrapper = HtmlWrapper(
    html_container_wrapper.wrap_around(
        html_strong_wraper.wrap_around(
            html_nav_wrapper.wrap_around(
                html_unordered_list_menu_class_wrapper.wrap_around(Html("%s"))
            )
        )
    )
)

def login_or_out() -> Html:

    if authenticated_user():
        return logout_link_html_code
    else:
        return login_link_html_code


def can_action_be_seen(action_name):
    list_of_allowed_groups = menu_security_dict.get(action_name, None)
    if list_of_allowed_groups is None:
        raise Exception("menu_security_dict doesn't include %s" % action_name)

    group = get_access_group_for_current_user()
    print("is %s in %s" % (group.name, str(list_of_allowed_groups)))
    return group in list_of_allowed_groups
