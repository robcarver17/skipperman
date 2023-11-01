from app.interface.events.constants import BACK_BUTTON_LABEL
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.forms import form_html_wrapper, html_button
from app.interface.html.html import ListOfHtml, Html


def back_button_only_with_text(state_data: StateDataForAction, some_text: str):
    form_html_wrapper(state_data.current_url).wrap_around(
        ListOfHtml([
            Html("%s" % some_text),
            html_button(BACK_BUTTON_LABEL)
        ]).join_as_paragraphs())