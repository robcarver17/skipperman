from app.web.end_points.underlying_menu_pages import get_menu_as_abstract_objects
from app.web.html.url_define import (
    get_urls_of_interest,
)

from app.web.html.process_abstract_form_to_html import (
    process_abstract_objects_to_html,
)

from app.web.flask.security import authenticated_user
from app.web.html.html_components import Html
from app.web.html.master_layout import get_master_layout
from app.web.flask.security import allow_user_to_make_snapshots


### Returns HTML for a menu page
def generate_menu_page_html() -> str:
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
    urls_of_interest = get_urls_of_interest()

    menu_as_form = get_menu_as_abstract_objects()
    menu_as_html = process_abstract_objects_to_html(
        menu_as_form, urls_of_interest=urls_of_interest
    )

    return menu_as_html
