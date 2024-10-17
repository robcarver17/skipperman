from app.frontend.shared.events_state import get_event_from_state

from app.backend.security.logged_in_user import get_volunteer_for_logged_in_user_or_superuser
from app.backend.security.user_access import can_see_all_groups_and_award_qualifications

from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.abstract_objects.abstract_buttons import Button

from app.frontend.shared.qualification_and_tick_state_storage import (
    get_edit_state_of_ticksheet,
    EDIT_CHECKBOX_STATE,
    EDIT_DROPDOWN_STATE,
    NO_EDIT_STATE,
    return_true_if_a_cadet_id_been_set,
    not_editing,
)

EDIT_DROPDOWN_BUTTON_LABEL = (
    "Edit using dropdown (allows entry of full ticks, half ticks, N/A)"
)
EDIT_CHECKBOX_BUTTON_LABEL = "Edit using checkboxes (allows entry of full ticks only)"
SAVE_BUTTON_LABEL = "Save changes"
PRINT_BUTTON_LABEL = "Print ticksheet to excel file"
SHOW_ALL_CADETS_BUTTON_LABEL = "Show all cadets"


def get_buttons_for_ticksheet(interface: abstractInterface) -> Line:
    if not_editing(interface):
        return get_buttons_for_ticksheet_when_not_editing(interface)
    else:
        ## No buttons, just the save / cancel on top of the nav bar
        return Line([])


def get_buttons_for_ticksheet_when_not_editing(interface: abstractInterface) -> Line:
    list_of_options = [
        edit_checkbox_button,
        edit_dropdown_button,
        print_button,
    ]

    cadet_id_set = return_true_if_a_cadet_id_been_set(interface)
    if cadet_id_set:
        list_of_options.append(show_all_cadets_button)

    return Line(list_of_options)

edit_checkbox_button = Button(EDIT_CHECKBOX_BUTTON_LABEL)
edit_dropdown_button = Button(EDIT_DROPDOWN_BUTTON_LABEL)
print_button = Button(PRINT_BUTTON_LABEL)
show_all_cadets_button = Button(SHOW_ALL_CADETS_BUTTON_LABEL)

def user_can_award_qualifications(interface):
    volunteer = get_volunteer_for_logged_in_user_or_superuser(interface)
    event = get_event_from_state(interface)

    can_award_qualificaiton = can_see_all_groups_and_award_qualifications(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )

    return can_award_qualificaiton


def get_cadet_button_instructions(interface) -> str:
    can_award_qualificaiton = user_can_award_qualifications(interface)
    state = get_edit_state_of_ticksheet(interface)
    cadet_id_set = return_true_if_a_cadet_id_been_set(interface)

    if state == NO_EDIT_STATE:
        if cadet_id_set:
            return 'Cadets with qualifications_and_ticks in brackets are already qualified. Only one cadet displayed. Press "see all cadets" button to see more, or select edit mode'
        else:
            return "Cadets with qualification in brackets are already qualified. Click on a cadet name to see only their ticksheet (useful for mobile)."

    cadet_button_instructions = ""
    if can_award_qualificaiton:
        cadet_button_instructions += "Click on cadet name to award qualification (will set all the ticks to full) or take qualification away. "
        if state == EDIT_CHECKBOX_STATE:
            cadet_button_instructions += "Click on relevant button to set all ticks to full for that cadet without changing qualification status (not possible if cadet already has qualification)"
        else:
            cadet_button_instructions += "Click other buttons next to cadet to set all their ticks to the relevant level without changing qualification status (not possible if cadet already has qualification) "
    else:
        if state == EDIT_CHECKBOX_STATE:
            cadet_button_instructions += "Click on cadet name to set all ticks to full for that cadet. Cadets with qualification in brackets are already qualified and you cannot change their tick status."
        else:
            cadet_button_instructions += "Click on cadet name to set all ticks to full for that cadet. Click other buttons next to cadet to set to other tick status. Cadets with qualification in brackets are already qualified and you cannot change their ticks."

    return cadet_button_instructions


def get_instructions_for_ticksheet(interface: abstractInterface) -> ListOfLines:
    cadet_id_set = return_true_if_a_cadet_id_been_set(interface)
    cadet_button_instructions = get_cadet_button_instructions(interface)

    state = get_edit_state_of_ticksheet(interface)
    if state == EDIT_CHECKBOX_STATE:
        if cadet_id_set:
            column_instruction = ""
        else:
            column_instruction = (
                "Click on column heading to fill in that tick for all cadets"
            )
        return ListOfLines(
            [
                "Click checkboxes to apply or disapply full ticks",
                cadet_button_instructions,
                column_instruction,
                "If you want to apply half ticks or N/A then save and choose dropdown edit. An existing half tick or N/A cannot be edited here",
                "Don't forget to press save when done. Pressing Cancel will lose your changes.",
                "You need to save before you can print.",
            ]
        ).add_Lines()
    elif state == EDIT_DROPDOWN_STATE:
        if cadet_id_set:
            column_instruction = ""
        else:
            column_instruction = "Click on column heading to fill in that tick for all cadets. Click on the buttons next to each column heading to change to that tick for all cadets"
        return ListOfLines(
            [
                "Choose the tick option in each cell.",
                cadet_button_instructions,
                column_instruction,
                "If you want to apply full ticks only press save and then choose checkbox ticking -it's quicker!",
                "Don't forget to press save when done. Pressing Cancel will lose your changes.",
                "You need to save before you can print.",
            ]
        ).add_Lines()
    elif state == NO_EDIT_STATE:
        return ListOfLines(
            [
                "Select dropdown edit if you want to include n/a, ",
                "Select checkbox edit just to do full ticks - this is quicker",
                cadet_button_instructions,
            ]
        ).add_Lines()

    raise Exception("State %s uknown" % state)
