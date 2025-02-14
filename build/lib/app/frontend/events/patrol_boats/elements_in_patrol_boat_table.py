from app.backend.volunteers.skills import get_dict_of_existing_skills_for_volunteer

from app.objects.volunteers import ListOfVolunteers, Volunteer

from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    get_list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_day,
)
from app.backend.patrol_boats.volunteers_patrol_boats_skills_and_roles_in_event import (
    get_sorted_volunteers_allocated_to_patrol_boat_at_event_on_days_sorted_by_role,
)

from app.data_access.store.object_store import ObjectStore

from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import (
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoats,
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
)

from app.backend.patrol_boats.patrol_boat_warnings import warn_on_pb2_drivers
from app.backend.volunteers.warnings import warn_on_volunteer_qualifications
from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS
from app.data_access.configuration.fixed import (
    COPY_OVERWRITE_SYMBOL,
    COPY_FILL_SYMBOL,
    SWAP_SHORTHAND,
    BOAT_SHORTHAND,
    ROLE_SHORTHAND,
    BOAT_AND_ROLE_SHORTHAND,
    REMOVE_SHORTHAND,
)
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    HelpButton,
    cancel_menu_button,
    save_menu_button,
)

from app.frontend.forms.swaps import is_ready_to_swap
from typing import List, Union

from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    get_remove_volunteer_button,
    copy_all_boats_button,
    copy_all_boats_and_roles_button,
    copyover_all_boats_button,
    copyover_all_boats_and_roles_button,
)
from app.frontend.events.patrol_boats.copying import (
    get_copy_buttons_for_boat_allocation,
)
from app.frontend.events.patrol_boats.swapping import get_swap_buttons_for_boat_rota
from app.frontend.events.patrol_boats.patrol_boat_dropdowns import (
    volunteer_boat_role_dropdown,
)
from app.objects.abstract_objects.abstract_form import checkboxInput, Link
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    DetailListOfLines,
)
from app.objects.abstract_objects.abstract_tables import RowInTable
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat


def get_volunteer_row_to_select_skill(
    interface: abstractInterface,
    volunteer: Volunteer,
) -> RowInTable:
    name = volunteer.name
    skill_box = volunteer_boat_skill_checkbox(interface=interface, volunteer=volunteer)

    return RowInTable([name, skill_box])


def get_existing_allocation_elements_for_day_and_boat(
    interface: abstractInterface, patrol_boat: PatrolBoat, day: Day, event: Event
) -> ListOfLines:
    object_store = interface.object_store
    list_of_volunteers_at_event_on_boats = (
        get_sorted_volunteers_allocated_to_patrol_boat_at_event_on_days_sorted_by_role(
            object_store=object_store,
            event=event,
            day=day,
            patrol_boat=patrol_boat,
        )
    )

    return ListOfLines(
        [
            get_existing_allocation_elements_for_volunteer_day_and_boat(
                interface=interface,
                volunteer_at_event_on_boat=volunteer_at_event_on_boat,
            )
            for volunteer_at_event_on_boat in list_of_volunteers_at_event_on_boats
        ]
    )


def get_existing_allocation_elements_for_volunteer_day_and_boat(
    interface: abstractInterface,
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> Line:
    name = volunteer_at_event_on_boat.volunteer.name
    has_pb2 = volunteer_at_event_on_boat.skills.can_drive_safety_boat
    if has_pb2:
        name = "%s[PB2] " % name

    group = volunteer_at_event_on_boat.role_and_group.group
    role = volunteer_at_event_on_boat.role_and_group.role
    if group.is_unallocated or not role.associate_sailing_group:
        group_name = ""
    else:
        group_name = "%s" % group.name

    role_dropdown = volunteer_boat_role_dropdown(
        interface=interface,
        volunteer_at_event_on_boat=volunteer_at_event_on_boat,
    )
    buttons = get_buttons_for_volunteer_day_and_boat(
        interface=interface,
        volunteer_at_event_on_boat=volunteer_at_event_on_boat,
    )

    return Line([name, " ", role_dropdown, group_name] + buttons)


def get_buttons_for_volunteer_day_and_boat(
    interface: abstractInterface,
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> list:
    in_swap_state = is_ready_to_swap(interface)

    if in_swap_state:
        copy_buttons = []
        remove_volunteer_button = ""
    else:
        copy_buttons = get_copy_buttons_for_boat_allocation(
            volunteer_at_event_on_boat=volunteer_at_event_on_boat
        )
        remove_volunteer_button = get_remove_volunteer_button(
            day=volunteer_at_event_on_boat.day,
            volunteer_id=volunteer_at_event_on_boat.volunteer.id,
        )

    swap_buttons = get_swap_buttons_for_boat_rota(
        interface=interface, volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )

    return copy_buttons + swap_buttons + [" "] + [remove_volunteer_button]


VOLUNTEERS_SKILL_FOR_PB2 = "PB2"


def volunteer_boat_skill_checkbox(
    interface: abstractInterface,
    volunteer: Volunteer,
) -> checkboxInput:
    skills = get_dict_of_existing_skills_for_volunteer(
        object_store=interface.object_store, volunteer=volunteer
    )
    has_boat_skill = skills.can_drive_safety_boat

    dict_of_labels = {VOLUNTEERS_SKILL_FOR_PB2: VOLUNTEERS_SKILL_FOR_PB2}
    dict_of_checked = {VOLUNTEERS_SKILL_FOR_PB2: has_boat_skill}
    return checkboxInput(
        dict_of_labels=dict_of_labels,
        dict_of_checked=dict_of_checked,
        input_name=get_volunteer_skill_checkbox_name(volunteer_id=volunteer.id),
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


def get_unique_list_of_volunteers_for_skills_checkboxes(
    object_store: ObjectStore, event: Event
) -> ListOfVolunteers:
    list_of_volunteers = get_list_of_volunteers_for_skills_checkboxes(
        object_store=object_store, event=event
    )

    return list_of_volunteers


def get_list_of_volunteers_for_skills_checkboxes(
    object_store: ObjectStore, event: Event
) -> ListOfVolunteers:
    return get_list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_day(
        object_store=object_store, event=event
    )


def warn_on_all_volunteers_in_patrol_boats(
    interface: abstractInterface,
    event: Event,
) -> Union[DetailListOfLines, str]:
    qualification_warnings = warn_on_volunteer_qualifications(
        object_store=interface.object_store, event=event
    )
    pb2driver_warnings = warn_on_pb2_drivers(
        object_store=interface.object_store, event=event
    )

    all_warnings = qualification_warnings + pb2driver_warnings

    if len(all_warnings) == 0:
        return ""

    return DetailListOfLines(ListOfLines(all_warnings).add_Lines(), name="Warnings")


def get_top_button_bar_for_patrol_boats(interface: abstractInterface) -> ButtonBar:
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ButtonBar([])
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

def get_bottom_button_bar_for_patrol_boats(interface: abstractInterface) -> ButtonBar:
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ButtonBar([])
    return ButtonBar(
        [
            cancel_menu_button,
            save_menu_button,
            help_button,
        ]
    )

help_button = HelpButton("patrol_boat_help")

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
