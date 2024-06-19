from app.backend.forms.swaps import is_ready_to_swap
from app.data_access.configuration.configuration import VOLUNTEERS_SKILL_FOR_PB2
from typing import List

from app.backend.volunteers.patrol_boats import \
    get_volunteer_ids_allocated_to_patrol_boat_at_event_on_days_sorted_by_role, \
    get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day
from app.backend.volunteers.volunteers import  get_volunteer_name_from_id, boat_related_skill_for_volunteer
from app.logic.events.patrol_boats.patrol_boat_buttons import get_remove_volunteer_button
from app.logic.events.patrol_boats.copying import get_copy_buttons_for_boat_allocation
from app.logic.events.patrol_boats.swapping import get_swap_buttons_for_boat_rota
from app.logic.events.patrol_boats.patrol_boat_dropdowns import \
    volunteer_boat_role_dropdown
from app.objects.abstract_objects.abstract_form import checkboxInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_tables import RowInTable
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat


def get_volunteer_row_to_select_skill(
        interface: abstractInterface,
        volunteer_id: str,
        ) -> RowInTable:
    name = get_volunteer_name_from_id(interface=interface, volunteer_id=volunteer_id)
    skill_box = volunteer_boat_skill_checkbox(interface=interface, volunteer_id=volunteer_id)

    return RowInTable([name, skill_box])


def get_existing_allocation_elements_for_day_and_boat( interface:abstractInterface,
                                                       patrol_boat: PatrolBoat,
                                                 day: Day,
                                                event: Event
                                                 ) -> ListOfLines:

    list_of_volunteer_ids = get_volunteer_ids_allocated_to_patrol_boat_at_event_on_days_sorted_by_role(
        interface=interface, event=event, day=day, patrol_boat=patrol_boat)
    return ListOfLines([
        get_existing_allocation_elements_for_volunteer_day_and_boat(
            event=event,
            day=day,
            volunteer_id=volunteer_id,
            interface=interface,
            patrol_boat=patrol_boat
        ) for volunteer_id in list_of_volunteer_ids
    ])


def get_existing_allocation_elements_for_volunteer_day_and_boat(
                                                interface:abstractInterface,
                                                 day: Day,
                                                event: Event,
                                                volunteer_id: str,
                                                patrol_boat: PatrolBoat,
                                                 ) -> Line:

    name = get_volunteer_name_from_id(interface=interface, volunteer_id=volunteer_id)
    has_boat_skill = boat_related_skill_for_volunteer(interface=interface, volunteer_id=volunteer_id)
    if has_boat_skill:
        name = "%s (PB2)" % name
    role_dropdown = volunteer_boat_role_dropdown(interface=interface, volunteer_id=volunteer_id, event=event, day=day)
    buttons = get_buttons_for_volunteer_day_and_boat(interface=interface,
                                                     event=event,
                                                     day=day,
                                                     volunteer_id=volunteer_id,
                                                     patrol_boat=patrol_boat)

    return Line([
        name, ' ',
        role_dropdown]+buttons)


def get_buttons_for_volunteer_day_and_boat(
                                                interface:abstractInterface,
                                                 day: Day,
                                                event: Event,
                                                volunteer_id: str,
                                                patrol_boat: PatrolBoat,
                                                 ) -> list:

    in_swap_state = is_ready_to_swap(interface)

    if in_swap_state:
        copy_buttons =[]
        remove_volunteer_button = ""
    else:
        copy_buttons = get_copy_buttons_for_boat_allocation(interface=interface, volunteer_id=volunteer_id, event=event, day=day)
        remove_volunteer_button = get_remove_volunteer_button(day=day, volunteer_id=volunteer_id)

    swap_buttons = get_swap_buttons_for_boat_rota(volunteer_id=volunteer_id, event=event, day=day, interface=interface,
                                                  boat_at_event=patrol_boat)

    return copy_buttons+ \
        swap_buttons+[' ']+ \
        [remove_volunteer_button]



def volunteer_boat_skill_checkbox(interface: abstractInterface, volunteer_id: str) -> checkboxInput:
    has_boat_skill =boat_related_skill_for_volunteer(interface=interface, volunteer_id=volunteer_id)

    dict_of_labels={VOLUNTEERS_SKILL_FOR_PB2: VOLUNTEERS_SKILL_FOR_PB2}
    dict_of_checked={VOLUNTEERS_SKILL_FOR_PB2: has_boat_skill}
    return checkboxInput(
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked,
        input_name=get_volunteer_skill_checkbox_name(volunteer_id=volunteer_id),
        input_label=""
    )

def get_volunteer_skill_checkbox_name(volunteer_id: str) -> str:
    return "VolunterSkill_%s" % (volunteer_id)


def is_volunteer_skill_checkbox_ticked(interface: abstractInterface, volunteer_id: str) -> bool:
    checkbox_name = get_volunteer_skill_checkbox_name(volunteer_id=volunteer_id)
    return VOLUNTEERS_SKILL_FOR_PB2 in interface.value_of_multiple_options_from_form(checkbox_name)


def get_unique_list_of_volunteer_ids_for_skills_checkboxes(interface: abstractInterface, event: Event) -> List[str]:
    list_of_ids = []
    for day in event.weekdays_in_event():
        list_of_volunteer_ids_for_day = get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(interface=interface, event=event, day=day)
        list_of_ids+=list_of_volunteer_ids_for_day

    return list(set(list_of_ids))
