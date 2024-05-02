from typing import List

from app.backend.volunteers.volunteer_rota_data import get_explanation_of_sorts_and_filters

from app.backend.volunteers.volunteer_rota_summary import get_summary_list_of_roles_and_groups_for_events, \
    get_summary_list_of_teams_and_groups_for_events
from app.data_access.configuration.configuration import VOLUNTEER_SKILLS, WEBLINK_FOR_QUALIFICATIONS
from app.data_access.configuration.fixed import COPY_SYMBOL1, COPY_SYMBOL2, SWAP_SHORTHAND1, SWAP_SHORTHAND2, \
    NOT_AVAILABLE_SHORTHAND, AVAILABLE_SHORTHAND
from app.logic.events.constants import SAVE_CHANGES

from app.logic.events.volunteer_rota.rota_state import get_skills_filter_from_state, get_sorts_and_filters_from_state
from app.objects.volunteers_in_roles import FILTER_OPTIONS

from app.backend.forms.swaps import is_ready_to_swap
from app.logic.volunteers.ENTRY_view_volunteers import all_sort_types as all_volunteer_name_sort_types
from app.objects.abstract_objects.abstract_buttons import ButtonBar, Button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import MaterialAroundTable, checkboxInput, Link, dropDownInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________, DetailListOfLines
from app.objects.day_selectors import Day
from app.objects.events import Event



def get_filters_and_buttons(interface: abstractInterface, event: Event) -> MaterialAroundTable:
    if is_ready_to_swap(interface):
        return MaterialAroundTable(null_list_of_lines, null_list_of_lines)

    sorts_and_filters = get_sorts_and_filters_from_state(interface)
    explain_all_sorts_and_filters = get_explanation_of_sorts_and_filters(sorts_and_filters)

    sort_buttons = get_all_volunteer_sort_buttons()
    action_buttons = get_action_buttons_for_rota()
    skills_filter = get_volunteer_skills_filter(interface)
    availablility_filter = get_availability_for_volunteers_filter(interface=interface, event=event)
    before_table =  ListOfLines(
            [
                action_buttons,
                skills_filter,
                availablility_filter,
                Line([filter_button,clear_filter_button]),
                sort_buttons,
                Line([explain_all_sorts_and_filters]),
                _______________])

    after_table = ListOfLines([
                action_buttons
            ])

    return MaterialAroundTable(before_table=before_table, after_table=after_table)



def get_availability_for_volunteers_filter(interface: abstractInterface, event: Event) -> Line:
    days_in_event = event.weekdays_in_event()
    availability_filters = [get_available_filter_for_day(day=day) for day in days_in_event]

    return Line(["   Choose daily availability / allocation status to filter volunteers by"]+availability_filters)


def get_available_filter_for_day( day: Day):
    list_of_options = [construct_filter_entry(day, option) for option in FILTER_OPTIONS]
    dict_of_options = dict([(option, option) for option in list_of_options])
    return dropDownInput(
      input_name=get_available_filter_name_for_day(day),
        dict_of_options=dict_of_options,
        input_label=""
    )

def get_available_filter_name_for_day(day: Day):
    return "filterAv_"+day.name

def construct_filter_entry(day:Day, option: str)->str:
    return "%s:%s" % (day.name, option)

def from_filter_entry_to_option(filter_entry:str) ->str:
    return filter_entry.split(":")[1]

null_list_of_lines = ListOfLines([_______________])


def get_all_volunteer_sort_buttons() -> ButtonBar:
    name_sort_buttons = get_volunteer_name_sort_buttons()
    cadet_location_sort = Button(SORT_BY_CADET_LOCATION, nav_button=True)

    return ButtonBar([cadet_location_sort]+name_sort_buttons)


SORT_BY_CADET_LOCATION = "Sort by cadet location"


def get_volunteer_name_sort_buttons() ->List[Button]:
    return [Button(sort_by, nav_button=True) for sort_by in all_volunteer_name_sort_types]

def get_volunteer_skills_filter(interface: abstractInterface):
    dict_of_labels = dict([(skill, skill) for skill in VOLUNTEER_SKILLS])
    dict_of_checked = get_skills_filter_from_state(interface)
    return checkboxInput(input_label="Filter for volunteers with these skills",
                         dict_of_checked=dict_of_checked,
                         dict_of_labels=dict_of_labels,
                         input_name=SKILLS_FILTER,
                         line_break=False)

SKILLS_FILTER = "skills_filter"
APPLY_FILTER_BUTTON_LABEL = "Apply filters"
CLEAR_FILTERS_BUTTON_LABEL = "Clear all filters"

filter_button = Button(APPLY_FILTER_BUTTON_LABEL, nav_button=True)
clear_filter_button = Button(CLEAR_FILTERS_BUTTON_LABEL, nav_button=True)

def get_header_buttons_for_rota():
    return ButtonBar([Button(BACK_BUTTON_LABEL, nav_button=True)])


def get_action_buttons_for_rota():
    return ButtonBar([
        Button(ADD_NEW_VOLUNTEER_BUTTON_LABEL, nav_button=True),
        Button(BACK_BUTTON_LABEL, nav_button=True),
        Button(SAVE_CHANGES, nav_button=True)
    ])


def get_summary_table(interface: abstractInterface, event: Event):
    summary_of_filled_roles =  get_summary_list_of_roles_and_groups_for_events(event=event, interface=interface)
    if len(summary_of_filled_roles) > 0:
        summary_of_filled_roles = DetailListOfLines(ListOfLines([
                summary_of_filled_roles]), name='Summary by role / group')
    else:
        summary_of_filled_roles=""

    return summary_of_filled_roles

def get_summary_group_table(interface: abstractInterface, event: Event):
    summary_of_filled_roles =  get_summary_list_of_teams_and_groups_for_events(event=event, interface=interface)
    if len(summary_of_filled_roles) > 0:
        summary_of_filled_roles = DetailListOfLines(ListOfLines([
                summary_of_filled_roles]), name='Summary by team/ group')
    else:
        summary_of_filled_roles=""

    return summary_of_filled_roles




link = Link(url=WEBLINK_FOR_QUALIFICATIONS, string="See qualifications table", open_new_window=True)
instructions = ListOfLines(["BACK will cancel any changes you make; any other button will save them",
                            Line(["Key for buttons - Copy: ",
                                        COPY_SYMBOL1, COPY_SYMBOL2,
                                        " ; Swap: ", SWAP_SHORTHAND1, SWAP_SHORTHAND2, ", ",
                                        '; Raincheck: make unavailable: ', NOT_AVAILABLE_SHORTHAND ,
                                        '; Available, but role undefined', AVAILABLE_SHORTHAND]),

                            "Click on any day column heading to sort by group and role, or sort volunteers by name, or by the location of their cadet(s)",
                            "Click on volunteer names to see roles done at previous events, edit days attending, or remove from event. Click on location to see and edit connected cadets. Click on skills to edit volunteer skills.",
                            "Click on 'unavailable' days to make a volunteer available. Select role = unavailable to make a volunteer unavailable",
                            "Save after selecting role to see possible group allocations where relevant.",
                            "You can copy roles/groups to other days to avoid tiresome re-entry",
                            "Enter any relevant notes, eg will arrive late etc",
                            "Click on summary triangle tabs above to see count of volunteers allocated so far",
                            link]).add_Lines()

ADD_NEW_VOLUNTEER_BUTTON_LABEL = "Add new volunteer to rota"
