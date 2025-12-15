from typing import Union

from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
    HelpButton,
    back_menu_button,
    cancel_menu_button,
    SAVE_KEYBOARD_SHORTCUT,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

"""
Both display_form... and post_form... should be added to the relevant ..._function_mapping file

(display_form_view_of_events, post_form_view_of_events): { ## this is the parent page they come from
    (display_form_..., post_form_...): 0, ## 0 is just a placeholder for forms without children; could be anything

"""


def display_form_AN_EXAMPLE(interface: abstractInterface):
    navbar = ButtonBar(
        [
            main_menu_button,
            back_menu_button,
            cancel_menu_button,
            save_button,
            help_button,
        ]
    )  ## any form without a cancel should have a main menu
    ## a form that accepts input would have a save_button and cancel_button

    contents_of_form = ListOfLines(
        [
            navbar,
            _______________,
            "Example form",
            textInput(
                input_name=input_name,
                value="default value",
                input_label="enter something",
            ),
            _______________,
        ]
    )

    return Form(contents_of_form)


input_name = "TEXT_INPUT_NOT_DISPLAYED_USED_TO_IDENTIFY"
help_button = HelpButton("name_of_help_file_in_doc_directory_without_md_extension")


def post_form_AN_EXAMPLE(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    ## note we don't need to handle help and menu buttons

    if back_menu_button.pressed(button_pressed):
        interface.DEPRECATE_flush_and_clear()
        return interface.get_new_display_form_for_parent_of_function(
            display_form_AN_EXAMPLE
        )

    elif cancel_menu_button.pressed(button_pressed):
        interface.log_error("You pressed cancel")
        interface.DEPRECATE_flush_and_clear()
    elif save_button.pressed(button_pressed):
        interface.log_error(
            "you entered %s"
            % interface.value_from_form(
                input_name, "no_value found in form which means error"
            )
        )
        return interface.get_new_form_given_function(
            display_form_AN_EXAMPLE
        )  ## could equally be any function 'below'
    else:
        return button_error_and_back_to_initial_state_form(interface)


save_button = Button("Save", nav_button=True, shortcut=SAVE_KEYBOARD_SHORTCUT)
