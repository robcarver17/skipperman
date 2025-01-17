from typing import Tuple, Union

from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id

from app.objects.volunteers import Volunteer

from app.frontend.forms.swaps import (
    is_ready_to_swap,
    SwapButtonState,
    store_swap_state,
    get_swap_state,
)
from app.backend.rota.changes import swap_roles_and_groups_for_volunteers_in_allocation
from app.data_access.configuration.fixed import SWAP_SHORTHAND, SWAP_SHORTHAND2
from app.frontend.shared.events_state import get_event_from_state

from app.frontend.events.volunteer_rota.button_values import (
    generic_button_value_for_volunteer_id_and_day,
    from_known_button_to_volunteer_id_and_day,
    get_list_of_generic_button_values_across_days_and_volunteers,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteer_roles_and_groups_with_id import VolunteerWithIdInRoleAtEvent


def swap_button_value_for_volunteer_id_and_day(volunteer_id: str, day: Day) -> str:
    return generic_button_value_for_volunteer_id_and_day(
        button_type="SWAP", volunteer_id=volunteer_id, day=day
    )


def get_list_of_swap_buttons(interface: abstractInterface, event: Event):
    return get_list_of_generic_button_values_across_days_and_volunteers(
        interface=interface,
        event=event,
        value_function=swap_button_value_for_volunteer_id_and_day,
    )


def get_swap_button(
    volunteer_data_at_event: AllEventDataForVolunteer,
    day: Day,
    interface: abstractInterface,
) -> Button:
    if is_ready_to_swap(interface):
        return swap_button_if_ready_to_swap(
            volunteer_data_at_event=volunteer_data_at_event,
            current_day=day,
            interface=interface,
        )
    else:
        return Button(
            label=Line([SWAP_SHORTHAND, SWAP_SHORTHAND2]),
            value=swap_button_value_for_volunteer_in_role_on_day(
                volunteer=volunteer_data_at_event.volunteer, day=day
            ),
        )


CANCEL_SWAP_BUTTON_LABEL = "SWAPPING - click to cancel"
SWAP_ROLE_ONLY_BUTTON_LABEL = "Swap role with me"


def swap_button_if_ready_to_swap(
    volunteer_data_at_event: AllEventDataForVolunteer,
    current_day: Day,
    interface: abstractInterface,
) -> Union[Button, str]:
    swap_day, swap_volunteer_id = get_day_and_volunteer_id_from_swap_state(interface)
    current_volunteer_id = volunteer_data_at_event.volunteer.id

    day_matches = swap_day == current_day
    volunteer_matches = current_volunteer_id == swap_volunteer_id
    has_role = has_role_on_day(
        volunteer_data_at_event=volunteer_data_at_event, current_day=current_day
    )
    value = swap_button_value_for_volunteer_in_role_on_day(
        volunteer=volunteer_data_at_event.volunteer, day=current_day
    )
    if day_matches and volunteer_matches:
        return Button(label=CANCEL_SWAP_BUTTON_LABEL, value=value)

    if day_matches and has_role and not volunteer_matches:
        return Button(label=SWAP_ROLE_ONLY_BUTTON_LABEL, value=value)
    else:
        ## swap not possibe
        return ""


def has_role_on_day(
    volunteer_data_at_event: AllEventDataForVolunteer,
    current_day: Day,
) -> bool:

    return not volunteer_data_at_event.roles_and_groups.role_and_group_on_day(
        day=current_day
    ).role.is_no_role_set()


def swap_button_value_for_volunteer_in_role_on_day(
    volunteer: Volunteer, day: Day
) -> str:
    return swap_button_value_for_volunteer_id_and_day(
        volunteer_id=volunteer.id,
        day=day,
    )


def revert_to_not_swapping_state(interface: abstractInterface):
    swap_state = SwapButtonState(ready_to_swap=False)
    store_swap_state(interface=interface, swap_state=swap_state)


def get_day_and_volunteer_id_from_swap_state(
    interface: abstractInterface,
) -> Tuple[Day, str]:
    swap_state = get_swap_state(interface)
    day_str = swap_state.dict_of_thing_to_swap["day_str"]
    volunteer_id = swap_state.dict_of_thing_to_swap["volunteer_id"]

    return Day[day_str], volunteer_id


def update_if_swap_button_pressed(interface: abstractInterface, swap_button: str):
    if is_ready_to_swap(interface):
        update_if_swap_button_pressed_and_ready_to_swap(
            interface=interface, swap_button=swap_button
        )
    else:
        update_if_swap_button_pressed_and_not_yet_ready_to_swap(
            interface=interface, swap_button=swap_button
        )


def update_if_swap_button_pressed_and_not_yet_ready_to_swap(
    interface: abstractInterface, swap_button: str
):
    get_and_store_swap_state_from_button_pressed(
        interface=interface, swap_button=swap_button
    )


def get_and_store_swap_state_from_button_pressed(
    interface: abstractInterface, swap_button: str
):
    volunteer_id, day = from_known_button_to_volunteer_id_and_day(swap_button)
    swap_state = SwapButtonState(
        ready_to_swap=True,
        dict_of_thing_to_swap=dict(day_str=day.name, volunteer_id=volunteer_id),
    )
    store_swap_state(interface=interface, swap_state=swap_state)


cancel_swap_button = Button("Cancel swap", nav_button=True)


def update_if_swap_button_pressed_and_ready_to_swap(
    interface: abstractInterface, swap_button: str
):
    if cancel_swap_button.pressed(swap_button):
        ## cancel swap
        pass
    else:
        update_if_swap_button_pressed_and_ready_to_swap_but_not_cancel_button(
            interface=interface, swap_button=swap_button
        )

    revert_to_not_swapping_state(interface)


def update_if_swap_button_pressed_and_ready_to_swap_but_not_cancel_button(
    interface: abstractInterface, swap_button: str
):
    original_volunteer_id, original_day = from_known_button_to_volunteer_id_and_day(
        swap_button
    )
    day_to_swap_with, volunteer_id_to_swap_with = (
        get_day_and_volunteer_id_from_swap_state(interface)
    )
    original_volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=original_volunteer_id
    )
    volunteer_to_swap_with = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=volunteer_id_to_swap_with
    )

    event = get_event_from_state(interface)
    if (
        day_to_swap_with == original_day
        and original_volunteer == volunteer_to_swap_with
    ):
        ## cancel swap
        return
    else:
        swap_roles_and_groups_for_volunteers_in_allocation(
            object_store=interface.object_store,
            original_day=original_day,
            event=event,
            day_to_swap_with=day_to_swap_with,
            volunteer_to_swap_with=volunteer_to_swap_with,
            original_volunteer=original_volunteer,
        )
