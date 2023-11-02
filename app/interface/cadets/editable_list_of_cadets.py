from app.interface.flask.state_for_action import StateDataForAction
from app.data_access.data_access import make_data
data = make_data()
from app.logic.cadets.view_cadets import get_list_of_cadets, SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, \
    SORT_BY_DOB_DSC

from app.interface.html.html import Html, html_paragraph_line_wrapper, ListOfHtml, html_error
from app.interface.html.forms import form_html_wrapper, html_button

## BUTTONS
ADD_CADET = "Add cadet"

## STAGES
VIEW_CADET="view_cadet"

## VAR NAMES
CADET = "cadet"

def editable_list_of_cadets(state_data: StateDataForAction) -> Html:
    print(state_data)
    if state_data.is_initial_stage:
        return display_or_respond_with_view_of_cadets(state_data)
    elif state_data.stage==VIEW_CADET:
        pass

## INITIAL STAGE

def display_or_respond_with_view_of_cadets(state_data: StateDataForAction) -> Html:
    if state_data.is_post:
        return post_view_of_cadets(state_data)
    else:
        return display_view_of_cadets(state_data)

## INITIAL STAGE: VIEW

def display_view_of_cadets(state_data: StateDataForAction, sort_order = SORT_BY_SURNAME) -> Html:
    list_of_cadets_with_buttons = display_list_of_cadets_with_buttons(sort_order=sort_order)

    html_inside_form = ListOfHtml([
        sort_buttons,
        Html("Click on any cadet to view/edit/delete"),
        add_button,
        list_of_cadets_with_buttons]
    ).join_as_paragraphs()

    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)

add_button = html_button(ADD_CADET)

all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC]
sort_buttons = ListOfHtml([
    html_button(sortby) for sortby in all_sort_types
                          ]).join()

def display_list_of_cadets_with_buttons( sort_order=SORT_BY_SURNAME) -> Html:
    list_of_cadets = get_list_of_cadets(data, sort_by=sort_order)

    list_with_buttons = [row_of_form_for_cadets_with_buttons(
        cadet
    ) for cadet in list_of_cadets]
    list_with_buttons_as_single_str = ListOfHtml(list_with_buttons).join_as_lines()

    return Html(list_with_buttons_as_single_str)

def row_of_form_for_cadets_with_buttons(cadet)-> Html:
    return html_button(str(cadet))

## INITIAL STAGE: POST

def post_view_of_cadets(state_data: StateDataForAction):
    button_pressed = state_data.last_button_pressed()
    if button_pressed==ADD_CADET:
        pass
    elif button_pressed in all_sort_types:
        return post_view_of_cadets_with_sort_selected(state_data)
    else:
        return post_view_of_cadets_with_cadet_selected(state_data)

def post_view_of_cadets_with_sort_selected(state_data: StateDataForAction):
    sort_order =state_data.last_button_pressed()

    return display_view_of_cadets(state_data, sort_order=sort_order)

def post_view_of_cadets_with_cadet_selected(state_data: StateDataForAction):
    cadet_selected = state_data.last_button_pressed()

    list_of_cadets_as_str = [str(cadet) for cadet in get_list_of_cadets(data)]
    try:
        assert cadet_selected in list_of_cadets_as_str
    except:
        return html_error("Cadet %s no longer in list- someone else has deleted or file corruption?" % cadet_selected)

    print(state_data.stage)
    print(state_data.session_data.other_data)
    update_state_for_specific_cadet(state_data=state_data, cadet_selected=cadet_selected)
    print(state_data.stage)
    print(state_data.session_data.other_data)

    return Html("%s %s" % (state_data.stage,get_specific_cadet_from_state(state_data)))

def update_state_for_specific_cadet(state_data: StateDataForAction, cadet_selected: str):
    state_data.set_value(CADET, cadet_selected)
    state_data.stage = VIEW_CADET

def get_specific_cadet_from_state(state_data: StateDataForAction) ->str:
    return state_data.get_value(CADET)

# FIXME DON'T FORGET BACK BUTTON WHEN VIEWING CADETS OR OTHER ACTIONS
