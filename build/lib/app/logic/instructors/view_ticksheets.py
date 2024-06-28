from typing import Union

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.instructors.buttons import get_list_of_all_tick_related_button_names, \
    get_list_of_all_possible_select_cadet_buttons, set_cadet_id
from app.logic.instructors.parse_ticksheet_table import save_ticksheet_edits
from app.logic.instructors.parse_macro_buttons_in_ticksheets import action_if_macro_tick_button_pressed
from app.logic.instructors.print_ticksheet import download_labelled_ticksheet_and_return_file

from app.logic.instructors.render_ticksheet_table import get_ticksheet_table
from app.logic.instructors.ticksheet_table_elements import get_buttons_for_ticksheet, get_instructions_for_ticksheet, \
    EDIT_CHECKBOX_BUTTON_LABEL, EDIT_DROPDOWN_BUTTON_LABEL, SAVE_BUTTON_LABEL, PRINT_BUTTON_LABEL, \
    SHOW_ALL_CADETS_BUTTON_LABEL
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, \
    get_nav_bar_with_just_back_button

from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________

from app.logic.shared.qualification_and_tick_state_storage import get_group_from_state, get_qualification_from_state, \
    set_edit_state_of_ticksheet, \
    EDIT_CHECKBOX_STATE, EDIT_DROPDOWN_STATE, NO_EDIT_STATE, get_edit_state_of_ticksheet, clear_cadet_id_in_state

from app.logic.events.events_in_state import get_event_from_state

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, File,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_view_ticksheets_for_event_and_group(interface: abstractInterface) -> Form:
    ### options: print, edit, add qualifications (super users only)
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    qualification = get_qualification_from_state(interface)
    navbar = get_nav_bar_with_just_back_button()
    buttons = get_buttons_for_ticksheet(interface)
    instructions = get_instructions_for_ticksheet(interface=interface)

    ticksheet_table = get_ticksheet_table(interface=interface,
                                          event=event,
                                          qualification=qualification,
                                          group=group)
    header = Line(
        Heading("Tick sheets 'Tickerman': Event %s, group %s, qualification %s" % (str(event), str(group), str(qualification)),
                centred=False, size=4))
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



def post_form_view_ticksheets_for_event_and_group(interface: abstractInterface) -> Union[Form, NewForm, File]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == BACK_BUTTON_LABEL:
        state = get_edit_state_of_ticksheet(interface)
        if state == NO_EDIT_STATE:
            ## DOES NOT SAVE
            return previous_form(interface)
        else:
            ## DOES NOT SAVE
            set_edit_state_of_ticksheet(interface=interface, state=NO_EDIT_STATE)
            return display_form_view_ticksheets_for_event_and_group(interface)

    ### IF STATE EDIT, SAVE EDITS HERE
    save_ticksheet_edits(interface)

    list_of_tick_buttons = get_list_of_all_tick_related_button_names(interface)
    list_of_all_possible_select_cadet_buttons = get_list_of_all_possible_select_cadet_buttons(interface)

    ## Edit state has to change
    if button_pressed == EDIT_DROPDOWN_BUTTON_LABEL:
        set_edit_state_of_ticksheet(interface=interface, state=EDIT_DROPDOWN_STATE)

    elif button_pressed == EDIT_CHECKBOX_BUTTON_LABEL:
        set_edit_state_of_ticksheet(interface=interface, state=EDIT_CHECKBOX_STATE)

    elif button_pressed == SAVE_BUTTON_LABEL:
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
        action_if_macro_tick_button_pressed(interface=interface, button_pressed=button_pressed)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()

    return display_form_view_ticksheets_for_event_and_group(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_view_ticksheets_for_event_and_group)

