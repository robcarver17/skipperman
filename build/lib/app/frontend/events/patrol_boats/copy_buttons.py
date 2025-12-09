from dataclasses import dataclass
from typing import List, Union

from app.backend.patrol_boats.copying import (
    is_possible_to_copy_boat_allocation,
    volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill,
    volunteer_has_at_least_one_allocated_boat_which_matches_others,
    is_possible_to_copy_roles,
    volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill,
    volunteer_has_at_least_one_allocated_role_which_matches_others,
    is_possible_to_copy_boat_and_role_allocation,
    is_possible_to_copy_fill_boat_and_role_allocation,
    is_required_to_copy_overwrite_boat_and_role_allocation,
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
)
from app.frontend.shared.buttons import is_button_of_type
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import (
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
)
from app.objects.day_selectors import Day


access_copy_menu_button = Button(
    "Copy/Overwrite patrol boats and/or roles from first available day", nav_button=True
)


@dataclass
class CopyButtonParameters:
    copy_boat: bool
    copy_role: bool
    overwrite: bool


def from_copy_button_type_to_copy_parameters(copy_type: str):
    if copy_type == COPY_BOAT_OVERWRITE:
        copy_boat = True
        copy_role = False
        overwrite = True
    elif copy_type == COPY_BOAT_FILL:
        copy_boat = True
        copy_role = False
        overwrite = False
    elif copy_type == COPY_ROLE_OVERWRITE:
        copy_boat = False
        copy_role = True
        overwrite = True
    elif copy_type == COPY_ROLE_FILL:
        copy_boat = False
        copy_role = True
        overwrite = False

    elif copy_type == COPY_BOTH_OVERWRITE:
        copy_boat = True
        copy_role = True
        overwrite = True
    elif copy_type == COPY_BOTH_FILL:
        copy_boat = True
        copy_role = True
        overwrite = False
    else:
        raise Exception("button type %s not recognised" % copy_type)

    return CopyButtonParameters(
        copy_boat=copy_boat, copy_role=copy_role, overwrite=overwrite
    )


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


def is_copy_individual_volunteer_button(button_value: str):
    return (
        is_copy_overwrite_boat_button(button_value)
        or is_copy_overwrite_role_button(button_value)
        or is_copy_overwrite_both_button(button_value)
        or is_copy_boat_fill_button(button_value)
        or is_copy_role_fill_button(button_value)
        or is_copy_both_fill_button(button_value)
    )


def is_copy_overwrite_boat_button(button_value: str):
    return is_button_of_type(
        value_of_button_pressed=button_value, type_to_check=COPY_BOAT_OVERWRITE
    )


def is_copy_overwrite_role_button(button_value: str):
    return is_button_of_type(
        value_of_button_pressed=button_value, type_to_check=COPY_ROLE_OVERWRITE
    )


def is_copy_overwrite_both_button(button_value: str):
    return is_button_of_type(
        value_of_button_pressed=button_value, type_to_check=COPY_BOTH_OVERWRITE
    )


def is_copy_boat_fill_button(button_value: str):
    return is_button_of_type(
        value_of_button_pressed=button_value, type_to_check=COPY_BOAT_FILL
    )


def is_copy_role_fill_button(button_value: str):
    return is_button_of_type(
        value_of_button_pressed=button_value, type_to_check=COPY_ROLE_FILL
    )


def is_copy_both_fill_button(button_value: str):
    return is_button_of_type(
        value_of_button_pressed=button_value, type_to_check=COPY_BOTH_FILL
    )


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
