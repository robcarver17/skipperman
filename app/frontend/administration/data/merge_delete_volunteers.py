from typing import Union

from app.frontend.administration.data.deleting_volunteers_process import (
    set_volunteer_to_delete_in_state,
    get_volunteer_to_delete_from_state,
    display_deleting_volunteer_process,
)
from app.frontend.administration.data.merging_volunteers_process import (
    set_volunteer_to_merge_with_in_state,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.buttons import (
    is_button_volunteer_selection,
    volunteer_from_button_pressed,
)

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
)
from app.frontend.volunteers.ENTRY_view_volunteers import (
    get_list_of_volunteers_with_buttons,
)

from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)


def display_form_merge_delete_volunteers(interface: abstractInterface):
    navbar = ButtonBar(
        [main_menu_button, back_menu_button, help_button]
    )  ## any form without a cancel should have a main menu
    ## a form that accepts input would have a save_button and cancel_button
    table_of_volunteers_with_buttons = get_list_of_volunteers_with_buttons(
        interface=interface
    )

    contents_of_form = ListOfLines(
        [
            navbar,
            _______________,
            "Select volunteer to merge or delete",
            table_of_volunteers_with_buttons,
            _______________,
        ]
    )

    return Form(contents_of_form)


help_button = HelpButton("merge_delete_volunteers_help")


def post_form_merge_delete_volunteers(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    ## note we don't need to handle help and menu buttons

    if back_menu_button.pressed(button_pressed):
        interface.flush_and_clear()
        return interface.get_new_display_form_for_parent_of_function(
            display_form_merge_delete_volunteers
        )

    elif is_button_volunteer_selection(
        button_pressed
    ):  ## must be a volunteer redirect:
        return view_specific_volunteer_form(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def view_specific_volunteer_form(interface: abstractInterface):
    volunteer = volunteer_from_button_pressed(
        object_store=interface.object_store,
        value_of_button_pressed=interface.last_button_pressed(),
    )
    set_volunteer_to_delete_in_state(interface=interface, volunteer=volunteer)
    return interface.get_new_form_given_function(
        display_form_merge_delete_individual_volunteer
    )


from app.backend.volunteers.list_of_volunteers import SORT_BY_NAME_SIMILARITY


def display_form_merge_delete_individual_volunteer(interface: abstractInterface):
    volunteer = get_volunteer_to_delete_from_state(interface)
    table_of_volunteers_with_buttons = get_list_of_volunteers_with_buttons(
        interface=interface,
        sort_order=SORT_BY_NAME_SIMILARITY,
        similar_volunteer=volunteer,
        exclude_volunteer=volunteer,
    )
    navbar = ButtonBar(
        [main_menu_button, back_menu_button, help_button]
    )  ## any form without a cancel should have a main menu

    contents_of_form = ListOfLines(
        [
            navbar,
            "Deleting or merging %s" % str(volunteer),
            _______________,
            delete_button,
            _______________,
            _______________,
            "Select volunteer to merge with (the volunteer you select will continue to exist):",
            table_of_volunteers_with_buttons,
            _______________,
        ]
    )

    return contents_of_form


delete_button = Button("Delete the volunteer completely")


def post_form_merge_delete_individual_volunteer(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    ## note we don't need to handle help and menu buttons

    if back_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(
            display_form_merge_delete_individual_volunteer
        )
    elif is_button_volunteer_selection(button_pressed):
        return launch_merge_volunteer_process(interface)
    elif delete_button.pressed(button_pressed):
        return launch_delete_volunteer_process(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def launch_merge_volunteer_process(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    volunteer_to_merge_with = volunteer_from_button_pressed(
        value_of_button_pressed=interface.last_button_pressed(),
        object_store=interface.object_store,
    )
    set_volunteer_to_merge_with_in_state(
        interface=interface, volunteer=volunteer_to_merge_with
    )
    return form_with_message_and_finished_button(
        interface=interface, message="Not implemented"
    )


def launch_delete_volunteer_process(interface: abstractInterface):
    return interface.get_new_form_given_function(display_deleting_volunteer_process)
