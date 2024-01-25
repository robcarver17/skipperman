from app.web.flask.state_for_action import StateDataForAction
from app.web.html.forms import form_html_wrapper, html_button, BACK_BUTTON_LABEL
from app.web.html.html import (
    Html,
    html_joined_list_as_paragraphs,
    html_container_wrapper,
    html_strong_wraper,
    html_nav_wrapper,
    html_link,
)
from app.web.html.url import INDEX_URL


def back_button_only_with_text(state_data: StateDataForAction, some_text: str):
    form_wrapper = form_html_wrapper(state_data.current_url)
    form_contents = html_joined_list_as_paragraphs(
        [Html("%s" % some_text), html_button(BACK_BUTTON_LABEL)]
    )

    return form_wrapper.wrap_around(form_contents)


go_home_html = html_container_wrapper.wrap_around(
    html_strong_wraper.wrap_around(
        html_nav_wrapper.wrap_around(
            html_link("CANCEL: Back to home menu", url=INDEX_URL)
        )
    )
)
