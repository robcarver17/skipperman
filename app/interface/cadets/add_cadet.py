import datetime
from typing import Tuple

from app.interface.flask.state_for_action import StateDataForAction
from app.interface.html.html import Html, ListOfHtml, html_error, empty_html, html_bold
from app.interface.html.components import back_button_only_with_text
from app.interface.html.forms import form_html_wrapper, html_button, html_form_text_input, html_date_input, html_as_date
from app.interface.cadets.constants import BACK_BUTTON_LABEL, CHECK_BUTTON_LABEL, FIRST_NAME, SURNAME, DOB, FINAL_ADD_BUTTON_LABEL,  ADD_CADET_BUTTON_LABEL
from app.interface.cadets.view_cadets import display_view_of_cadets

from app.logic.cadets.add_cadet import add_new_verified_cadet, verify_cadet_and_warn
from app.objects.cadets import Cadet, default_cadet

from app.data_access.data_access import data

def get_view_for_add_cadet(state_data: StateDataForAction):
    ## don't need to check get/post as will always be post
    last_button_pressed = state_data.last_button_pressed()
    if last_button_pressed==ADD_CADET_BUTTON_LABEL:
        ## hasn't been displayed before, will have no defaults
        return display_form(state_data)

    elif last_button_pressed==CHECK_BUTTON_LABEL:
        ## verify results, display form again
        verification_text, form_values =process_form_when_checking_cadet(state_data)
        return display_form(state_data, verification_text=verification_text, form_values=form_values)

    elif last_button_pressed==FINAL_ADD_BUTTON_LABEL:
        return process_form_when_cadet_verified(state_data)

    elif last_button_pressed==BACK_BUTTON_LABEL:
        state_data.reset_to_initial_stage()
        return display_view_of_cadets(state_data)

    else:
        return html_error("Uknown button pressed - shouldn't happen!")


def display_form(state_data: StateDataForAction, form_values: Cadet = default_cadet,
                 verification_text: Html = empty_html):

    cadet_is_verified = form_values is not default_cadet
    header_text = Html("Add a new cadet")
    first_name = html_form_text_input(input_label="First name", input_name=FIRST_NAME, value = form_values.first_name)
    surname = html_form_text_input(input_label="Second name", input_name=SURNAME, value=form_values.surname)
    dob = html_date_input(input_label="Date of birth", input_name=DOB,
                          max_date_years=-5, min_date_years=40,
                          value=form_values.date_of_birth)

    footer_buttons = get_footer_buttons(cadet_is_verified=cadet_is_verified)

    list_of_html_inside_form = [header_text,
                                first_name,
                                surname,
                                dob,
                                verification_text,
                                footer_buttons
                                ]
    html_inside_form = ListOfHtml(list_of_html_inside_form).join_as_paragraphs()
    form = form_html_wrapper(state_data.current_url)

    return form.wrap_around(html_inside_form)


def process_form_when_checking_cadet(state_data: StateDataForAction) -> Tuple[Html, Cadet]:
    try:
        cadet = get_cadet_from_form(state_data)
        verify_text = html_bold(verify_cadet_and_warn(cadet=cadet, data=data))
    except:
        verify_text = html_bold("Doesn't appear to be a valid cadet (wrong date time in old browser?)")
        cadet = default_cadet

    return verify_text, cadet

def get_cadet_from_form(state_data: StateDataForAction) -> Cadet:
    first_name = state_data.value_from_form(FIRST_NAME)
    surname = state_data.value_from_form(SURNAME)
    date_of_birth=html_as_date(state_data.value_from_form(DOB))

    return Cadet(first_name=first_name, surname=surname, date_of_birth=date_of_birth)


def process_form_when_cadet_verified(state_data: StateDataForAction):
    try:
        cadet = get_cadet_from_form(state_data)
        add_new_verified_cadet(cadet, data)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        return html_error("Can't add this cadet, something weird has happened error code %s, try again" % str(e))

    return back_button_only_with_text(state_data=state_data,
                                      some_text="Added cadet %s" % str(cadet))



def get_footer_buttons(cadet_is_verified: bool):
    back = html_button(BACK_BUTTON_LABEL)
    final_submit = html_button(FINAL_ADD_BUTTON_LABEL)
    check_submit = html_button(CHECK_BUTTON_LABEL)
    if cadet_is_verified:
        return ListOfHtml([
            back,
            check_submit,
            final_submit
        ]).join()
    else:
        return ListOfHtml([
            back,
            check_submit
        ]).join()
