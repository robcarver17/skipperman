from copy import copy
from typing import Tuple

from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import (
    Html,
    empty_html,
    html_bold,
    html_joined_list,
    html_joined_list_as_paragraphs,
)
from app.interface.flask.flash import html_error, flash_error
from app.interface.html.components import back_button_only_with_text, BACK_BUTTON_LABEL
from app.interface.html.forms import (
    form_html_wrapper,
    html_button,
    html_form_text_input,
    html_date_input,
    html_as_date,
)
from app.interface.cadets.constants import (
     CHECK_BUTTON_LABEL,
    FIRST_NAME,
    SURNAME,
    DOB,
    FINAL_ADD_BUTTON_LABEL,
    ADD_CADET_BUTTON_LABEL,
)
from app.interface.cadets.view_cadets import display_view_of_cadets

from app.logic.cadets.add_cadet import (
    add_new_verified_cadet,
    verify_cadet_and_warn,
)
from app.objects.cadets import Cadet, default_cadet


def display_view_for_add_cadet(state_data: StateDataForAction):
    ## don't need to check get/post as will always be post
    last_button_pressed = state_data.last_button_pressed()
    if last_button_pressed == ADD_CADET_BUTTON_LABEL:
        ## hasn't been displayed before, will have no defaults
        return get_add_cadet_form(
            state_data=state_data,
            first_time_displayed=True
        )

    elif last_button_pressed == CHECK_BUTTON_LABEL:
        ## verify results, display form again
        return get_add_cadet_form(
            state_data=state_data,
            first_time_displayed=False
        )

    elif last_button_pressed == FINAL_ADD_BUTTON_LABEL:
        return process_form_when_cadet_verified(state_data)

    elif last_button_pressed == BACK_BUTTON_LABEL:
        return reset_stage_and_return_previous(state_data)

    else:
        return html_error("Uknown button pressed - shouldn't happen!")



def get_add_cadet_form(    state_data: StateDataForAction,
                           first_time_displayed: bool = True):
    if first_time_displayed:
        footer_buttons_html = get_footer_buttons_for_add_cadet_form(form_is_empty=True)
        return get_add_cadet_form_with_information_passed(
            state_data, footer_buttons_html=footer_buttons_html
        )
    else:
        verification_text, cadet = verify_form_with_cadet_details(state_data)
        form_is_empty = cadet == default_cadet
        footer_buttons_html = get_footer_buttons_for_add_cadet_form(form_is_empty)

        return get_add_cadet_form_with_information_passed(
            state_data,
            verification_text=verification_text,
            cadet=cadet,
            footer_buttons_html=footer_buttons_html,
        )


def get_add_cadet_form_with_information_passed(
    state_data: StateDataForAction,
    cadet: Cadet = default_cadet,
    verification_text: Html = empty_html,
    footer_buttons_html: Html = empty_html,
    header_text: str = "Add a new cadet",
) -> Html:
    print("add cadet form")
    html_inside_form = get_html_inside_add_cadet_form(
        cadet=cadet,
        verification_text=verification_text,
        footer_buttons_html=footer_buttons_html,
        header_text=header_text,
    )
    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)


def get_html_inside_add_cadet_form(
    cadet: Cadet = default_cadet,
    verification_text: Html = empty_html,
    footer_buttons_html: Html = empty_html,
    header_text: str = "Add a new cadet",
):

    header_text = Html(header_text)
    form_fields = form_fields_for_add_cadet(cadet)

    list_of_html_inside_form = [
        header_text,
        form_fields,
        verification_text,
        footer_buttons_html,
    ]
    html_inside_form = html_joined_list_as_paragraphs(list_of_html_inside_form)

    return html_inside_form


def form_fields_for_add_cadet(cadet: Cadet):
    first_name = html_form_text_input(
        input_label="First name", input_name=FIRST_NAME, value=cadet.first_name
    )
    surname = html_form_text_input(
        input_label="Second name", input_name=SURNAME, value=cadet.surname
    )
    dob = html_date_input(
        input_label="Date of birth",
        input_name=DOB,
        value=cadet.date_of_birth,
    )

    form_fields = html_joined_list([first_name, surname, dob])

    return form_fields


def verify_form_with_cadet_details(
    state_data: StateDataForAction, default=default_cadet
) -> Tuple[Html, Cadet]:
    try:
        cadet = get_cadet_from_form(state_data)
        verify_text = html_bold(verify_cadet_and_warn(cadet=cadet))
    except:
        verify_text = html_bold(
            "Doesn't appear to be a valid cadet (wrong date time in old browser?)"
        )
        cadet = copy(default)

    return verify_text, cadet


def get_cadet_from_form(state_data: StateDataForAction) -> Cadet:
    first_name = state_data.value_from_form(FIRST_NAME).strip().title()
    surname = state_data.value_from_form(SURNAME).strip().title()
    date_of_birth = html_as_date(state_data.value_from_form(DOB))

    return Cadet(first_name=first_name, surname=surname, date_of_birth=date_of_birth)


def process_form_when_cadet_verified(state_data: StateDataForAction):
    try:
        cadet = add_cadet_from_form_to_data(state_data)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        return html_error(
            "Can't add this cadet, something weird has happened error code %s, try again"
            % str(e)
        )

    return back_button_only_with_text(
        state_data=state_data, some_text="Added cadet %s" % str(cadet)
    )


def add_cadet_from_form_to_data(state_data: StateDataForAction):
    cadet = get_cadet_from_form(state_data)
    add_new_verified_cadet(cadet)

    return cadet


def get_footer_buttons_for_add_cadet_form(form_is_empty: bool):
    back = html_button(BACK_BUTTON_LABEL)
    final_submit = html_button(FINAL_ADD_BUTTON_LABEL)
    check_submit = html_button(CHECK_BUTTON_LABEL)
    if form_is_empty:
        return html_joined_list([back, check_submit])
    else:
        return html_joined_list([back, check_submit, final_submit])


def reset_stage_and_return_previous(
    state_data: StateDataForAction, error_msg: str = ""
):
    if error_msg is not "":
        flash_error(error_msg)
    state_data.clear_session_data_for_action_and_reset_stage()
    return display_view_of_cadets(state_data)
