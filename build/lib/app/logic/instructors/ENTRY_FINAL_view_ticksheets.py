from typing import Union

from app.backend.security.logged_in_user import get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER
from app.backend.security.user_access import can_see_all_groups_and_award_qualifications

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.instructors.buttons import (
    get_list_of_all_tick_related_button_names,
    get_list_of_all_possible_select_cadet_buttons,
    set_cadet_id,
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
    EDIT_CHECKBOX_BUTTON_LABEL,
    EDIT_DROPDOWN_BUTTON_LABEL,
    PRINT_BUTTON_LABEL,
    SHOW_ALL_CADETS_BUTTON_LABEL,
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
    clear_cadet_id_in_state,
    not_editing,
)

from app.frontend.shared.events_state import get_event_from_state

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
    ticksheet_table = get_ticksheet_table(
        interface=interface, event=event, qualification=qualification, group=group
    )
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

    volunteer_id = get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER(interface)
    if can_see_all_groups_and_award_qualifications(
        interface=interface,
        event=get_event_from_state(interface),
        volunteer_id=volunteer_id,
    ):
        help = HelpButton("ticksheet_entry_help_SI")
    else:
        help = HelpButton("ticksheet_entry_help")

    navbar.append(help)

    return ButtonBar(navbar)


def post_form_view_ticksheets_for_event_and_group(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    button_pressed = interface.last_button_pressed()
    if cancel_menu_button.pressed(button_pressed):
        ## DOES NOT SAVE
        set_edit_state_of_ticksheet(interface=interface, state=NO_EDIT_STATE)
        return display_form_view_ticksheets_for_event_and_group(interface)

    elif back_menu_button.pressed(button_pressed):
        set_edit_state_of_ticksheet(interface=interface, state=NO_EDIT_STATE)
        clear_cadet_id_in_state(interface)
        return previous_form(interface)

    ### IF STATE EDIT, SAVE EDITS HERE
    save_ticksheet_edits(interface)

    list_of_tick_buttons = get_list_of_all_tick_related_button_names(interface)
    list_of_all_possible_select_cadet_buttons = (
        get_list_of_all_possible_select_cadet_buttons(interface)
    )

    ## Edit state has to change
    if button_pressed == EDIT_DROPDOWN_BUTTON_LABEL:
        set_edit_state_of_ticksheet(interface=interface, state=EDIT_DROPDOWN_STATE)

    elif button_pressed == EDIT_CHECKBOX_BUTTON_LABEL:
        set_edit_state_of_ticksheet(interface=interface, state=EDIT_CHECKBOX_STATE)

    elif save_menu_button.pressed(button_pressed):
        ## already save, but need to change state back to not editing
        set_edit_state_of_ticksheet(interface=interface, state=NO_EDIT_STATE)

    elif button_pressed == PRINT_BUTTON_LABEL:
        return download_labelled_ticksheet_and_return_file(interface)

    elif button_pressed in list_of_all_possible_select_cadet_buttons:
        set_cadet_id(interface=interface, button_pressed=button_pressed)

    elif button_pressed == SHOW_ALL_CADETS_BUTTON_LABEL:
        clear_cadet_id_in_state(interface)

    ## SPECIAL BUTTONS: qualification, all ticks, all column
    elif button_pressed in list_of_tick_buttons:
        action_if_macro_tick_button_pressed(
            interface=interface, button_pressed=button_pressed
        )

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface._save_data_store_cache()

    return display_form_view_ticksheets_for_event_and_group(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_view_ticksheets_for_event_and_group
    )
