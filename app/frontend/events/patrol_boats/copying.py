from typing import List, Union

from app.backend.patrol_boats.changes import (
    copy_across_earliest_allocation_of_boats_at_event,
)
from app.backend.patrol_boats.volunteers_patrol_boats_skills_and_roles_in_event import (
    get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats,
)
from app.frontend.shared.buttons import is_button_of_type

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.rota.copying import (
    copy_earliest_valid_role_and_overwrite_for_volunteer,
    copy_earliest_valid_role_to_all_empty_for_volunteer,
)
from app.backend.patrol_boats.copying import (
    volunteer_has_at_least_one_allocated_role_which_matches_others,
    is_possible_to_copy_boat_allocation,
    is_possible_to_copy_boat_and_role_allocation,
    is_possible_to_copy_fill_boat_and_role_allocation,
    volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill,
    is_required_to_copy_overwrite_boat_and_role_allocation,
    volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill,
    volunteer_has_at_least_one_allocated_boat_which_matches_others,
    is_possible_to_copy_roles,
)
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
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import (
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
)
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
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> List[Button]:
    copy_boat_buttons = get_copy_buttons_for_boat_copy_in_boat_rota(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )
    copy_both_buttons = get_copy_buttons_for_role_and_boat_in_rota(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )

    copy_role_buttons = get_copy_buttons_for_role_in_boat_rota(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )

    return copy_boat_buttons + copy_role_buttons + copy_both_buttons


def get_copy_buttons_for_boat_copy_in_boat_rota(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> List[Union[Button, str]]:

    any_copy_possible = is_possible_to_copy_boat_allocation(volunteer_at_event_on_boat)

    if not any_copy_possible:
        return [""]

    copy_fill_possible = (
        volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
            volunteer_at_event_on_boat
        )
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

    buttons = []
    if overwrite_copy_required:
        buttons.append(overwrite_button)
    if copy_fill_possible:
        buttons.append(fill_button)

    return buttons


def get_copy_buttons_for_role_in_boat_rota(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> List[Union[Button, str]]:

    any_copy_possible = is_possible_to_copy_roles(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )
    if not any_copy_possible:
        return [""]

    copy_fill_possible = (
        volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
            volunteer_at_event_on_boat=volunteer_at_event_on_boat
        )
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
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> List[Union[Button, str]]:
    any_copy_possible = is_possible_to_copy_boat_and_role_allocation(
        volunteer_at_event_on_boat
    )
    if not any_copy_possible:
        return [""]

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

    buttons = []
    if overwrite_copy_required:
        buttons.append(overwrite_button)
    if fill_copy_possible:
        buttons.append(fill_button)

    return buttons


COPY_BOAT_OVERWRITE = "copyOverwriteBoatButton"
COPY_ROLE_OVERWRITE = "copyOverwriteRoleButton"
COPY_BOTH_OVERWRITE = "copyOverwriteBothButton"

COPY_BOAT_FILL = "copyFillBoatButton"
COPY_ROLE_FILL = "copyFillRoleButton"
COPY_BOTH_FILL = "copyFillBothButton"

def is_copy_button(button_value:str):
    return is_copy_overwrite_boat_button(button_value) or \
    is_copy_overwrite_role_button(button_value) or \
    is_copy_overwrite_both_button(button_value) or \
    \
    is_copy_boat_fill_button(button_value) or \
    is_copy_role_fill_button(button_value) or \
    is_copy_both_fill_button(button_value)

def is_copy_overwrite_boat_button(button_value: str):
    return is_button_of_type(value_of_button_pressed=button_value, type_to_check=COPY_BOAT_OVERWRITE)

def is_copy_overwrite_role_button(button_value: str):
    return is_button_of_type(value_of_button_pressed=button_value, type_to_check=COPY_ROLE_OVERWRITE)

def is_copy_overwrite_both_button(button_value: str):
    return is_button_of_type(value_of_button_pressed=button_value, type_to_check=COPY_BOTH_OVERWRITE)

def is_copy_boat_fill_button(button_value: str):
    return is_button_of_type(value_of_button_pressed=button_value, type_to_check=COPY_BOAT_FILL)

def is_copy_role_fill_button(button_value: str):
    return is_button_of_type(value_of_button_pressed=button_value, type_to_check=COPY_ROLE_FILL)

def is_copy_both_fill_button(button_value: str):
    return is_button_of_type(value_of_button_pressed=button_value, type_to_check=COPY_BOTH_FILL)



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



def copy_across_all_boats(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=False,
        )


def overwrite_allocation_across_all_boats(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=True,
        )


def copy_across_all_boats_and_roles(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=False,
        )
        copy_earliest_valid_role_to_all_empty_for_volunteer(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer_with_boat_data.volunteer,
        )


def overwrite_copy_across_all_boats_and_roles(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=True,
        )
        copy_earliest_valid_role_and_overwrite_for_volunteer(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer_with_boat_data.volunteer,
        )
