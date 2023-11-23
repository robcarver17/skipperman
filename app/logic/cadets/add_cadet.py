from dataclasses import dataclass
from copy import copy
from typing import Union, Tuple
from app.logic.abstract_form import Form, NewForm,Line, ListOfLines, Button, dateInput, textInput, form_with_message_and_finished_button, _______________, cancel_button
from app.logic.cadets.constants import CHECK_BUTTON_LABEL, FINAL_ADD_BUTTON_LABEL, FIRST_NAME, \
    SURNAME, DOB

from app.objects.cadets import Cadet, is_cadet_age_surprising, default_cadet
from app.data_access.data import data
from app.logic.abstract_interface import abstractInterface
from app.logic.abstract_logic_api import initial_state_form


from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_DATE,
    SIMILARITY_LEVEL_TO_WARN_NAME,
    MIN_CADET_AGE,
    MAX_CADET_AGE,
)


def display_form_add_cadet(
    interface: abstractInterface,
        first_time_displayed: bool = True
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if first_time_displayed:
        ## hasn't been displayed before, will have no defaults
        return get_add_cadet_form(
            interface=interface,
            first_time_displayed=True
        )

    elif last_button_pressed == CHECK_BUTTON_LABEL:
        ## verify results, display form again
        return get_add_cadet_form(
            interface=interface,
            first_time_displayed=False
        )

    elif last_button_pressed == FINAL_ADD_BUTTON_LABEL:
        return process_form_when_cadet_verified(interface)

    else:
        interface.log_error("Uknown button pressed %s - shouldn't happen!" % last_button_pressed)
        return initial_state_form

@dataclass
class CadetAndVerificationText:
    cadet: Cadet
    verification_text: str = ""

    @property
    def is_default(self) -> bool:
        return self.cadet is default_cadet

default_cadet_and_text = CadetAndVerificationText(cadet=default_cadet, verification_text="")

def post_form_add_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    return display_form_add_cadet(interface, first_time_displayed = False)


def get_add_cadet_form(interface: abstractInterface,
                           first_time_displayed: bool = True) -> Form:
    if first_time_displayed:
        footer_buttons = get_footer_buttons_for_add_cadet_form(form_is_empty=True)
        return get_add_cadet_form_with_information_passed(
            footer_buttons=footer_buttons
        )
    else:
        cadet_and_text = verify_form_with_cadet_details(interface)
        form_is_empty = cadet_and_text.is_default
        footer_buttons = get_footer_buttons_for_add_cadet_form(form_is_empty)

        return get_add_cadet_form_with_information_passed(
            cadet_and_text=cadet_and_text,
            footer_buttons=footer_buttons,
        )


def get_add_cadet_form_with_information_passed(
    footer_buttons: Union[Line, ListOfLines],
    header_text: str = "Add a new cadet",
    cadet_and_text: CadetAndVerificationText = default_cadet_and_text
) -> Form:
    print("add cadet form")
    form_fields = form_fields_for_add_cadet(cadet_and_text.cadet)

    list_of_lines_inside_form = ListOfLines([
        header_text,
        _______________,
        form_fields,
        _______________,
        cadet_and_text.verification_text,
        _______________,
        footer_buttons,
    ])

    return Form(list_of_lines_inside_form)


def form_fields_for_add_cadet(cadet: Cadet):
    first_name = textInput(
        input_label="First name", input_name=FIRST_NAME, value=cadet.first_name
    )
    surname = textInput(
        input_label="Second name", input_name=SURNAME, value=cadet.surname
    )
    dob = dateInput(
        input_label="Date of birth",
        input_name=DOB,
        value=cadet.date_of_birth,
    )

    form_fields = ListOfLines([Line(first_name), Line(surname), Line(dob)])

    return form_fields



def verify_form_with_cadet_details(
    interface: abstractInterface, default=default_cadet
) -> CadetAndVerificationText:
    try:
        cadet = get_cadet_from_form(interface)
        verify_text = verify_cadet_and_warn(cadet=cadet)
    except:
        cadet = copy(default)
        verify_text = \
            "Doesn't appear to be a valid cadet (wrong date time in old browser?)"

    return CadetAndVerificationText(cadet=cadet, verification_text=verify_text)


def get_cadet_from_form(interface: abstractInterface) -> Cadet:
    first_name = interface.value_from_form(FIRST_NAME).strip().title()
    surname = interface.value_from_form(SURNAME).strip().title()
    date_of_birth = interface.value_from_form(DOB)

    return Cadet(first_name=first_name, surname=surname, date_of_birth=date_of_birth)


def process_form_when_cadet_verified(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        cadet = add_cadet_from_form_to_data(interface)
    except Exception as e:
        ## should never happen as we have to be verified to get here, but still
        interface.log_error(
            "Can't add this cadet, something weird has happened error code %s, try again"
            % str(e)
        )
        return initial_state_form

    return form_with_message_and_finished_button("Added cadet %s" % str(cadet))


def add_cadet_from_form_to_data(interface) -> Cadet:
    cadet = get_cadet_from_form(interface)
    add_new_verified_cadet(cadet)

    return cadet


def get_footer_buttons_for_add_cadet_form(form_is_empty: bool) -> Line:
    final_submit = Button(FINAL_ADD_BUTTON_LABEL)
    check_submit = Button(CHECK_BUTTON_LABEL)
    if form_is_empty:
        return Line([cancel_button, check_submit])
    else:
        return Line([cancel_button, check_submit, final_submit])




LOWEST_FEASIBLE_CADET_AGE = MIN_CADET_AGE - 2
HIGHEST_FEASIBLE_CADET_AGE = MAX_CADET_AGE + 20  ## might be backfilling


def verify_cadet_and_warn(cadet: Cadet) -> str:
    warn_text = ""
    if len(cadet.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(cadet.first_name) < 4:
        warn_text += "First name seems too short. "
    if is_cadet_age_surprising(cadet):
        warn_text += "Cadet seems awfully old or young."
    warn_text += warning_for_similar_cadets(cadet=cadet)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def warning_for_similar_cadets(cadet: Cadet) -> str:
    similar_cadets = list_of_similar_cadets(cadet)

    if len(similar_cadets) > 0:
        similar_cadets_str = ", ".join(
            [str(other_cadet) for other_cadet in similar_cadets]
        )
        ## Some similar cadets, let's see if it's a match
        return "Following cadets look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""


def list_of_similar_cadets(cadet: Cadet) -> list:
    existing_cadets = data.data_list_of_cadets.read()
    similar_cadets = existing_cadets.similar_cadets(
        cadet,
        name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME,
        dob_threshold=SIMILARITY_LEVEL_TO_WARN_DATE,
    )

    return similar_cadets


def add_new_verified_cadet(cadet: Cadet):
    data.data_list_of_cadets.add(cadet)
