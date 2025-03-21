from typing import Union, List

from app.data_access.configuration.fixed import ADD_KEYBOARD_SHORTCUT
from app.frontend.cadets.add_cadet import display_form_add_cadet
from app.frontend.cadets.cadet_committee import display_form_cadet_committee
from app.frontend.cadets.import_members import display_form_import_members
from app.frontend.cadets.view_individual_cadets import (
    display_form_view_individual_cadet,
)
from app.objects.cadets import (
    Cadet,
    SORT_BY_SURNAME,
    SORT_BY_FIRSTNAME,
    SORT_BY_DOB_ASC,
    SORT_BY_DOB_DSC,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import Table, RowInTable

from app.frontend.shared.cadet_state import update_state_for_specific_cadet
from app.backend.cadets.list_of_cadets import (
    get_cadet_from_list_of_cadets_given_str_of_cadet,
    get_sorted_list_of_cadets,
)


def display_form_view_of_cadets(interface: abstractInterface) -> Form:
    return display_form_view_of_cadets_with_sort_order_passed(
        interface=interface, sort_order=SORT_BY_SURNAME
    )


def display_form_view_of_cadets_with_sort_order_passed(
    interface: abstractInterface, sort_order=SORT_BY_SURNAME
) -> Form:
    table_of_cadets_with_buttons = get_table_of_cadets_with_buttons(
        interface=interface, sort_order=sort_order
    )
    form_contents = ListOfLines(
        [
            nav_buttons,
            _______________,
            sort_buttons,
            _______________,
            "Click on any sailor to view / edit",
            _______________,
            table_of_cadets_with_buttons,
        ]
    )

    form = Form(form_contents)

    return form


def post_form_view_of_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if add_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_add_cadet)

    if import_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_import_members)
    elif committee_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_cadet_committee)

    elif sort_button_pressed(button_pressed):
        ## no change to stage required, just sort order
        new_sort_order = interface.last_button_pressed()
        return display_form_view_of_cadets_with_sort_order_passed(
            interface=interface, sort_order=new_sort_order
        )

    else:  ## must be a cadet redirect:
        return form_for_view_individual_cadet(interface)


def form_for_view_individual_cadet(interface: abstractInterface) -> NewForm:
    cadet_selected_as_str = interface.last_button_pressed()
    cadet = get_cadet_from_list_of_cadets_given_str_of_cadet(
        object_store=interface.object_store, cadet_selected=cadet_selected_as_str
    )
    update_state_for_specific_cadet(interface=interface, cadet=cadet)

    return interface.get_new_form_given_function(display_form_view_individual_cadet)


def get_table_of_cadets_with_buttons(
    interface: abstractInterface, sort_order=SORT_BY_SURNAME
) -> Table:
    list_of_cadets = get_sorted_list_of_cadets(
        object_store=interface.object_store, sort_by=sort_order
    )
    list_of_rows = [
        row_of_form_for_cadets_with_buttons(cadet) for cadet in list_of_cadets
    ]

    return Table(list_of_rows)


def row_of_form_for_cadets_with_buttons(cadet: Cadet) -> RowInTable:
    return RowInTable([Button(str(cadet))])


def sort_button_pressed(button_pressed: str):
    return any([button.pressed(button_pressed) for button in sort_buttons])


all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC]

ADD_CADET_BUTTON_LABEL = "Add sailor"
IMPORT_CADETS_FROM_MEMBERSHIP_FILE = "Import members from a spreadsheet file"
CADET_COMMITTEE_BUTTON_LABEL = "Edit cadet committee"

add_button = Button(
    ADD_CADET_BUTTON_LABEL, nav_button=True, shortcut=ADD_KEYBOARD_SHORTCUT
)
import_button = Button(IMPORT_CADETS_FROM_MEMBERSHIP_FILE, nav_button=True)
committee_button = Button(CADET_COMMITTEE_BUTTON_LABEL, nav_button=True)
help_button = HelpButton("view_all_cadets_help")

sort_buttons_list = [Button(sort_by, nav_button=True) for sort_by in all_sort_types]


nav_buttons = ButtonBar(
    [main_menu_button, add_button, import_button, committee_button, help_button]
)
sort_buttons = ButtonBar(sort_buttons_list)
