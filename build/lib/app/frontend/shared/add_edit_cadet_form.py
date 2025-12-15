from copy import copy
from dataclasses import dataclass
from typing import Union

from app.backend.cadets.add_edit_cadet import (
    verify_cadet_and_return_warnings,
    add_new_verified_cadet,
)
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    cancel_menu_button,
    Button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    textInput,
    dateInput,
    dropDownInput,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
    _______________,
)
from app.objects.abstract_objects.abstract_text import bold

from app.objects.cadets import (
    Cadet,
    default_cadet,
    DOB_SURE,
    DOB_UNKNOWN,
    DOB_IRRELEVANT,
    UNCONFIRMED_DATE_OF_BIRTH,
    IRRELEVANT_DATE_OF_BIRTH,
)
from app.objects.membership_status import (
    MembershipStatus,
    describe_status,
    all_status_description_as_dict_for_user_input,
    none_member,
)
from app.objects.utilities.exceptions import (
    arg_not_passed,
    MISSING_FROM_FORM,
    MissingData,
)


@dataclass
class CadetAndVerificationText:
    cadet: Cadet
    verification_text: str = ""

    @property
    def is_default(self) -> bool:
        return self.cadet is default_cadet


default_cadet_and_text = CadetAndVerificationText(
    cadet=default_cadet, verification_text=""
)


def get_add_cadet_form(
    interface: abstractInterface,
    header_text: ListOfLines = arg_not_passed,
    first_time_displayed: bool = True,
    help_string: str = arg_not_passed,
) -> Form:
    if first_time_displayed:
        footer_buttons = get_footer_buttons_for_add_cadet_form(form_is_empty=True)
        return get_add_cadet_form_with_information_passed(
            footer_buttons=footer_buttons,
            header_text=header_text,
            help_string=help_string,
        )
    else:
        cadet_and_text = verify_form_with_cadet_details(interface)
        form_is_empty = cadet_and_text.is_default
        footer_buttons = get_footer_buttons_for_add_cadet_form(
            form_is_empty=form_is_empty
        )

        return get_add_cadet_form_with_information_passed(
            header_text=header_text,
            cadet_and_text=cadet_and_text,
            footer_buttons=footer_buttons,
            help_string=help_string,
        )


default_header = ListOfLines(["Add a new sailor"])


def get_add_cadet_form_with_information_passed(
    footer_buttons: Union[Line, ListOfLines, ButtonBar],
    help_string: str = arg_not_passed,
    header_text: ListOfLines = arg_not_passed,
    cadet_and_text: CadetAndVerificationText = default_cadet_and_text,
) -> Form:
    if header_text is arg_not_passed:
        header_text = default_header
    if help_string is arg_not_passed:
        nav_bar = ""
    else:
        nav_bar = ButtonBar([HelpButton(help_string)])

    form_fields = form_fields_for_add_cadet(cadet_and_text.cadet)

    list_of_lines_inside_form = ListOfLines(
        [nav_bar]
        + header_text
        + [
            _______________,
            _______________,
            form_fields,
            _______________,
            bold(cadet_and_text.verification_text),
            _______________,
            footer_buttons,
        ]
    )

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
    if cadet.membership_status == none_member:
        default_dob_status = DOB_IRRELEVANT
    elif cadet.date_of_birth == UNCONFIRMED_DATE_OF_BIRTH:
        default_dob_status = DOB_UNKNOWN
    elif cadet.date_of_birth == IRRELEVANT_DATE_OF_BIRTH:
        default_dob_status = DOB_IRRELEVANT
    else:
        default_dob_status = DOB_SURE

    dob_unsure = dropDownInput(
        input_label="status: ",
        input_name=DOB_UNSURE_FIELD,
        dict_of_options={
            DOB_SURE: DOB_SURE,
            DOB_IRRELEVANT: DOB_IRRELEVANT,
            DOB_UNKNOWN: DOB_UNKNOWN,
        },
        default_label=default_dob_status,
    )
    membership_status = dropDownInput(
        input_label="",
        input_name=MEMBERSHIP_STATUS,
        dict_of_options=membership_status_options(),
        default_label=describe_status(cadet.membership_status),
    )

    form_fields = ListOfLines(
        [
            Line(first_name),
            Line(surname),
            Line([dob, dob_unsure]),
            Line(membership_status),
        ]
    )

    return form_fields


def membership_status_options():
    return dict(
        [
            (status_description, status.name)
            for status_description, status in all_status_description_as_dict_for_user_input.items()
        ]
    )


def verify_form_with_cadet_details(
    interface: abstractInterface, default=default_cadet
) -> CadetAndVerificationText:
    try:
        cadet = get_cadet_from_form(interface)
        if cadet is MISSING_FROM_FORM:
            raise "Can't get cadet from form"
        verify_text = verify_cadet_and_return_warnings(
            cadet=cadet, object_store=interface.object_store
        )
    except Exception as e:
        cadet = copy(default)
        verify_text = (
            "Doesn't appear to be a valid sailor (wrong date time in old browser?) error code %s"
            % str(e)
        )

    return CadetAndVerificationText(cadet=cadet, verification_text=verify_text)


def get_footer_buttons_for_add_cadet_form(form_is_empty: bool) -> ButtonBar:
    if form_is_empty:
        return ButtonBar([cancel_menu_button, check_details_button])
    else:
        return ButtonBar(
            [cancel_menu_button, check_details_button, final_submit_button]
        )


FIRST_NAME = "first_name"
SURNAME = "surname"
DOB = "date_of_birth"
DOB_UNSURE_FIELD = "dob_unsure"
MEMBERSHIP_STATUS = "membership_status"

CHECK_BUTTON_LABEL = "Check details entered"
FINAL_ADD_BUTTON_LABEL = "Yes - these details are correct - add to data"
final_submit_button = Button(FINAL_ADD_BUTTON_LABEL, nav_button=True)
check_details_button = Button(CHECK_BUTTON_LABEL, nav_button=True)


def get_cadet_from_form(interface: abstractInterface, as_non_member: bool = False) -> Cadet:
    first_name = interface.value_from_form(FIRST_NAME, default=MISSING_FROM_FORM)
    surname = interface.value_from_form(SURNAME, default=MISSING_FROM_FORM)
    date_of_birth = interface.value_from_form(
        DOB, default=MISSING_FROM_FORM, value_is_date=True
    )
    dob_status = interface.value_from_form(DOB_UNSURE_FIELD, default=MISSING_FROM_FORM)
    membership_status = interface.value_from_form(MEMBERSHIP_STATUS, default=MISSING_FROM_FORM)

    if MISSING_FROM_FORM in [first_name, surname, dob_status, date_of_birth, membership_status]:
        return MISSING_FROM_FORM

    return Cadet.new(
        first_name=first_name.strip().title(),
        surname=surname.strip().title(),
        date_of_birth=date_of_birth,
        membership_status=MembershipStatus[membership_status],
        dob_status=dob_status,
        as_non_member =as_non_member
    )


def add_cadet_from_form_to_data(interface: abstractInterface, as_non_member: bool = False) -> Cadet:
    cadet = get_cadet_from_form(interface, as_non_member=as_non_member)
    if cadet is MISSING_FROM_FORM:
        raise MissingData("Can't get cadet from form")
    
    cadet = add_new_verified_cadet(object_store=interface.object_store, cadet=cadet)
    interface.DEPRECATE_flush_and_clear()

    return cadet
