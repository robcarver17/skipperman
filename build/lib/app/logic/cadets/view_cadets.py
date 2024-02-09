from typing import Union

from app.logic.cadets.constants import (
    VIEW_INDIVIDUAL_CADET_STAGE,
    ADD_CADET_STAGE,
    ADD_CADET_BUTTON_LABEL,
)
from app.objects.cadets import Cadet
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_interface import abstractInterface
from app.logic.cadets.cadet_state_storage import update_state_for_specific_cadet
from app.backend.cadets import get_sorted_list_of_cadets, SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC


def display_form_view_of_cadets(interface: abstractInterface) -> Form:
    print("display view of cadets")
    return display_form_view_of_cadets_with_sort_order_passed(
        sort_order=SORT_BY_SURNAME
    )

def display_form_view_of_cadets_with_sort_order_passed(sort_order=SORT_BY_SURNAME) -> Form:
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
        return NewForm(ADD_CADET_STAGE)

    elif button_pressed in all_sort_types:
        ## no change to stage required, just sort order
        sort_order = interface.last_button_pressed()
        return display_form_view_of_cadets_with_sort_order_passed(sort_order)

    else:  ## must be a cadet redirect:
        cadet_selected = interface.last_button_pressed()
        update_state_for_specific_cadet(interface=interface, cadet_selected=cadet_selected)
        return NewForm(VIEW_INDIVIDUAL_CADET_STAGE)


def display_list_of_cadets_with_buttons(sort_order=SORT_BY_SURNAME) -> ListOfLines:
    list_of_cadets = get_sorted_list_of_cadets(sort_by=sort_order)

    list_with_buttons = [
        row_of_form_for_cadets_with_buttons(cadet) for cadet in list_of_cadets
    ]

    return ListOfLines(list_with_buttons)


def row_of_form_for_cadets_with_buttons(cadet: Cadet) -> Line:
    return Line([Button(str(cadet))])


all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC]


add_button = Button(ADD_CADET_BUTTON_LABEL)

sort_buttons = Line([Button(sort_by) for sort_by in all_sort_types])


