from app.logic.events.events_in_state import get_event_from_state

from app.backend.data.security import get_volunteer_id_of_logged_in_user_or_superuser
from app.backend.ticks_and_qualifications.ticksheets import can_see_all_groups_and_award_qualifications
from app.objects.groups import Group

from app.objects.events import Event

from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.abstract_objects.abstract_buttons import Button

from app.logic.instructors.state_storage import get_edit_state_of_ticksheet, EDIT_CHECKBOX_STATE, EDIT_DROPDOWN_STATE, \
    NO_EDIT_STATE, get_group_from_state

EDIT_DROPDOWN_BUTTON_LABEL = "Edit using dropdown (allows entry of full ticks, half ticks, N/A)"
EDIT_CHECKBOX_BUTTON_LABEL = "Edit using checkboxes (allows entry of full ticks only)"
SAVE_BUTTON_LABEL = "Save changes"
PRINT_BUTTON_LABEL = "Print ticksheet to excel file"


def get_buttons_for_ticksheet(interface: abstractInterface) -> Line:
    state = get_edit_state_of_ticksheet(interface)
    if state in [EDIT_CHECKBOX_STATE, EDIT_DROPDOWN_STATE]:
        return Line([Button(SAVE_BUTTON_LABEL)])

    elif state == NO_EDIT_STATE:
        return Line([Button(EDIT_CHECKBOX_BUTTON_LABEL), Button(EDIT_DROPDOWN_BUTTON_LABEL), Button(PRINT_BUTTON_LABEL)])

    raise Exception("State %s uknown" % state)

def user_can_award_qualifications(interface):
    volunteer_id = get_volunteer_id_of_logged_in_user_or_superuser(interface)
    event = get_event_from_state(interface)

    can_award_qualificaiton= can_see_all_groups_and_award_qualifications(interface=interface, event=event, volunteer_id=volunteer_id)

    if can_award_qualificaiton:
        qual_line = 'Click on cadet name to award qualification or take qualification away'
    else:
        qual_line = ''

    return qual_line

def get_instructions_for_ticksheet(interface: abstractInterface) -> ListOfLines:
    can_award_qualificaiton = user_can_award_qualifications(interface)

    state = get_edit_state_of_ticksheet(interface)
    if state ==EDIT_CHECKBOX_STATE:
        return ListOfLines([
            'Check boxes to apply or disapply full ticks. Click on button next to cadet name to fill in all ticks, click on column heading to fill in that tick for all cadets',
            can_award_qualificaiton,
            'If you want to apply half ticks or N/A then save and choose dropdown edit. An existing half tick or N/A cannot be edited here',
            "Don't forget to press save when done. Pressing Back will lose your changes.",
            "You need to save before you can print."
        ]).add_Lines()
    elif state==EDIT_DROPDOWN_STATE:
        return ListOfLines([
            'Choose the tick option in each cell.",'
            'Click on the buttons next to cadet name to mark all ticks with appropriate marking',
            'Click on the buttons next to each column heading to fill in that tick for all cadets',
            can_award_qualificaiton,
            "If you want to apply full ticks only press save and then choose checkbox ticking -it's quicker!",
            "Don't forget to press save when done. Pressing Back will lose your changes.",
            "You need to save before you can print."
        ]).add_Lines()
    elif state == NO_EDIT_STATE:
        return ListOfLines([
            'Select dropdown edit if you want to include n/a, ',
            'Select checkbox edit just to do full ticks - this is quicker'
        ]).add_Lines()

    raise Exception("State %s uknown" % state)
