from typing import List

from app.OLD_backend.rota.patrol_boats import (
    DEPRECATE_get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day,
)
from app.backend.patrol_boats.changes import copy_across_earliest_allocation_of_boats_at_event

from app.frontend.shared.events_state import get_event_from_state

from app.OLD_backend.data.patrol_boats import PatrolBoatsData
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.rota.volunteer_rota import (
    is_possible_to_copy_roles_for_non_grouped_roles_only,
)
from app.backend.rota.copying import copy_earliest_valid_role_and_overwrite_for_volunteer, \
    copy_earliest_valid_role_to_all_empty_for_volunteer, \
    volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill
from app.backend.patrol_boats.copying import volunteer_has_at_least_one_allocated_role_which_matches_others
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
    interface: abstractInterface, day: Day, event: Event, volunteer_id: str
) -> List[Button]:
    copy_boat_buttons = get_copy_buttons_for_boat_copy_in_boat_rota(
        interface=interface, volunteer_id=volunteer_id, event=event, day=day
    )
    copy_both_buttons = get_copy_buttons_for_role_and_boat_in_rota(
        interface=interface, volunteer_id=volunteer_id, event=event, day=day
    )
    copy_role_buttons = get_copy_buttons_for_role_in_boat_rota(
        interface=interface, volunteer_id=volunteer_id, event=event, day=day
    )

    return copy_boat_buttons + copy_role_buttons + copy_both_buttons


def get_copy_buttons_for_boat_copy_in_boat_rota(
    interface: abstractInterface, day: Day, event: Event, volunteer_id: str
) -> List[Button]:
    copy_fill_possible = (
        volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
    )
    any_copy_possible = is_possible_to_copy_boat_allocation(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    overwrite_copy_required = (
        not volunteer_has_at_least_one_allocated_boat_which_matches_others(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
    )

    overwrite_copy_button_name = (
        copy_overwrite_button_name_for_boat_copy_in_boat_at_event_on_day(
            day=day,
            volunteer_id=volunteer_id,
        )
    )
    fill_button_name = copy_fill_button_name_for_boat_copy_in_boat_at_event_on_day(
        day=day, volunteer_id=volunteer_id
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
    interface: abstractInterface, day: Day, event: Event, volunteer_id: str
) -> List[Button]:
    any_copy_possible = is_possible_to_copy_roles_for_non_grouped_roles_only(
        interface=interface, event=event, volunteer_id=volunteer_id, day=day
    )
    copy_fill_possible = (
        volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
    )
    overwrite_copy_required = (
        not volunteer_has_at_least_one_allocated_role_which_matches_others(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
    )
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
    interface: abstractInterface, day: Day, event: Event, volunteer_id: str
) -> List[Button]:
    any_copy_possible = is_possible_to_copy_boat_and_role_allocation(
        interface=interface, event=event, volunteer_id=volunteer_id, day=day
    )
    fill_copy_possible = is_possible_to_copy_fill_boat_and_role_allocation(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    overwrite_copy_required = is_required_to_copy_overwrite_boat_and_role_allocation(
        interface=interface, event=event, volunteer_id=volunteer_id
    )

    copy_overwrite_button_name = (
        copy_overwrite_button_name_for_both_volunteer_role_and_boat_at_event_on_day(
            day=day,
            volunteer_id=volunteer_id,
        )
    )
    copy_fill_button_name = (
        copy_fill_button_name_for_both_volunteer_role_and_boat_at_event_on_day(
            day=day, volunteer_id=volunteer_id
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


def is_possible_to_copy_boat_allocation(
    interface: abstractInterface, event: Event, volunteer_id: str
):
    on_same_boat_for_all_days = volunteer_is_on_same_boat_for_all_days(
        interface=interface, volunteer_id=volunteer_id, event=event
    )

    copy_button_required = not on_same_boat_for_all_days

    return copy_button_required


def is_possible_to_copy_boat_and_role_allocation(
    interface: abstractInterface, event: Event, volunteer_id: str, day: Day
):
    boat_possible = is_possible_to_copy_boat_allocation(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    role_possible = is_possible_to_copy_roles_for_non_grouped_roles_only(
        interface=interface, event=event, volunteer_id=volunteer_id, day=day
    )

    return boat_possible and role_possible


def is_possible_to_copy_fill_boat_and_role_allocation(
    interface: abstractInterface, event: Event, volunteer_id: str
):
    boat_possible = volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    role_possible = volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
        interface=interface, event=event, volunteer_id=volunteer_id
    )

    return boat_possible and role_possible


def is_required_to_copy_overwrite_boat_and_role_allocation(
    interface: abstractInterface, event: Event, volunteer_id: str
):
    boat_possible = not volunteer_has_at_least_one_allocated_boat_which_matches_others(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    role_possible = not volunteer_has_at_least_one_allocated_role_which_matches_others(
        interface=interface, event=event, volunteer_id=volunteer_id
    )

    return boat_possible and role_possible


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


def volunteer_is_on_same_boat_for_all_days(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> bool:
    patrol_boat_data = PatrolBoatsData(interface.data)
    return patrol_boat_data.volunteer_is_on_same_boat_for_all_days(
        event=event, volunteer_id=volunteer_id
    )


def volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> bool:
    patrol_boat_data = PatrolBoatsData(interface.data)
    return patrol_boat_data.volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
        event=event, volunteer_id=volunteer_id
    )


def volunteer_has_at_least_one_allocated_boat_which_matches_others(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> bool:
    patrol_boat_data = PatrolBoatsData(interface.data)
    return (
        patrol_boat_data.volunteer_has_at_least_one_allocated_boat_which_matches_others(
            event=event, volunteer_id=volunteer_id
        )
    )


def copy_across_all_boats(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_volunteer_ids = (
        DEPRECATE_get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day(
            interface=interface, event=event
        )
    )
    for volunteer_id in list_of_volunteer_ids:
        copy_across_earliest_allocation_of_boats_at_event(
            interface=interface,
            volunteer_id=volunteer_id,
            event=event,
            allow_overwrite=False,
        )


def copy_over_across_all_boats(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_volunteer_ids = (
        DEPRECATE_get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day(
            interface=interface, event=event
        )
    )
    for volunteer_id in list_of_volunteer_ids:
        copy_across_earliest_allocation_of_boats_at_event(
            interface=interface,
            volunteer_id=volunteer_id,
            event=event,
            allow_overwrite=True,
        )


def copy_across_all_boats_and_roles(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_volunteer_ids = (
        DEPRECATE_get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day(
            interface=interface, event=event
        )
    )
    for volunteer_id in list_of_volunteer_ids:
        copy_across_earliest_allocation_of_boats_at_event(
            interface=interface,
            volunteer_id=volunteer_id,
            event=event,
            allow_overwrite=False,
        )
        copy_earliest_valid_role_to_all_empty_for_volunteer(
            interface=interface, event=event, volunteer_id=volunteer_id
        )


def copy_over_across_all_boats_and_roles(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_volunteer_ids = (
        DEPRECATE_get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day(
            interface=interface, event=event
        )
    )
    for volunteer_id in list_of_volunteer_ids:
        copy_across_earliest_allocation_of_boats_at_event(
            interface=interface,
            volunteer_id=volunteer_id,
            event=event,
            allow_overwrite=True,
        )
        copy_earliest_valid_role_and_overwrite_for_volunteer(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
