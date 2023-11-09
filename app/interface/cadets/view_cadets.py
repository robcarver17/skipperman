from app.interface.cadets.constants import sort_buttons, ADD_CADET_BUTTON_LABEL
from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import Html, ListOfHtml
from app.interface.html.forms import form_html_wrapper, html_button
from app.logic.cadets.view_cadets import SORT_BY_SURNAME, get_list_of_cadets

add_button = html_button(ADD_CADET_BUTTON_LABEL)

def display_view_of_cadets(
    state_data: StateDataForAction, sort_order=SORT_BY_SURNAME
) -> Html:
    list_of_cadets_with_buttons = display_list_of_cadets_with_buttons(
        sort_order=sort_order
    )

    html_inside_form = ListOfHtml(
        [
            sort_buttons,
            Html("Click on any cadet to view/edit/delete"),
            add_button,
            list_of_cadets_with_buttons,
        ]
    ).join_as_paragraphs()

    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)


def display_list_of_cadets_with_buttons(sort_order=SORT_BY_SURNAME) -> Html:
    list_of_cadets = get_list_of_cadets(sort_by=sort_order)

    list_with_buttons = [
        row_of_form_for_cadets_with_buttons(cadet) for cadet in list_of_cadets
    ]
    list_with_buttons_as_single_str = ListOfHtml(list_with_buttons).join_as_lines()

    return Html(list_with_buttons_as_single_str)

def row_of_form_for_cadets_with_buttons(cadet) -> Html:
    return html_button(str(cadet))