from app.interface.events.constants import CHECK_CADET_BUTTON_LABEL, FINAL_CADET_ADD_BUTTON_LABEL, SEE_ALL_CADETS_BUTTON_LABEL, SEE_SIMILAR_CADETS_ONLY_LABEL
from app.interface.html.forms import html_button
from app.interface.html.html import html_joined_list, html_joined_list_as_lines
from app.logic.cadets.add_cadet import list_of_similar_cadets
from app.logic.cadets.view_cadets import get_list_of_cadets, SORT_BY_FIRSTNAME
from app.objects.cadets import Cadet


def get_footer_buttons(
    cadet: Cadet, see_all_cadets: bool = False, include_final: bool = False
):
    check = html_button(CHECK_CADET_BUTTON_LABEL)
    add = html_button(FINAL_CADET_ADD_BUTTON_LABEL)

    if include_final:
        main_buttons = html_joined_list([check, add])
    else:
        main_buttons = check

    cadet_buttons_html = get_html_list_of_cadet_buttons(cadet, see_all_cadets=see_all_cadets)

    return html_joined_list_as_lines([
        main_buttons,
        cadet_buttons_html
    ])


def get_html_list_of_cadet_buttons(cadet: Cadet, see_all_cadets: bool = False):
    if see_all_cadets:
        list_of_cadets = get_list_of_cadets(sort_by=SORT_BY_FIRSTNAME)
        list_of_cadets = [SEE_SIMILAR_CADETS_ONLY_LABEL]+list_of_cadets
    else:
        ## similar cadets with option to see more
        list_of_cadets = list_of_similar_cadets(cadet)
        list_of_cadets = [SEE_ALL_CADETS_BUTTON_LABEL]+list_of_cadets

    cadets_as_buttons = [html_button(str(cadet)) for cadet in list_of_cadets]

    return html_joined_list(cadets_as_buttons)