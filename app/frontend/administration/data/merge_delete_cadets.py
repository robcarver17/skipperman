from typing import Union

from app.frontend.administration.data.deleting_cadets_process import set_cadet_to_delete_in_state, \
    get_cadet_to_delete_from_state
from app.frontend.administration.data.deleting_cadets_process import display_deleting_cadet_process
from app.frontend.administration.data.merging_cadets_process import set_cadet_to_merge_with_in_state
from app.frontend.cadets.ENTRY_view_cadets import get_table_of_cadets_with_buttons
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.buttons import is_button_cadet_selection, cadet_from_button_pressed

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, textInput,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
    HelpButton,
back_menu_button,
SAVE_KEYBOARD_SHORTCUT
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface, form_with_message_and_finished_button
from app.objects.utilities.cadet_matching_and_sorting import SORT_BY_SIMILARITY_BOTH


def display_form_merge_delete_cadets(interface: abstractInterface):
    navbar = ButtonBar([main_menu_button, back_menu_button, help_button]) ## any form without a cancel should have a main menu
    ## a form that accepts input would have a save_button and cancel_button
    table_of_cadets_with_buttons = get_table_of_cadets_with_buttons(
        interface=interface
    )

    contents_of_form = ListOfLines(
        [
            navbar,
            _______________,
            "Select cadet to merge or delete",
            table_of_cadets_with_buttons,
            _______________,
        ]
    )

    return Form(contents_of_form)


help_button = HelpButton("merge_delete_cadets_help")


def post_form_merge_delete_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    ## note we don't need to handle help and menu buttons

    if back_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(display_form_merge_delete_cadets)
    elif is_button_cadet_selection(button_pressed):
        return form_for_view_individual_cadet(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


save_button = Button('Save', nav_button=True, shortcut=SAVE_KEYBOARD_SHORTCUT)

def form_for_view_individual_cadet(interface: abstractInterface) -> NewForm:
    cadet = cadet_from_button_pressed(value_of_button_pressed=interface.last_button_pressed(),
                                      object_store=interface.object_store)
    set_cadet_to_delete_in_state(interface=interface, cadet=cadet)

    return interface.get_new_form_given_function(display_form_merge_delete_individual_cadet)

def display_form_merge_delete_individual_cadet(interface: abstractInterface):
    cadet = get_cadet_to_delete_from_state(interface)
    table_of_cadets_with_buttons = get_table_of_cadets_with_buttons(
        interface=interface,
        exclude_cadet=cadet,
        sort_order=SORT_BY_SIMILARITY_BOTH,
        similar_cadet=cadet
    )
    navbar = ButtonBar([main_menu_button, back_menu_button, help_button]) ## any form without a cancel should have a main menu

    contents_of_form = ListOfLines(
        [
            navbar,
            "Deleting or merging %s" % str(cadet),
            _______________,
            delete_button,
            _______________,
            "Select sailor to merge with (the sailor you select will continue to exist):",
            table_of_cadets_with_buttons,
            _______________,
        ]
    )

    return contents_of_form

delete_button = Button("Delete the sailor completely")

def post_form_merge_delete_individual_cadet(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    ## note we don't need to handle help and menu buttons

    if back_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(display_form_merge_delete_individual_cadet)
    elif is_button_cadet_selection(button_pressed):
        return launch_merge_cadet_process(interface)
    elif delete_button.pressed(button_pressed):
        return launch_delete_cadet_process(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)

def launch_merge_cadet_process(interface: abstractInterface)-> Union[Form, NewForm]:
    cadet_to_merge_with = cadet_from_button_pressed(value_of_button_pressed=interface.last_button_pressed(),
                                      object_store=interface.object_store)
    set_cadet_to_merge_with_in_state(interface=interface, cadet=cadet_to_merge_with)
    return form_with_message_and_finished_button(
        interface=interface,
        message="Not implemented"
    )



def launch_delete_cadet_process(interface: abstractInterface):

    ## get warnings
    ## confirm ok
    ## if not okay, clear cache without saving
    ## if ok flush cache and return
    return interface.get_new_form_given_function(display_deleting_cadet_process)

