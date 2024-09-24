from app.objects_OLD.patrol_boats import ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats, VolunteerAtEventWithSkillsAndRolesAndPatrolBoats

from app.backend.OLD_patrol_boats.patrol_boat_warnings import warn_on_pb2_drivers
from app.OLD_backend.rota.warnings import warn_on_volunteer_qualifications
from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS
from app.data_access.configuration.fixed import COPY_OVERWRITE_SYMBOL, COPY_FILL_SYMBOL, SWAP_SHORTHAND, BOAT_SHORTHAND, \
    ROLE_SHORTHAND, BOAT_AND_ROLE_SHORTHAND, REMOVE_SHORTHAND
from app.objects_OLD.abstract_objects.abstract_buttons import ButtonBar, HelpButton, cancel_menu_button, save_menu_button

from app.data_access.data_layer.ad_hoc_cache import AdHocCache

from app.OLD_backend.forms.swaps import is_ready_to_swap
from typing import List, Union

from app.backend.OLD_patrol_boats.people_on_boats import \
    get_sorted_volunteers_allocated_to_patrol_boat_at_event_on_days_sorted_by_role
from app.backend.OLD_patrol_boats.data import get_list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_data
from app.OLD_backend.volunteers.volunteers import (
    can_volunteer_drive_safety_boat, get_volunteer_from_id,
)
from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    get_remove_volunteer_button, copy_all_boats_button, copy_all_boats_and_roles_button, copyover_all_boats_button,
    copyover_all_boats_and_roles_button,
)
from app.frontend.events.patrol_boats.copying import get_copy_buttons_for_boat_allocation
from app.frontend.events.patrol_boats.swapping import get_swap_buttons_for_boat_rota
from app.frontend.events.patrol_boats.patrol_boat_dropdowns import (
    volunteer_boat_role_dropdown, )
from app.objects_OLD.abstract_objects.abstract_form import checkboxInput, Link
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, DetailListOfLines
from app.objects_OLD.abstract_objects.abstract_tables import RowInTable
from app.objects_OLD.day_selectors import Day
from app.objects_OLD.events import Event
from app.objects_OLD.primtive_with_id.patrol_boats import PatrolBoat


def get_volunteer_row_to_select_skill(
    volunteer_at_event: VolunteerAtEventWithSkillsAndRolesAndPatrolBoats
) -> RowInTable:
    name = volunteer_at_event.volunteer.name
    skill_box = volunteer_boat_skill_checkbox(
         volunteer_at_event=volunteer_at_event
    )

    return RowInTable([name, skill_box])


def get_existing_allocation_elements_for_day_and_boat(
    interface: abstractInterface, patrol_boat: PatrolBoat, day: Day, event: Event
) -> ListOfLines:
    list_of_volunteers = \
        get_sorted_volunteers_allocated_to_patrol_boat_at_event_on_days_sorted_by_role(
            cache=interface.cache,
             event=event, day=day, patrol_boat=patrol_boat
        )

    return ListOfLines(
        [
            get_existing_allocation_elements_for_volunteer_day_and_boat(
                day=day,
                interface=interface,
                volunteer_at_event=volunteer_at_event,
                patrol_boat=patrol_boat

            )
            for volunteer_at_event in list_of_volunteers
        ]
    )


def get_existing_allocation_elements_for_volunteer_day_and_boat(
    interface: abstractInterface,
    day: Day,
    volunteer_at_event: VolunteerAtEventWithSkillsAndRolesAndPatrolBoats,
        patrol_boat: PatrolBoat
) -> Line:
    name = volunteer_at_event.volunteer.name
    has_pb2 = volunteer_at_event.has_pb2_qualification()
    if has_pb2:
        name = "%s (PB2)" % name
    role_dropdown = volunteer_boat_role_dropdown(
        interface=interface, volunteer_id=volunteer_at_event.volunteer.id, event=volunteer_at_event.volunteer_event_data.event, day=day
    )
    buttons = get_buttons_for_volunteer_day_and_boat(
        interface=interface,
        day=day,
        volunteer_at_event=volunteer_at_event,
        patrol_boat=patrol_boat
    )

    return Line([name, " ", role_dropdown] + buttons)


def get_buttons_for_volunteer_day_and_boat(
    interface: abstractInterface,
    day: Day,
    volunteer_at_event: VolunteerAtEventWithSkillsAndRolesAndPatrolBoats,
    patrol_boat: PatrolBoat
) -> list:
    in_swap_state = is_ready_to_swap(interface)

    if in_swap_state:
        copy_buttons = []
        remove_volunteer_button = ""
    else:
        ### FIXME HERE
        copy_buttons = get_copy_buttons_for_boat_allocation(
            interface=interface, volunteer_id=volunteer_at_event.volunteer.id, event=volunteer_at_event.volunteer_event_data.event, day=day
        )
        remove_volunteer_button = get_remove_volunteer_button(
            day=day, volunteer_id=volunteer_at_event.volunteer.id
        )

    swap_buttons = get_swap_buttons_for_boat_rota(
        volunteer_id=volunteer_at_event.volunteer.id,
        event=volunteer_at_event.volunteer_event_data.event,
        day=day,
        interface=interface,
        boat_at_event=patrol_boat,
    )

    return copy_buttons + swap_buttons + [" "] + [remove_volunteer_button]


VOLUNTEERS_SKILL_FOR_PB2 = "PB2"

def volunteer_boat_skill_checkbox(
     volunteer_at_event: VolunteerAtEventWithSkillsAndRolesAndPatrolBoats
) -> checkboxInput:
    has_boat_skill = volunteer_at_event.skills.can_drive_safety_boat

    dict_of_labels = {VOLUNTEERS_SKILL_FOR_PB2: VOLUNTEERS_SKILL_FOR_PB2}
    dict_of_checked = {VOLUNTEERS_SKILL_FOR_PB2: has_boat_skill}
    return checkboxInput(
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked,
        input_name=get_volunteer_skill_checkbox_name(volunteer_id=volunteer_at_event.volunteer.id),
        input_label="",
    )


def get_volunteer_skill_checkbox_name(volunteer_id: str) -> str:
    return "VolunterSkill_%s" % (volunteer_id)


def is_volunteer_skill_checkbox_ticked(
    interface: abstractInterface, volunteer_id: str
) -> bool:
    checkbox_name = get_volunteer_skill_checkbox_name(volunteer_id=volunteer_id)
    return VOLUNTEERS_SKILL_FOR_PB2 in interface.value_of_multiple_options_from_form(
        checkbox_name
    )


def get_unique_list_of_volunteer_ids_for_skills_checkboxes(
    cache: AdHocCache, event: Event
) -> List[str]:
    list_of_volunteers = get_list_of_volunteers_for_skills_checkboxes(cache=cache, event=event)

    return list_of_volunteers.list_of_volunteer_ids()

def get_list_of_volunteers_for_skills_checkboxes(
        cache: AdHocCache, event: Event
) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats:
    return get_list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_data(cache=cache,
                                event=event)


def warn_on_all_volunteers_in_patrol_boats(
    interface: abstractInterface,
        event: Event,
) -> Union[DetailListOfLines, str]:
    qualification_warnings = warn_on_volunteer_qualifications(cache=interface.cache, event=event)
    pb2driver_warnings = warn_on_pb2_drivers(cache=interface.cache, event=event)

    all_warnings = qualification_warnings + pb2driver_warnings

    if len(all_warnings) == 0:
        return ""

    return DetailListOfLines(ListOfLines(all_warnings).add_Lines(), name="Warnings")


def get_button_bar_for_patrol_boats(interface: abstractInterface) -> ButtonBar:
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ButtonBar([])
    help_button = HelpButton("patrol_boat_help")
    return ButtonBar(
        [
            cancel_menu_button,
            save_menu_button,
            copy_all_boats_button,
            copy_all_boats_and_roles_button,
            copyover_all_boats_button,
            copyover_all_boats_and_roles_button,
            help_button,
        ]
    )


link = Link(
    url=WEBLINK_FOR_QUALIFICATIONS, string="Qualifications table", open_new_window=True
)
instructions_qual_table = ListOfLines(
    [
        Line(
            [
                "Tick to specify that a volunteer has PB2 (check don't assume: ",
                link,
                " )",
            ]
        )
    ]
)
instructions_text = ListOfLines(
    [
        Line(
            [
                "Save changes after non button actions. Key for buttons: Copy, fill and overwrite existing ",
                COPY_OVERWRITE_SYMBOL,
                "; Copy and fill any unallocated days ",
                COPY_FILL_SYMBOL,
                "; Swap ",
                SWAP_SHORTHAND,
                " ; ",
                BOAT_SHORTHAND,
                " = boat, ",
                ROLE_SHORTHAND,
                " = role, ",
                BOAT_AND_ROLE_SHORTHAND,
                " = boat & role. " "; Remove from boat: ",
                REMOVE_SHORTHAND,
            ]
        )
    ]
)
