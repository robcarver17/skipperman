from copy import copy
from dataclasses import dataclass
from typing import Union

from app.backend.cadets.list_of_cadets import (
    get_list_of_cadets,
    get_list_of_similar_cadets_from_data, get_cadet_from_list_of_cadets_given_str_of_cadet,
)
from app.frontend.shared.buttons import break_up_buttons
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button, cancel_menu_button, \
    check_if_button_in_list_was_pressed
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.cadets.add_edit_cadet import verify_cadet_and_return_warnings
from app.frontend.shared.add_edit_cadet_form import (
    CadetAndVerificationText,
    get_add_cadet_form_with_information_passed,
    verify_form_with_cadet_details, add_cadet_from_form_to_data,
)

from app.objects.cadets import Cadet, default_cadet
from app.objects.utilities.cadet_matching_and_sorting import sort_a_list_of_cadets, SORT_BY_SURNAME, SORT_BY_FIRSTNAME, \
    SORT_BY_DOB_ASC, SORT_BY_DOB_DSC, SORT_BY_SIMILARITY_BOTH
from app.objects.utilities.exceptions import arg_not_passed
from app.data_access.configuration.configuration import SIMILARITY_LEVEL_TO_WARN_NAME

@dataclass
class ParametersForGetOrSelectCadetForm:
    header_text: ListOfLines
    help_string: str = arg_not_passed
    cancel_button: bool = False
    skip_button: bool = False
    final_add_button: bool = False
    see_all_cadets_button: bool = False
    default_cadet_passed: bool = False
    sort_by: str = SORT_BY_SIMILARITY_BOTH
    similarity_name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME

    def save_values_to_state(self, interface: abstractInterface):
        interface.set_persistent_value(SORT_BY_STATE, self.sort_by)
        interface.set_persistent_value(SEE_ALL_CADETS, self.see_all_cadets_button)
        interface.set_persistent_value(FINAL_ADD, self.final_add_button)

    def get_values_from_state(self, interface: abstractInterface):
        self.sort_by = interface.get_persistent_value(SORT_BY_STATE, SORT_BY_SIMILARITY_BOTH)
        self.final_add_button = interface.get_persistent_value(FINAL_ADD, False)
        self.see_all_cadets_button = interface.get_persistent_value(SEE_ALL_CADETS, False)

    def clear_values_in_state(self, interface: abstractInterface):
        for key in [SORT_BY_STATE, SEE_ALL_CADETS, FINAL_ADD]:
            interface.clear_persistent_value(key)

    def update_with_passed_cadet(self, cadet: Cadet):
        if cadet is default_cadet:
            self.default_cadet_passed = True
            self.see_all_cadets_button = True
        else:
            self.default_cadet_passed = False


SORT_BY_STATE = '*selectcadetform_sortyby'
SEE_ALL_CADETS = '*selectcadetform_seelall'
FINAL_ADD = "*selectcadtes_finaladd"

def get_add_or_select_existing_cadet_form(
    interface: abstractInterface,
    parameters: ParametersForGetOrSelectCadetForm,
    cadet: Cadet = arg_not_passed,  ## can be eithier cadet (passed from eg registration data), arg_not_passed (subsequent calls, get from form), or default_cadet
) -> Form:
    parameters.get_values_from_state(interface)
    parameters.update_with_passed_cadet(cadet)

    cadet_and_text = get_cadet_and_verification_text(interface=interface, cadet=cadet)

    ## First time, don't include final or all cadets
    footer_buttons = get_footer_buttons_add_or_select_existing_cadets_form(
        interface=interface,
        parameters=parameters,
        cadet_and_text=cadet_and_text
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
        print("Getting cadet from form")
        cadet_and_text = verify_form_with_cadet_details(interface=interface)
    elif cadet is default_cadet:
        verification_text = ''
        cadet_and_text = CadetAndVerificationText(
            cadet=cadet,
            verification_text=verification_text
        )
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
    cadet_and_text: CadetAndVerificationText,
    parameters: ParametersForGetOrSelectCadetForm,

) -> ListOfLines:
    cadet = cadet_and_text.cadet
    verification_text = cadet_and_text.verification_text
    extra_buttons =get_extra_buttons(parameters)

    if len(verification_text) == 0 and not parameters.default_cadet_passed:
        ## nothing to check, so can put add button up
        parameters.final_add_button = True

    main_buttons = get_list_of_main_buttons(parameters=parameters)

    cadet_buttons = get_list_of_cadet_buttons(
        interface=interface, cadet=cadet, parameters=parameters
    )

    return ListOfLines([main_buttons, extra_buttons, _______________]+cadet_buttons)


def get_extra_buttons(parameters: ParametersForGetOrSelectCadetForm):
    extra_buttons = []
    if parameters.cancel_button:
        extra_buttons.append(cancel_menu_button)
    if parameters.skip_button:
        extra_buttons.append(skip_button)
    extra_buttons = Line(extra_buttons)

    return extra_buttons



def get_list_of_main_buttons(    parameters: ParametersForGetOrSelectCadetForm) -> Line:
    if parameters.default_cadet_passed:
        main_buttons = [check_cadet_for_me_button]
    elif parameters.final_add_button:
        main_buttons = [check_cadet_for_me_button, add_cadet_button]
    else:
        main_buttons = [check_confirm_allow_to_add_cadet_button]

    return Line(main_buttons)

def get_list_of_cadet_buttons(
    interface: abstractInterface, cadet: Cadet,     parameters: ParametersForGetOrSelectCadetForm,

) -> ListOfLines:
    list_of_similar_cadets = get_list_of_similar_cadets_from_data(
        object_store=interface.object_store, cadet=cadet,
        name_threshold=parameters.similarity_name_threshold
    )
    no_similar_cadets = len(list_of_similar_cadets)==0
    list_of_all_cadets_in_data = get_list_of_cadets(object_store=interface.object_store)

    if no_similar_cadets:
        list_of_cadets = list_of_all_cadets_in_data
        state_button = " "
        msg = "No similar cadets - choosing from all. "
    elif parameters.see_all_cadets_button:
        list_of_cadets = list_of_all_cadets_in_data
        msg = "Currently choosing from all cadets. "
        state_button = see_similar_cadets_only_button
    else:
        ## similar cadets with option to see more
        list_of_cadets = list_of_similar_cadets
        msg = "Currently choosing from similar cadets only. "
        state_button = see_all_cadets_button

    list_of_cadets= sort_a_list_of_cadets(list_of_cadets, sort_by=parameters.sort_by, similar_cadet=cadet,
                                          )
    sort_order_buttons  = get_sort_order_buttons(parameters=parameters, list_of_cadets=list_of_cadets)
    cadet_choice_buttons = [Button(str(cadet)) for cadet in list_of_cadets]
    cadet_choice_buttons = break_up_buttons(cadet_choice_buttons)

    return ListOfLines([_______________, Line([msg, state_button]+sort_order_buttons),
                        _______________,]+ cadet_choice_buttons).add_Lines()


def get_sort_order_buttons(
     parameters: ParametersForGetOrSelectCadetForm,
    list_of_cadets: list,
):
    if len(list_of_cadets)<5:
        ## no need to sort, probably not that many
        return ['']
    sort_msg = " Current sort: %s" % parameters.sort_by

    current_sort_order = parameters.sort_by
    possible_sort_labels = copy(possible_sorts)
    if current_sort_order is not arg_not_passed:
        possible_sort_labels.remove(current_sort_order)

    buttons = [sort_msg]+[Button(sort_label) for sort_label in possible_sort_labels]

    if current_sort_order in [SORT_BY_SIMILARITY_BOTH]:
        buttons.append(refresh_button)

    return buttons

def is_button_a_sort_button(button_value: str):
    return button_value in possible_sorts

possible_sorts = [SORT_BY_SURNAME,
SORT_BY_FIRSTNAME,
SORT_BY_DOB_ASC,
SORT_BY_DOB_DSC,
SORT_BY_SIMILARITY_BOTH
]



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
    parameters.get_values_from_state(interface)
    last_button_pressed = interface.last_button_pressed()
    print("last button %s" % last_button_pressed)

    if response_requires_new_form(interface):
        return generic_post_response_to_add_or_select_when_returning_new_form(
            interface=interface,
            parameters=parameters
        )

    parameters.clear_values_in_state(interface)
    if skip_button.pressed(last_button_pressed):
        return ResultFromAddOrSelect(skip=True)

    elif cancel_menu_button.pressed(last_button_pressed):
        return ResultFromAddOrSelect(cancel=True)

    elif add_cadet_button.pressed(last_button_pressed):
        try:
            cadet =add_cadet_from_form_to_data(interface)
        except Exception as e:
            interface.log_error("Error %s when adding cadet to data" % str(e))
            return form_as_result(interface=interface, parameters=parameters)


        return ResultFromAddOrSelect(cadet=cadet, cadet_was_added=True)

    else:
        try:
            cadet = get_existing_cadet_selected_from_button(interface)
        except Exception as e:
            interface.log_error("Error %s when selecting exiating cadet" % str(e))
            return  form_as_result(interface=interface, parameters=parameters)

        return ResultFromAddOrSelect(cadet=cadet, cadet_was_added=False)

def response_requires_new_form(interface: abstractInterface):
    last_button_pressed = interface.last_button_pressed()
    if is_button_a_sort_button(last_button_pressed):
        return True

    return check_if_button_in_list_was_pressed(last_button_pressed=last_button_pressed,
                                               list_of_buttons=[
                                                   see_similar_cadets_only_button,
                                                   see_all_cadets_button,
                                                   check_confirm_allow_to_add_cadet_button,
                                                   check_cadet_for_me_button,
                                                   refresh_button
                                               ])


def generic_post_response_to_add_or_select_when_returning_new_form(
    interface: abstractInterface,
    parameters: ParametersForGetOrSelectCadetForm
) -> ResultFromAddOrSelect():

    last_button_pressed = interface.last_button_pressed()
    if is_button_a_sort_button(last_button_pressed):
        print("Sorting by %s" % last_button_pressed)
        parameters.sort_by = last_button_pressed
    elif refresh_button.pressed(last_button_pressed):
        pass

    elif see_similar_cadets_only_button.pressed(
        last_button_pressed
    ):
        parameters.see_all_cadets_button = False
    elif check_confirm_allow_to_add_cadet_button.pressed(last_button_pressed):
        parameters.final_add_button = True

    elif check_cadet_for_me_button.pressed(last_button_pressed):
        parameters.final_add_button = True
        ## verify results already in form, display form again, allow final this time

    elif see_all_cadets_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        parameters.see_all_cadets_button = True
        parameters.sort_by = SORT_BY_SIMILARITY_BOTH ## OBVIOUS DEFAULT
    else:
        raise Exception("Button not recognised! %s" % last_button_pressed)

    parameters.save_values_to_state(interface)

    return form_as_result(interface=interface, parameters=parameters)



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

def form_as_result(interface: abstractInterface, parameters: ParametersForGetOrSelectCadetForm) -> ResultFromAddOrSelect:
    form = get_add_or_select_existing_cadet_form(
        interface=interface,
        parameters=parameters)

    return ResultFromAddOrSelect(
        form=form
        )



CHECK_CADET_FOR_ME_BUTTON_LABEL = "Please check the details again for me before I add"
CHECK_CADET_CONFIRM_BUTTON_LABEL = "I have double checked these details - allow me to add"
FINAL_CADET_ADD_BUTTON_LABEL = "Yes - these details are correct - add this new cadet"
SEE_ALL_CADETS_BUTTON_LABEL = "Choose from all existing cadets"
SEE_SIMILAR_CADETS_ONLY_LABEL = "See similar cadets only"
SKIP_BUTTON_LABEL = (
    "Skip"
)
REFRESH_LIST_BUTTON_LABEL = "Refresh list"


add_cadet_button = Button(FINAL_CADET_ADD_BUTTON_LABEL)
check_cadet_for_me_button = Button(CHECK_CADET_FOR_ME_BUTTON_LABEL)
check_confirm_allow_to_add_cadet_button = Button(CHECK_CADET_CONFIRM_BUTTON_LABEL)
see_similar_cadets_only_button = Button(SEE_SIMILAR_CADETS_ONLY_LABEL)
see_all_cadets_button = Button(SEE_ALL_CADETS_BUTTON_LABEL)
skip_button = Button(SKIP_BUTTON_LABEL)
refresh_button = Button(REFRESH_LIST_BUTTON_LABEL)