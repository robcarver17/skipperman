from typing import List

from app.backend.patrol_boats.changes import copy_across_earliest_allocation_of_boats_at_event
from app.backend.patrol_boats.volunteers_patrol_boats_skills_and_roles_in_event import \
    get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.rota.copying import copy_earliest_valid_role_and_overwrite_for_volunteer, \
    copy_earliest_valid_role_to_all_empty_for_volunteer
from app.backend.patrol_boats.copying import volunteer_has_at_least_one_allocated_role_which_matches_others, \
    is_possible_to_copy_boat_allocation, is_possible_to_copy_boat_and_role_allocation, \
    is_possible_to_copy_fill_boat_and_role_allocation, \
    volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill, \
    is_required_to_copy_overwrite_boat_and_role_allocation, \
    volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill, \
    volunteer_has_at_least_one_allocated_boat_which_matches_others
from app.data_access.configuration.fixed import (
    COPY_OVERWRITE_SYMBOL,
    BOAT_SHORTHAND,
    BOAT_AND_ROLE_SHORTHAND,
    ROLE_SHORTHAND,
    COPY_FILL_SYMBOL,
)
from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    generic_button_name_for_volunteer_in_boat_at_event_on_day,
    get_list_of_generic_buttons_for_each_volunteer_day_combo,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import \
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday
from app.objects.day_selectors import Day
from app.objects.events import Event

COPY_OVERWRITE_BOAT_BUTTON_LABEL = Line([COPY_OVERWRITE_SYMBOL, BOAT_SHORTHAND])
COPY_OVERWRITE_BOTH_BUTTON_LABEL = Line(
    [COPY_OVERWRITE_SYMBOL, BOAT_AND_ROLE_SHORTHAND]
)
COPY_OVERWRITE_ROLE_BUTTON_LABEL = Line([COPY_OVERWRITE_SYMBOL, ROLE_SHORTHAND])

COPY_FILL_BOAT_BUTTON_LABEL = Line([COPY_FILL_SYMBOL, BOAT_SHORTHAND])
COPY_FILL_BOTH_BUTTON_LABEL = Line([COPY_FILL_SYMBOL, BOAT_AND_ROLE_SHORTHAND])
COPY_FILL_ROLE_BUTTON_LABEL = Line([COPY_FILL_SYMBOL, ROLE_SHORTHAND])


def get_copy_buttons_for_boat_allocation(
        volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday

) -> List[Button]:
    copy_boat_buttons = get_copy_buttons_for_boat_copy_in_boat_rota(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )
    copy_both_buttons = get_copy_buttons_for_role_and_boat_in_rota(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat    )

    copy_role_buttons = get_copy_buttons_for_role_in_boat_rota(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat    )

    return copy_boat_buttons + copy_role_buttons + copy_both_buttons


def get_copy_buttons_for_boat_copy_in_boat_rota(
        volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday
) -> List[Button]:
    copy_fill_possible = (
        volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
            volunteer_at_event_on_boat
        )
    )
    any_copy_possible = is_possible_to_copy_boat_allocation(
        volunteer_at_event_on_boat
    )
    overwrite_copy_required = (
        not volunteer_has_at_least_one_allocated_boat_which_matches_others(
            volunteer_at_event_on_boat
        )
    )

    overwrite_copy_button_name = (
        copy_overwrite_button_name_for_boat_copy_in_boat_at_event_on_day(
            day=volunteer_at_event_on_boat.day,
            volunteer_id=volunteer_at_event_on_boat.volunteer.id,
        )
    )
    fill_button_name = copy_fill_button_name_for_boat_copy_in_boat_at_event_on_day(
        day=volunteer_at_event_on_boat.day,
        volunteer_id=volunteer_at_event_on_boat.volunteer.id,
    )
    overwrite_button = Button(
        label=COPY_OVERWRITE_BOAT_BUTTON_LABEL, value=overwrite_copy_button_name
    )
    fill_button = Button(label=COPY_FILL_BOAT_BUTTON_LABEL, value=fill_button_name)

    if any_copy_possible:
        buttons = []
        if overwrite_copy_required:
            buttons.append(overwrite_button)
        if copy_fill_possible:
            buttons.append(fill_button)
    else:
        buttons = [""]

    return buttons


def get_copy_buttons_for_role_in_boat_rota(
        volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday
) -> List[Button]:
    any_copy_possible = is_possible_to_copy_roles_for_non_grouped_roles_only(
volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )
    copy_fill_possible = (
        volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
            volunteer_at_event_on_boat=volunteer_at_event_on_boat        )
    )
    overwrite_copy_required = (
        not volunteer_has_at_least_one_allocated_role_which_matches_others(
            volunteer_at_event_on_boat=volunteer_at_event_on_boat
        )
    )
    day = volunteer_at_event_on_boat.day
    volunteer_id = volunteer_at_event_on_boat.volunteer.id
    copy_overwrite_button_name = (
        copy_overwrite_button_name_for_volunteer_role_in_boat_at_event_on_day(
            day=day,
            volunteer_id=volunteer_id,
        )
    )
    copy_fill_button_name = (
        copy_fill_button_name_for_volunteer_role_in_boat_at_event_on_day(
            day=day, volunteer_id=volunteer_id
        )
    )

    copy_overwrite_button = Button(
        label=COPY_OVERWRITE_ROLE_BUTTON_LABEL, value=copy_overwrite_button_name
    )
    copy_fill_button = Button(
        label=COPY_FILL_ROLE_BUTTON_LABEL, value=copy_fill_button_name
    )

    if any_copy_possible:
        buttons = []
        if overwrite_copy_required:
            buttons.append(copy_overwrite_button)
        if copy_fill_possible:
            buttons.append(copy_fill_button)
    else:
        buttons = [""]

    return buttons


def get_copy_buttons_for_role_and_boat_in_rota(
        volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday

) -> List[Button]:
    any_copy_possible = is_possible_to_copy_boat_and_role_allocation(
        volunteer_at_event_on_boat
    )
    fill_copy_possible = is_possible_to_copy_fill_boat_and_role_allocation(
        volunteer_at_event_on_boat
    )
    overwrite_copy_required = is_required_to_copy_overwrite_boat_and_role_allocation(
        volunteer_at_event_on_boat
    )

    copy_overwrite_button_name = (
        copy_overwrite_button_name_for_both_volunteer_role_and_boat_at_event_on_day(
            day=volunteer_at_event_on_boat.day,
            volunteer_id=volunteer_at_event_on_boat.volunteer.id,
        )
    )
    copy_fill_button_name = (
        copy_fill_button_name_for_both_volunteer_role_and_boat_at_event_on_day(
            day=volunteer_at_event_on_boat.day,
            volunteer_id=volunteer_at_event_on_boat.volunteer.id,
        )
    )

    overwrite_button = Button(
        label=COPY_OVERWRITE_BOTH_BUTTON_LABEL, value=copy_overwrite_button_name
    )
    fill_button = Button(label=COPY_FILL_BOTH_BUTTON_LABEL, value=copy_fill_button_name)

    if any_copy_possible:
        buttons = []
        if overwrite_copy_required:
            buttons.append(overwrite_button)
        if fill_copy_possible:
            buttons.append(fill_button)
    else:
        buttons = [""]

    return buttons


COPY_BOAT_OVERWRITE = "copyOverwriteBoatButton"
COPY_ROLE_OVERWRITE = "copyOverwriteRoleButton"
COPY_BOTH_OVERWRITE = "copyOverwriteBothButton"

COPY_BOAT_FILL = "copyFillBoatButton"
COPY_ROLE_FILL = "copyFillRoleButton"
COPY_BOTH_FILL = "copyFillBothButton"


def copy_overwrite_button_name_for_boat_copy_in_boat_at_event_on_day(
    day: Day, volunteer_id: str
) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        button_type=COPY_BOAT_OVERWRITE, day=day, volunteer_id=volunteer_id
    )


def copy_fill_button_name_for_boat_copy_in_boat_at_event_on_day(
    day: Day, volunteer_id: str
) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        button_type=COPY_BOAT_FILL, day=day, volunteer_id=volunteer_id
    )


def copy_overwrite_button_name_for_volunteer_role_in_boat_at_event_on_day(
    day: Day, volunteer_id: str
) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        button_type=COPY_ROLE_OVERWRITE, day=day, volunteer_id=volunteer_id
    )


def copy_fill_button_name_for_volunteer_role_in_boat_at_event_on_day(
    day: Day, volunteer_id: str
) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        button_type=COPY_ROLE_FILL, day=day, volunteer_id=volunteer_id
    )


def copy_overwrite_button_name_for_both_volunteer_role_and_boat_at_event_on_day(
    day: Day, volunteer_id: str
) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        button_type=COPY_BOTH_OVERWRITE, day=day, volunteer_id=volunteer_id
    )


def copy_fill_button_name_for_both_volunteer_role_and_boat_at_event_on_day(
    day: Day, volunteer_id: str
) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        button_type=COPY_BOTH_FILL, day=day, volunteer_id=volunteer_id
    )


def get_list_of_all_types_of_copy_buttons(
    interface: abstractInterface, event: Event
) -> List[str]:
    return (
        get_list_of_all_copy_overwrite_boat_buttons_for_boat_allocation(
            interface=interface, event=event
        )
        + get_list_of_all_copy_overwrite_role_buttons_for_boat_allocation(
            interface=interface, event=event
        )
        + get_list_of_all_copy_overwrite_both_buttons_for_boat_allocation(
            interface=interface, event=event
        )
        + get_list_of_all_copy_fill_boat_buttons_for_boat_allocation(
            interface=interface, event=event
        )
        + get_list_of_all_copy_fill_role_buttons_for_boat_allocation(
            interface=interface, event=event
        )
        + get_list_of_all_copy_fill_both_buttons_for_boat_allocation(
            interface=interface, event=event
        )
    )


def get_list_of_all_copy_overwrite_boat_buttons_for_boat_allocation(
    interface: abstractInterface, event: Event
) -> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        interface=interface,
        event=event,
        button_name_function=copy_overwrite_button_name_for_boat_copy_in_boat_at_event_on_day,
    )


def get_list_of_all_copy_fill_boat_buttons_for_boat_allocation(
    interface: abstractInterface, event: Event
) -> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        interface=interface,
        event=event,
        button_name_function=copy_fill_button_name_for_boat_copy_in_boat_at_event_on_day,
    )


def get_list_of_all_copy_overwrite_role_buttons_for_boat_allocation(
    interface: abstractInterface, event: Event
) -> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        interface=interface,
        event=event,
        button_name_function=copy_overwrite_button_name_for_volunteer_role_in_boat_at_event_on_day,
    )


def get_list_of_all_copy_fill_role_buttons_for_boat_allocation(
    interface: abstractInterface, event: Event
) -> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        interface=interface,
        event=event,
        button_name_function=copy_fill_button_name_for_volunteer_role_in_boat_at_event_on_day,
    )


def get_list_of_all_copy_overwrite_both_buttons_for_boat_allocation(
    interface: abstractInterface, event: Event
) -> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        interface=interface,
        event=event,
        button_name_function=copy_overwrite_button_name_for_both_volunteer_role_and_boat_at_event_on_day,
    )


def get_list_of_all_copy_fill_both_buttons_for_boat_allocation(
    interface: abstractInterface, event: Event
) -> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        interface=interface,
        event=event,
        button_name_function=copy_fill_button_name_for_both_volunteer_role_and_boat_at_event_on_day,
    )


def copy_across_all_boats(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
        object_store=interface.object_store, event=event
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=False,
        )


def overwrite_allocation_across_all_boats(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
        object_store=interface.object_store, event=event
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=True,
        )



def copy_across_all_boats_and_roles(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
        object_store=interface.object_store, event=event
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=False,
        )
        copy_earliest_valid_role_to_all_empty_for_volunteer(
            object_store=interface.object_store, event=event, volunteer=volunteer_with_boat_data.volunteer
        )


def overwrite_copy_across_all_boats_and_roles(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
        object_store=interface.object_store, event=event
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=True,
        )
        copy_earliest_valid_role_and_overwrite_for_volunteer(
            object_store=interface.object_store, event=event, volunteer=volunteer_with_boat_data.volunteer
        )

def is_possible_to_copy_roles_for_non_grouped_roles_only(
        volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday

) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    role_today = volunteer_at_event_on_boat.role_and_group.role
    if role_today.is_no_role_set():
        return False

    all_roles = volunteer_at_event_on_boat.role_and_group_by_day.list_of_roles()

    no_roles_to_copy = len(all_roles) == 0
    all_roles_match = len(set(all_roles)) <= 1

    roles_require_groups = [
        role.associate_sailing_group
        for role in all_roles
    ]
    at_least_one_role_require_group = any(roles_require_groups)

    ## copy not possible if all roles the same, or at least one requires a group, or nothing to copy
    if all_roles_match or at_least_one_role_require_group or no_roles_to_copy:
        return False
    else:
        return True

