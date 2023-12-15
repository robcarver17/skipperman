from typing import Union

from app.logic.cadets.constants import (
    VIEW_INDIVIDUAL_CADET_FORM,
    ADD_CADET_FORM,
    ADD_CADET_BUTTON_LABEL,
)
from app.objects.cadets import ListOfCadets, Cadet
from app.data_access.data import data
from app.logic.forms_and_interfaces.abstract_form import (
    Form,
    NewForm,
    Line,
    Button,
    ListOfLines,
    main_menu_button, _______________,
)
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface

SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
SORT_BY_DOB_ASC = "Sort by date of birth, ascending"
SORT_BY_DOB_DSC = "Sort by date of birth, descending"


def display_form_view_of_cadets(sort_order=SORT_BY_SURNAME) -> Form:
    list_of_cadets_with_buttons = display_list_of_cadets_with_buttons(
        sort_order=sort_order
    )

    form_contents = ListOfLines(
        [
            main_menu_button,
            _______________,
            sort_buttons,
            _______________,
            Line("Click on any cadet to view/edit/delete"),
            _______________,
            add_button,
            _______________,
            list_of_cadets_with_buttons,
        ]
    )

    form = Form(form_contents)

    return form


def post_form_view_of_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == ADD_CADET_BUTTON_LABEL:
        return NewForm(ADD_CADET_FORM)
    elif button_pressed in all_sort_types:
        ## no change to stage required, just sort order
        sort_order = interface.last_button_pressed()
        return display_form_view_of_cadets(sort_order=sort_order)
    else:  ## must be a cadet redirect:
        return NewForm(VIEW_INDIVIDUAL_CADET_FORM)


def display_list_of_cadets_with_buttons(sort_order=SORT_BY_SURNAME) -> ListOfLines:
    list_of_cadets = get_list_of_cadets(sort_by=sort_order)

    list_with_buttons = [
        row_of_form_for_cadets_with_buttons(cadet) for cadet in list_of_cadets
    ]

    return ListOfLines(list_with_buttons)


def row_of_form_for_cadets_with_buttons(cadet: Cadet) -> Line:
    return Line([Button(str(cadet))])


all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC]


add_button = Button(ADD_CADET_BUTTON_LABEL)

sort_buttons = Line([Button(sort_by) for sort_by in all_sort_types])

from app.objects.constants import arg_not_passed
def get_list_of_cadets(sort_by: str = arg_not_passed) -> ListOfCadets:
    master_list = data.data_list_of_cadets.read()
    if sort_by is arg_not_passed:
        return master_list
    if sort_by == SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    elif sort_by == SORT_BY_DOB_ASC:
        return master_list.sort_by_dob_asc()
    elif sort_by == SORT_BY_DOB_DSC:
        return master_list.sort_by_dob_desc()
    else:
        return master_list


def cadet_name_from_id(cadet_id: str) -> str:
    cadet = cadet_from_id(cadet_id)

    return str(cadet)


def cadet_from_id(cadet_id: str) -> Cadet:
    list_of_cadets = get_list_of_cadets()

    cadet = list_of_cadets.object_with_id(cadet_id)

    return cadet


def cadet_from_id_with_passed_list(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Cadet:
    cadet = list_of_cadets.object_with_id(cadet_id)

    return cadet
