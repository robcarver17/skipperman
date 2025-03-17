from dataclasses import dataclass
from typing import Union

from app.backend.cadets.list_of_cadets import (
    get_list_of_cadets_sorted_by_first_name,
    get_list_of_similar_cadets, get_cadet_from_list_of_cadets_given_str_of_cadet,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button, cancel_menu_button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.cadets.add_edit_cadet import verify_cadet_and_return_warnings
from app.frontend.shared.add_edit_cadet_form import (
    CadetAndVerificationText,
    get_add_cadet_form_with_information_passed,
    verify_form_with_cadet_details, get_cadet_from_form, add_cadet_from_form_to_data,
)

from app.objects.cadets import Cadet, sort_a_list_of_cadets
from app.objects.exceptions import arg_not_passed


@dataclass
class ParametersForGetOrSelectCadetForm:
    header_text: ListOfLines
    cancel_button: bool = False
    skip_button: bool = False
    final_add_button: bool = False
    see_all_cadets_button: bool = False
    sort_by: str = arg_not_passed
    help_string: str = arg_not_passed

def get_add_or_select_existing_cadet_form(
    interface: abstractInterface,
    parameters: ParametersForGetOrSelectCadetForm,
    cadet: Cadet = arg_not_passed,  ## Is passed only on first iteration when cadet is from data not form
) -> Form:

    cadet_and_text = get_cadet_and_verification_text(interface=interface, cadet=cadet)

    verification_text = cadet_and_text.verification_text
    cadet = cadet_and_text.cadet

    if len(verification_text) == 0:
        ## nothing to check, so can put add button up
        parameters.final_add_button = True

    ## First time, don't include final or all cadets
    footer_buttons = get_footer_buttons_add_or_select_existing_cadets_form(
        interface=interface,
        cadet=cadet,
        parameters=parameters
    )
    # Custom header text

    return get_add_cadet_form_with_information_passed(
        cadet_and_text=cadet_and_text,
        footer_buttons=footer_buttons,
        header_text=parameters.header_text,
        help_string = parameters.help_string
    )

def get_cadet_and_verification_text(interface: abstractInterface, cadet: Cadet = arg_not_passed) -> CadetAndVerificationText:
    if cadet is arg_not_passed:
        ## Form has been filled in, this isn't our first rodeo, get cadet from form
        cadet_and_text = verify_form_with_cadet_details(interface=interface)
    else:
        ## Cadet details as in WA passed through, uese these
        verification_text = verify_cadet_and_return_warnings(
            cadet=cadet, object_store=interface.object_store
        )
        cadet_and_text = CadetAndVerificationText(
            cadet=cadet, verification_text=verification_text
        )

    return cadet_and_text

def get_footer_buttons_add_or_select_existing_cadets_form(
    interface: abstractInterface,
    cadet: Cadet,
    parameters: ParametersForGetOrSelectCadetForm,

) -> ListOfLines:

    extra_buttons =get_extra_buttons(parameters)
    main_buttons = get_list_of_main_buttons(parameters)

    cadet_buttons = get_list_of_cadet_buttons(
        interface=interface, cadet=cadet, parameters=parameters
    )

    return ListOfLines([main_buttons, extra_buttons]+cadet_buttons)

def get_extra_buttons(parameters: ParametersForGetOrSelectCadetForm):
    extra_buttons = []
    if parameters.cancel_button:
        extra_buttons.append(cancel_menu_button)
    if parameters.skip_button:
        extra_buttons.append(skip_button)
    extra_buttons = Line(extra_buttons)

    return extra_buttons



def get_list_of_main_buttons(    parameters: ParametersForGetOrSelectCadetForm) -> Line:
    main_buttons = [check_cadet_for_me_button]
    if parameters.final_add_button:
        main_buttons.append(add_cadet_button)

    return Line(main_buttons)

def get_list_of_cadet_buttons(
    interface: abstractInterface, cadet: Cadet,     parameters: ParametersForGetOrSelectCadetForm,

) -> ListOfLines:
    if parameters.see_all_cadets_button:
        list_of_cadets = get_list_of_cadets_sorted_by_first_name(
            object_store=interface.object_store
        )
        msg = "Currently choosing from all cadets"
        state_button = see_similar_cadets_only_button
    else:
        ## similar cadets with option to see more
        list_of_cadets = get_list_of_similar_cadets(
            object_store=interface.object_store, cadet=cadet
        )
        msg = "Currently choosing from similar cadets only:"
        state_button = see_all_cadets_button


    list_of_cadets= sort_a_list_of_cadets(list_of_cadets)

    cadet_choice_buttons = Line([Button(str(cadet)) for cadet in list_of_cadets])

    return ListOfLines([Line([msg, state_button]), cadet_choice_buttons]).add_Lines()



@dataclass
class ResultFromAddOrSelect:
    form: Union[Form, NewForm] = arg_not_passed
    cadet: Cadet = arg_not_passed
    skip: bool = False
    cancel: bool = False
    cadet_was_added: bool = False

    @property
    def is_form(self):
        return not self.form is arg_not_passed

    @property
    def is_cadet(self):
        return not self.cadet is arg_not_passed


def generic_post_response_to_add_or_select_cadet(
    interface: abstractInterface,
parameters: ParametersForGetOrSelectCadetForm
) -> ResultFromAddOrSelect:

    last_button_pressed = interface.last_button_pressed()

    if response_requires_new_form(interface):
        return generic_post_response_to_add_or_select_when_returning_new_form(
            interface=interface,
            parameters=parameters
        )

    elif skip_button.pressed(last_button_pressed):
        return ResultFromAddOrSelect(skip=True)

    elif cancel_menu_button.pressed(last_button_pressed):
        return ResultFromAddOrSelect(cancel=True)

    elif add_cadet_button.pressed(last_button_pressed):
        cadet =add_cadet_from_form_to_data(interface)
        return ResultFromAddOrSelect(cadet=cadet, cadet_was_added=True)

    else:
        cadet = get_existing_cadet_selected_from_button(interface)
        return ResultFromAddOrSelect(cadet=cadet, cadet_was_added=False)

def response_requires_new_form(interface: abstractInterface):
    last_button_pressed = interface.last_button_pressed()
    return see_similar_cadets_only_button.pressed(
        last_button_pressed
    ) or check_cadet_for_me_button.pressed(last_button_pressed) or see_all_cadets_button.pressed(last_button_pressed)


def generic_post_response_to_add_or_select_when_returning_new_form(
    interface: abstractInterface,
parameters: ParametersForGetOrSelectCadetForm
) -> ResultFromAddOrSelect():

    last_button_pressed = interface.last_button_pressed()
    if see_similar_cadets_only_button.pressed(
        last_button_pressed
    ) or check_cadet_for_me_button.pressed(last_button_pressed):
        parameters.final_add_button = True
        parameters.see_all_cadets_button = False
        ## verify results already in form, display form again, allow final this time
        form = get_add_or_select_existing_cadet_form(
            interface=interface,
            parameters=parameters
        )

    elif see_all_cadets_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        parameters.final_add_button = True
        parameters.see_all_cadets_button = True
        form = get_add_or_select_existing_cadet_form(
            interface=interface,
            parameters=parameters
        )
    else:
        raise Exception("Not recognised!")

    return ResultFromAddOrSelect(
        form=form
        )



def get_existing_cadet_selected_from_button(interface: abstractInterface) -> Cadet:
    cadet_selected_as_str = interface.last_button_pressed()

    try:
        cadet = get_cadet_from_list_of_cadets_given_str_of_cadet(
            object_store=interface.object_store, cadet_selected=cadet_selected_as_str
        )
    except:
        raise Exception(
            "Cadet selected no longer exists - file corruption or someone deleted?",
        )

    return cadet

CHECK_CADET_FOR_ME_BUTTON_LABEL = "Please check the details again for me before I add"
FINAL_CADET_ADD_BUTTON_LABEL = "Yes - these details are correct - add this new cadet"
SEE_ALL_CADETS_BUTTON_LABEL = "Choose from all existing cadets"
SEE_SIMILAR_CADETS_ONLY_LABEL = "See similar cadets only"
SKIP_BUTTON_LABEL = (
    "Skip (do not use if it is a real cadet name)"
)

add_cadet_button = Button(FINAL_CADET_ADD_BUTTON_LABEL)
check_cadet_for_me_button = Button(CHECK_CADET_FOR_ME_BUTTON_LABEL)
see_similar_cadets_only_button = Button(SEE_SIMILAR_CADETS_ONLY_LABEL)
see_all_cadets_button = Button(SEE_ALL_CADETS_BUTTON_LABEL)
skip_button = Button(SKIP_BUTTON_LABEL)
