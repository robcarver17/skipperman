from typing import Union

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.utilities.notes.parse_notes import save_all_notes, update_sort_status
from app.frontend.utilities.notes.render_notes import (
    help_button,
    get_existing_incomplete_notes,
    get_existing_complete_notes,
    save_quick_note_button,
    get_quick_note_form,
    save_button,
    save_table_entries,
    sort_buttons,
    get_sorted_list_of_volunteer_notes,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    ButtonBar,
    cancel_menu_button,
    check_if_button_in_list_was_pressed,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_text import Heading


def display_form_notes(interface: abstractInterface):
    navbar = ButtonBar(
        [
            main_menu_button,
            cancel_menu_button,
            save_button,
            help_button,
        ]
    )  ## any form without a cancel should have a main menu
    ## a form that accepts input would have a save_button and cancel_button

    list_of_notes = get_sorted_list_of_volunteer_notes(interface)

    quick_note_form = get_quick_note_form()
    incomplete_table = get_existing_incomplete_notes(
        interface, list_of_notes=list_of_notes
    )
    complete_table = get_existing_complete_notes(interface, list_of_notes=list_of_notes)

    contents_of_form = ListOfLines(
        [
            navbar,
            _______________,
            _______________,
            Heading("New note", size=3, centred=True),
            _______________,
            quick_note_form,
            save_quick_note_button,
            _______________,
            _______________,
            Heading("Active notes - click buttons to sort", size=3, centred=True),
            _______________,
            incomplete_table,
            save_table_entries,
            _______________,
            _______________,
            Heading("Completed notes", size=3, centred=True),
            _______________,
            complete_table,
            save_table_entries,
        ]
    )

    return Form(contents_of_form)


def post_form_notes(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    ## note we don't need to handle help and menu buttons

    if cancel_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(display_form_notes)
    elif was_sort_button(interface):
        update_sort_status(interface)
        save_all_notes(interface)
        return interface.get_new_form_given_function(
            display_form_notes
        )  ## could equally be any function 'below'

    elif was_save_button(interface):
        save_all_notes(interface)
        return interface.get_new_form_given_function(
            display_form_notes
        )  ## could equally be any function 'below'
    else:
        return button_error_and_back_to_initial_state_form(interface)


def was_sort_button(inteface: abstractInterface):
    return check_if_button_in_list_was_pressed(
        inteface.last_button_pressed(), sort_buttons
    )


def was_save_button(interface: abstractInterface):
    return check_if_button_in_list_was_pressed(
        interface.last_button_pressed(),
        [save_button, save_quick_note_button, save_table_entries],
    )
