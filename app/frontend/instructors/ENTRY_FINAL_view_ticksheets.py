from typing import Union
from app.objects.abstract_objects.abstract_buttons import (
    check_if_button_in_list_was_pressed,
)

from app.backend.security.logged_in_user import (
    get_volunteer_for_logged_in_user_or_superuser,
)
from app.backend.security.user_access import can_see_all_groups_and_award_qualifications

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.instructors.buttons import is_generic_tick_button_pressed
from app.frontend.shared.buttons import (
    is_button_cadet_selection,
    cadet_from_button_pressed,
)
from app.frontend.instructors.parse_ticksheet_table import save_ticksheet_edits
from app.frontend.instructors.parse_macro_buttons_in_ticksheets import (
    action_if_macro_tick_button_pressed,
)
from app.frontend.instructors.print_ticksheet import (
    download_labelled_ticksheet_and_return_file,
)

from app.frontend.instructors.render_ticksheet_table import get_ticksheet_table
from app.frontend.instructors.ticksheet_table_elements import (
    get_buttons_for_ticksheet,
    get_instructions_for_ticksheet,
)
from app.frontend.instructors.ticksheet_table_elements import (
    edit_checkbox_button,
    edit_dropdown_button,
    print_button,
    show_all_cadets_button,
)

from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    main_menu_button,
    HelpButton,
    back_menu_button,
    cancel_menu_button,
    save_menu_button,
)

from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)

from app.frontend.shared.qualification_and_tick_state_storage import (
    get_group_from_state,
    get_qualification_from_state,
    set_edit_state_of_ticksheet,
    EDIT_CHECKBOX_STATE,
    EDIT_DROPDOWN_STATE,
    NO_EDIT_STATE,
    not_editing,
)

from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.cadet_state import (
    clear_cadet_state,
    update_state_for_specific_cadet,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_view_ticksheets_for_event_and_group(
    interface: abstractInterface,
) -> Form:
    ### options: print, edit, add qualifications_and_ticks (super users only)
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    qualification = get_qualification_from_state(interface)

    buttons = get_buttons_for_ticksheet(interface)
    instructions = get_instructions_for_ticksheet(interface=interface)
    navbar = get_nav_bar(interface)
    ticksheet_table = get_ticksheet_table(interface=interface)
    header = Line(
        Heading(
            "Tick sheets 'Tickerman': Event %s, group %s, qualification %s"
            % (str(event), str(group), str(qualification)),
            centred=False,
            size=4,
        )
    )
    lines_inside_form = ListOfLines(
        [
            navbar,
            _______________,
            header,
            _______________,
            instructions,
            _______________,
            buttons,
            _______________,
            ticksheet_table,
            _______________,
        ]
    )

    return Form(lines_inside_form)


def get_nav_bar(interface: abstractInterface):
    if not_editing(interface):
        navbar = [main_menu_button, back_menu_button]
    else:
        navbar = ButtonBar([cancel_menu_button, save_menu_button])

    if can_logged_in_volunteer_award_qualifications(interface):
        help = HelpButton("ticksheet_entry_help_SI")
    else:
        help = HelpButton("ticksheet_entry_help")

    navbar.append(help)

    return ButtonBar(navbar)


def can_logged_in_volunteer_award_qualifications(interface: abstractInterface):
    volunteer = get_volunteer_for_logged_in_user_or_superuser(interface)
    return can_see_all_groups_and_award_qualifications(
        object_store=interface.object_store,
        event=get_event_from_state(interface),
        volunteer=volunteer,
    )


def post_form_view_ticksheets_for_event_and_group(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    if button_pressed_is_back_or_cancel(interface):
        return (
            post_form_view_ticksheets_for_event_and_group_when_back_or_cancel_pressed(
                interface
            )
        )

    elif button_pressed_modifies_state_only(interface):
        return post_form_view_ticksheets_for_event_modifies_state_only(interface)

    elif button_pressed_modifies_ticksheet(interface):
        return post_form_view_ticksheets_for_event_and_saving_ticksheets(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)


def button_pressed_is_back_or_cancel(interface: abstractInterface):
    button_pressed = interface.last_button_pressed()

    return check_if_button_in_list_was_pressed(
        button_pressed, list_of_buttons=[cancel_menu_button, back_menu_button]
    )


def button_pressed_modifies_state_only(interface: abstractInterface):
    button_pressed = interface.last_button_pressed()
    if check_if_button_in_list_was_pressed(
        button_pressed,
        list_of_buttons=[
            print_button,
            show_all_cadets_button,
            edit_dropdown_button,
            edit_checkbox_button,
        ],
    ):
        return True

    if is_button_cadet_selection(button_pressed):
        return True

    return False


def button_pressed_modifies_ticksheet(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if save_menu_button.pressed(last_button):
        return True
    if is_generic_tick_button_pressed(last_button):
        return True
    return False


def post_form_view_ticksheets_for_event_and_group_when_back_or_cancel_pressed(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    button_pressed = interface.last_button_pressed()

    if cancel_menu_button.pressed(button_pressed):
        ## DOES NOT SAVE
        set_edit_state_of_ticksheet(interface=interface, state=NO_EDIT_STATE)
        return display_form_view_ticksheets_for_event_and_group(interface)

    elif back_menu_button.pressed(button_pressed):
        set_edit_state_of_ticksheet(interface=interface, state=NO_EDIT_STATE)
        clear_cadet_state(interface)
        return previous_form(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)


def post_form_view_ticksheets_for_event_modifies_state_only(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    button_pressed = interface.last_button_pressed()

    ## Edit state has to change
    if edit_dropdown_button.pressed(button_pressed):
        set_edit_state_of_ticksheet(interface=interface, state=EDIT_DROPDOWN_STATE)

    elif edit_checkbox_button.pressed(button_pressed):
        set_edit_state_of_ticksheet(interface=interface, state=EDIT_CHECKBOX_STATE)

    ## Select single cadet / all cadets
    elif is_button_cadet_selection(button_pressed):
        cadet = cadet_from_button_pressed(
            object_store=interface.object_store, value_of_button_pressed=button_pressed
        )
        update_state_for_specific_cadet(cadet=cadet, interface=interface)

    elif show_all_cadets_button.pressed(button_pressed):
        clear_cadet_state(interface)

    ## printing
    elif print_button.pressed(button_pressed):
        return download_labelled_ticksheet_and_return_file(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    return display_form_view_ticksheets_for_event_and_group(interface)


def post_form_view_ticksheets_for_event_and_saving_ticksheets(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    button_pressed = interface.last_button_pressed()

    interface.lock_cache()
    if is_generic_tick_button_pressed(button_pressed):
        action_if_macro_tick_button_pressed(
            interface=interface, button_pressed=button_pressed
        )
        save_ticksheet_edits(interface)

    ## Saving
    elif save_menu_button.pressed(button_pressed):
        save_ticksheet_edits(interface)
        set_edit_state_of_ticksheet(interface=interface, state=NO_EDIT_STATE)
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_changes_in_cached_data_to_disk()

    return display_form_view_ticksheets_for_event_and_group(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_view_ticksheets_for_event_and_group
    )
