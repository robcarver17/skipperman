from copy import copy
from dataclasses import dataclass
from typing import Union


from app.backend.volunteers.add_edit_volunteer import verify_volunteer_and_warn
from app.backend.volunteers.connected_cadets import get_list_of_similar_volunteers
from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers, sort_list_of_volunteers, \
    get_volunteer_from_list_of_given_str_of_volunteer
from app.frontend.shared.add_edit_or_choose_volunteer_form import VolunteerAndVerificationText, get_volunteer_from_form, \
    get_add_volunteer_form_with_information_passed, add_volunteer_from_form_to_data
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import Button, cancel_menu_button, \
    check_if_button_in_list_was_pressed
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface


from app.objects.cadets import Cadet
from app.backend.volunteers.list_of_volunteers import SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_NAME_SIMILARITY
from app.objects.exceptions import arg_not_passed
from app.objects.volunteers import Volunteer, default_volunteer


@dataclass
class ParametersForGetOrSelectVolunteerForm:
    header_text: ListOfLines
    help_string: str = arg_not_passed
    cancel_button: bool = False
    skip_button: bool = False
    final_add_button: bool = False
    volunteer_is_default: bool = False
    see_all_volunteers: bool = False
    sort_by: str = SORT_BY_NAME_SIMILARITY

    def save_values_to_state(self, interface: abstractInterface):
        print(str(self))
        interface.set_persistent_value(SORT_BY_STATE, self.sort_by)
        interface.set_persistent_value(SEE_ALL_VOLUNTEERS, self.see_all_volunteers)
        interface.set_persistent_value(FINAL_ADD, self.final_add_button)

    def get_values_from_state(self, interface: abstractInterface):
        self.sort_by = interface.get_persistent_value(SORT_BY_STATE, SORT_BY_FIRSTNAME)
        self.final_add_button = interface.get_persistent_value(FINAL_ADD, False)
        self.see_all_volunteers = interface.get_persistent_value(SEE_ALL_VOLUNTEERS, False)

    def clear_values_in_state(self, interface: abstractInterface):
        for key in [SORT_BY_STATE, SEE_ALL_VOLUNTEERS, FINAL_ADD]:
            interface.clear_persistent_value(key)

    def update_on_passed_volunteer(self, volunteer: Volunteer):
        if volunteer is default_volunteer:
            self.volunteer_is_default = True
            self.see_all_volunteers = True
        else:
            self.volunteer_is_default = False

SORT_BY_STATE = '*selectvoolunteerform_sortyby'
SEE_ALL_VOLUNTEERS = '*selectvolunteersform_seelall'
FINAL_ADD = "*selectvolunteers_finaladd"

def get_add_or_select_existing_volunteer_form(
    interface: abstractInterface,
    parameters: ParametersForGetOrSelectVolunteerForm,
    volunteer: Volunteer = arg_not_passed,  ## Is passed only on first iteration
     cadet: Cadet = arg_not_passed ## only when idenitfying at events
) -> Form:
    parameters.get_values_from_state(interface)
    parameters.update_on_passed_volunteer(volunteer)

    volunteer_and_text = get_volunteer_and_verification_text(
        interface=interface, volunteer=volunteer, cadet=cadet
    )


    ## First time, don't include final or all cadets
    footer_buttons = get_footer_buttons_add_or_select_existing_volunteer_form(
        interface=interface,
        volunteer_and_text=volunteer_and_text,
        cadet=cadet,
        parameters=parameters
    )
    # Custom header text

    return get_add_volunteer_form_with_information_passed(
        volunteer_and_text=volunteer_and_text,
        footer_buttons=footer_buttons,
        header_text=parameters.header_text,
        help_string = parameters.help_string
    )


def get_volunteer_and_verification_text(interface: abstractInterface,
                                        volunteer: Volunteer = arg_not_passed,
                                        cadet: Cadet = arg_not_passed) -> VolunteerAndVerificationText:
    if volunteer is default_volunteer:
        return VolunteerAndVerificationText(volunteer=volunteer, verification_text='')

    if volunteer is arg_not_passed:
        ## Form has been filled in, this isn't our first rodeo, get volunteer from form
        volunteer = get_volunteer_from_form(interface)

    verification_text = verify_volunteer_and_warn(
        object_store=interface.object_store, volunteer=volunteer,
        cadet=cadet
    )
    volunteer_and_text = VolunteerAndVerificationText(
        volunteer=volunteer, verification_text=verification_text
    )

    return volunteer_and_text

def get_footer_buttons_add_or_select_existing_volunteer_form(
    interface: abstractInterface,
parameters: ParametersForGetOrSelectVolunteerForm,
    volunteer_and_text: VolunteerAndVerificationText,
        cadet: Cadet = arg_not_passed,

) -> ListOfLines:
    verification_text = volunteer_and_text.verification_text
    volunteer = volunteer_and_text.volunteer

    if len(verification_text) == 0 and not parameters.volunteer_is_default:
        ## nothing to check, so can put add button up
        parameters.final_add_button = True

    extra_buttons =get_extra_buttons(parameters)

    main_buttons = get_list_of_main_buttons(parameters=parameters)

    volunteer_buttons = get_list_of_volunteer_buttons(
        interface=interface, volunteer=volunteer, cadet=cadet, parameters=parameters
    )

    return ListOfLines([main_buttons, extra_buttons, _______________]+volunteer_buttons)



def get_extra_buttons(parameters:ParametersForGetOrSelectVolunteerForm):
    extra_buttons = []
    if parameters.cancel_button:
        extra_buttons.append(cancel_menu_button)
    if parameters.skip_button:
        extra_buttons.append(skip_volunteer_button)
    extra_buttons = Line(extra_buttons)

    return extra_buttons



def get_list_of_main_buttons(    parameters: ParametersForGetOrSelectVolunteerForm) -> Line:
    if parameters.volunteer_is_default:
        main_buttons = [check_for_me_volunteer_button]
    elif parameters.final_add_button:
        main_buttons = [check_for_me_volunteer_button, add_volunteer_button]
    else:
        main_buttons = [check_confirm_volunteer_button]

    return Line(main_buttons)



def get_list_of_volunteer_buttons(
    interface: abstractInterface, volunteer: Volunteer,    parameters: ParametersForGetOrSelectVolunteerForm, cadet: Cadet = arg_not_passed

) -> ListOfLines:
    list_of_similar_volunteers = get_list_of_similar_volunteers(
        object_store=interface.object_store, volunteer=volunteer, cadet=cadet
    )
    no_similar_volunteers = len(list_of_similar_volunteers)==0
    if no_similar_volunteers or parameters.see_all_volunteers:
        list_of_volunteers = get_list_of_volunteers(
            object_store=interface.object_store
        )
        if no_similar_volunteers:
            msg = "No similar volunteers: choosing from all volunteers"
        else:
            msg = "Currently choosing from all volunteers"
        state_button = see_similar_volunteers_button

    else:
        list_of_volunteers = list_of_similar_volunteers
        msg = "Currently choosing from similar volunteers only:"
        state_button = see_all_volunteers_button


    list_of_volunteers=sort_list_of_volunteers(list_of_volunteers, sort_by=parameters.sort_by, similar_volunteer = volunteer)
    sort_order_buttons  = get_sort_order_buttons(parameters)
    volunteer_choice_buttons = Line([Button(str(volunteer)) for volunteer in list_of_volunteers])

    return ListOfLines([_______________, Line([msg, state_button]+sort_order_buttons),
                        _______________, volunteer_choice_buttons]).add_Lines()


def get_sort_order_buttons(
     parameters: ParametersForGetOrSelectVolunteerForm,

):
    if not parameters.see_all_volunteers:
        ## no need to sort, probably not that many
        return ['']
    sort_msg = parameters.sort_by

    current_sort_order = parameters.sort_by
    possible_sort_labels = copy(possible_sorts)
    if current_sort_order is not arg_not_passed:
        possible_sort_labels.remove(current_sort_order)

    list_of_buttons =  [sort_msg]+[Button(sort_label) for sort_label in possible_sort_labels]

    if current_sort_order == SORT_BY_NAME_SIMILARITY:
        list_of_buttons.append(refresh_list_button)

    return list_of_buttons

def is_button_a_sort_button(button_value: str):
    return button_value in possible_sorts

possible_sorts = [
    SORT_BY_FIRSTNAME,SORT_BY_SURNAME, SORT_BY_NAME_SIMILARITY
]



@dataclass
class ResultFromAddOrSelectVolunteer:
    form: Union[Form, NewForm] = arg_not_passed
    volunteer: Volunteer = arg_not_passed,
    skip: bool = False
    cancel: bool = False
    volunteer_was_added: bool = False

    @property
    def is_form(self):
        return not self.form is arg_not_passed

    @property
    def is_volunteer(self):
        return not self.volunteer is arg_not_passed


def generic_post_response_to_add_or_select_volunteer(
    interface: abstractInterface,
parameters: ParametersForGetOrSelectVolunteerForm
) -> ResultFromAddOrSelectVolunteer:
    parameters.get_values_from_state(interface)
    last_button_pressed = interface.last_button_pressed()

    if response_requires_new_form(interface):
        return generic_post_response_to_add_or_select_volunteer_when_returning_new_form(
            interface=interface,
            parameters=parameters
        )

    parameters.clear_values_in_state(interface)
    if skip_volunteer_button.pressed(last_button_pressed):
        return ResultFromAddOrSelectVolunteer(skip=True)

    elif cancel_menu_button.pressed(last_button_pressed):
        return ResultFromAddOrSelectVolunteer(cancel=True)

    elif add_volunteer_button.pressed(last_button_pressed):
        try:
            volunteer = add_volunteer_from_form_to_data(interface)
        except Exception as e:
            interface.log_error("Error adding volunteer %s" % str(e))
            return form_as_result(interface=interface, parameters=parameters)

        return ResultFromAddOrSelectVolunteer(volunteer=volunteer, volunteer_was_added=True)

    else:
        try:
            volunteer=get_existing_volunteer_selected_from_button(interface=interface)
        except Exception as e:
            interface.log_error("Error selecting volunteer %s" % str(e))
            return form_as_result(interface=interface, parameters=parameters)

        return ResultFromAddOrSelectVolunteer(volunteer=volunteer, volunteer_was_added=False)

def response_requires_new_form(interface: abstractInterface):
    last_button_pressed = interface.last_button_pressed()
    if is_button_a_sort_button(last_button_pressed):
        return True

    return  check_if_button_in_list_was_pressed(
        last_button_pressed=last_button_pressed,
        list_of_buttons=[
            see_similar_volunteers_button,
            see_all_volunteers_button,
            check_confirm_volunteer_button,
            check_for_me_volunteer_button,
            refresh_list_button
        ]
    )



def generic_post_response_to_add_or_select_volunteer_when_returning_new_form(
    interface: abstractInterface,
    parameters:ParametersForGetOrSelectVolunteerForm
) -> ResultFromAddOrSelectVolunteer:

    last_button_pressed = interface.last_button_pressed()
    if is_button_a_sort_button(last_button_pressed):
        print("Sorting by %s" % last_button_pressed)
        parameters.sort_by = last_button_pressed
    elif refresh_list_button.pressed(last_button_pressed):
        pass

    elif see_similar_volunteers_button.pressed(
        last_button_pressed
    ):
        parameters.see_all_volunteers = False

    elif see_all_volunteers_button.pressed(last_button_pressed):
        ## verify results already in form, display form again, allow final this time
        parameters.see_all_volunteers = True

    elif check_if_button_in_list_was_pressed(last_button_pressed=last_button_pressed, list_of_buttons=[check_for_me_volunteer_button, check_confirm_volunteer_button]):
        parameters.final_add_button= True

    else:
        raise Exception("Button not recognised! %s" % last_button_pressed)

    parameters.save_values_to_state(interface)

    return form_as_result(interface=interface, parameters=parameters)



def get_existing_volunteer_selected_from_button(interface: abstractInterface) -> Volunteer:
    volunteer_selected_as_str = interface.last_button_pressed()

    volunteer = get_volunteer_from_list_of_given_str_of_volunteer(
        object_store=interface.object_store,
        volunteer_as_str=volunteer_selected_as_str,
        default=None,
    )
    if volunteer is None:
        raise Exception("Volunteer %s has gone missing!" % volunteer_selected_as_str)


    return volunteer

def form_as_result(interface: abstractInterface, parameters: ParametersForGetOrSelectVolunteerForm):
    form = get_add_or_select_existing_volunteer_form(
        interface=interface,
        parameters=parameters)

    return ResultFromAddOrSelectVolunteer(
        form=form
    )


SEE_SIMILAR_VOLUNTEER_ONLY_LABEL = "See similar volunteers only"
SEE_ALL_VOLUNTEER_BUTTON_LABEL = "Choose from all existing volunteers"
CONFIRM_CHECKED_VOLUNTEER_BUTTON_LABEL = (
    "I have double checked the volunteer details entered - allow me to add"
)
CHECK_FOR_ME_VOLUNTEER_BUTTON_LABEL = "Please check these volunteer details for me"
FINAL_VOLUNTEER_ADD_BUTTON_LABEL = (
    "Yes - these details are correct - add this new volunteer"
)
SKIP_VOLUNTEER_BUTTON_LABEL = "Skip - this isn't a volunteers name"
REFRESH_LIST_BUTTON_LABEL = "Refresh list"

add_volunteer_button = Button(FINAL_VOLUNTEER_ADD_BUTTON_LABEL)

see_all_volunteers_button = Button(SEE_ALL_VOLUNTEER_BUTTON_LABEL)
see_similar_volunteers_button = Button(SEE_SIMILAR_VOLUNTEER_ONLY_LABEL)

check_for_me_volunteer_button = Button(CHECK_FOR_ME_VOLUNTEER_BUTTON_LABEL)
check_confirm_volunteer_button = Button(CONFIRM_CHECKED_VOLUNTEER_BUTTON_LABEL)

skip_volunteer_button = Button(SKIP_VOLUNTEER_BUTTON_LABEL)
refresh_list_button = Button(REFRESH_LIST_BUTTON_LABEL)