from app.interface.events.constants import (
    CHECK_CADET_BUTTON_LABEL,
    FINAL_CADET_ADD_BUTTON_LABEL,
    SEE_ALL_CADETS_BUTTON_LABEL,
    SEE_SIMILAR_CADETS_ONLY_LABEL,
)
from app.interface.html.forms import html_button
from app.interface.html.html import html_joined_list, html_joined_list_as_lines, Html
from app.logic.cadets.add_cadet import list_of_similar_cadets
from app.logic.cadets.backend import get_list_of_cadets, SORT_BY_FIRSTNAME

from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import html_bold, Html
from app.interface.cadets.add_cadet import (
    get_add_cadet_form_with_information_passed,verify_form_with_cadet_details
)
from app.interface.events.constants import (
    CHECK_CADET_BUTTON_LABEL,
    FINAL_CADET_ADD_BUTTON_LABEL,
    SEE_ALL_CADETS_BUTTON_LABEL,
    SEE_SIMILAR_CADETS_ONLY_LABEL,
)

from app.logic.cadets.view_cadets import get_list_of_cadets
from app.logic.cadets.add_cadet import verify_cadet_and_warn

from app.objects.cadets import Cadet
from app.objects.constants import arg_not_passed

def get_add_or_select_existing_cadet_form(state_data: StateDataForAction,
                                          see_all_cadets:bool,
                                          include_final_button: bool,
                                          cadet: Cadet = arg_not_passed) -> Html:
    print("Generating add/select cadet form")
    if cadet is arg_not_passed:
        ## get initial verification
        verification_text, cadet = verify_form_with_cadet_details(state_data)
    else:
        verification_text = verify_cadet_and_warn(cadet)

    ## First time, don't include final or all cadets
    footer_buttons_html = get_footer_buttons_add_or_select_existing_cadets_form(cadet, see_all_cadets=see_all_cadets,
                                                                                include_final_button=include_final_button)
    # Custom header text
    header_text = "Looks like a new cadet in the WA entry file. You can edit them, check their details and then add, or choose an existing cadet instead (avoid creating duplicates!)"
    return get_add_cadet_form_with_information_passed(
        state_data,
        verification_text=verification_text,
        cadet=cadet,
        footer_buttons_html=footer_buttons_html,
        header_text=header_text,
    )


def get_footer_buttons_add_or_select_existing_cadets_form(cadet: Cadet, see_all_cadets: bool = False,
                                                          include_final_button: bool = False) -> Html:
    main_buttons = get_html_list_of_main_buttons(include_final_button)

    cadet_buttons_html = get_html_list_of_cadet_buttons(
        cadet, see_all_cadets=see_all_cadets
    )

    return html_joined_list_as_lines([main_buttons, cadet_buttons_html])

def get_html_list_of_main_buttons(include_final_button: bool):
    check = html_button(CHECK_CADET_BUTTON_LABEL)
    add = html_button(FINAL_CADET_ADD_BUTTON_LABEL)

    if include_final_button:
        main_buttons = html_joined_list([check, add])
    else:
        main_buttons = check

    return main_buttons

def get_html_list_of_cadet_buttons(cadet: Cadet, see_all_cadets: bool = False):
    if see_all_cadets:
        list_of_cadets = get_list_of_cadets(sort_by=SORT_BY_FIRSTNAME)
        extra_button = html_button(SEE_SIMILAR_CADETS_ONLY_LABEL)
    else:
        ## similar cadets with option to see more
        list_of_cadets = list_of_similar_cadets(cadet)
        extra_button = html_button(SEE_ALL_CADETS_BUTTON_LABEL)

    cadets_as_buttons = html_joined_list(
        [html_button(str(cadet)) for cadet in list_of_cadets]
    )

    cadet_buttons_html = html_joined_list_as_lines([extra_button, cadets_as_buttons])

    return cadet_buttons_html
