from app.web.flask.state_for_action import StateDataForAction
from app.backend.events import get_list_of_events
from app.objects.events import SORT_BY_START_DSC

from app.web.html.forms import form_html_wrapper, html_button
from app.web.html.html import Html, ListOfHtml

from app.web.events.constants import ADD_EVENT_BUTTON_LABEL, sort_buttons
from app.web.events.utils import row_of_form_for_event_with_buttons

def display_view_of_events(
    state_data: StateDataForAction, sort_by: str = SORT_BY_START_DSC
):
    list_of_events_with_buttons = display_list_of_events_with_buttons(sort_by=sort_by)
    add_button = html_button(ADD_EVENT_BUTTON_LABEL)

    html_inside_form = ListOfHtml(
        [
            sort_buttons,
            Html(
                "Click on any event to view/edit/delete/upload/allocate/anything else"
            ),
            add_button,
            list_of_events_with_buttons,
        ]
    ).join_as_paragraphs()

    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)


def display_list_of_events_with_buttons(sort_by=SORT_BY_START_DSC) -> Html:
    list_of_events = get_list_of_events(sort_by=sort_by)

    list_with_buttons = [
        row_of_form_for_event_with_buttons(event) for event in list_of_events
    ]
    list_with_buttons_as_single_str = ListOfHtml(list_with_buttons).join_as_lines()

    return Html(list_with_buttons_as_single_str)
