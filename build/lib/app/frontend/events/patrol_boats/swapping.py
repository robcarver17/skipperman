from typing import Union, Tuple

from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id
from app.frontend.shared.buttons import get_type_of_button_pressed, is_button_of_type

from app.objects.volunteers import Volunteer

from app.frontend.forms.swaps import (
    is_ready_to_swap,
    SwapButtonState,
    store_swap_state,
    get_swap_state,
)
from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    get_boat_allocated_to_volunteer_on_day_at_event,
)


from app.backend.patrol_boats.swapping import (
    is_possible_to_swap_roles_on_one_day,
    swap_boats_for_volunteers_in_allocation_using_swapdata,
    swap_roles_for_volunteers_in_allocation_using_swapdata,
    SwapData, move_volunteer_into_empty_boat_using_swapdata,
    do_swapping_for_volunteers_boats_and_possibly_roles_in_boat_allocation,
)

from app.frontend.shared.events_state import get_event_from_state

from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    generic_button_name_for_volunteer_in_boat_at_event_on_day,
    get_day_and_volunteer_given_button_of_type, get_day_and_patrol_boat_given_button_of_type,
)
from app.data_access.configuration.fixed import (
    BOAT_SHORTHAND,
    BOAT_AND_ROLE_SHORTHAND,
    SWAP_SHORTHAND,
    SWAP_SHORTHAND2,
)

from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import (
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
)
from app.objects.day_selectors import Day
from app.objects.patrol_boats import PatrolBoat




def get_swap_buttons_for_boat_rota(
    interface: abstractInterface,
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> list:
    if is_ready_to_swap(interface):
        return [
            get_swap_button_when_ready_to_swap(
                interface=interface,
                volunteer_at_event_on_boat=volunteer_at_event_on_boat,
            )
        ]
    else:
        return get_swap_buttons_when_not_ready_to_swap(volunteer_at_event_on_boat)


## NOT READY TO SWAP
def get_swap_buttons_when_not_ready_to_swap(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> list:
    okay_to_swap_roles = is_possible_to_swap_roles_on_one_day(
        volunteer_at_event_on_boat
    )
    day = volunteer_at_event_on_boat.day
    volunteer_id = volunteer_at_event_on_boat.volunteer.id
    list_of_buttons = [
        get_swap_boat_button_when_not_ready_to_swap(day=day, volunteer_id=volunteer_id)
    ]
    if okay_to_swap_roles:
        list_of_buttons.append(
            get_swap_both_button_when_not_ready_to_swap(
                day=day, volunteer_id=volunteer_id
            )
        )

    return list_of_buttons


def get_swap_boat_button_when_not_ready_to_swap(day: Day, volunteer_id: str) -> Button:
    return Button(
        value=get_swap_boats_button_name(day=day, volunteer_id=volunteer_id),
        label=SWAP_BOATS_BUTTON_LABEL,
    )


def get_swap_both_button_when_not_ready_to_swap(day: Day, volunteer_id: str) -> Button:
    return Button(
        value=get_swap_both_button_name(day=day, volunteer_id=volunteer_id),
        label=SWAP_BOTH_BUTTON_LABEL,
    )


#### READY TO SWAP


def get_swap_button_when_ready_to_swap(
    interface: abstractInterface,
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> Union[Button, str]:
    (
        swapping_both,
        swap_day,
        volunteer_to_swap,
    ) = get_type_day_volunteer_from_swap_state(interface)

    day = volunteer_at_event_on_boat.day
    event = volunteer_at_event_on_boat.event
    volunteer = volunteer_at_event_on_boat.volunteer
    volunteer_id = volunteer.id

    this_is_the_swapper = swap_day == day and volunteer_to_swap == volunteer
    swapping_on_this_day = swap_day == day

    if this_is_the_swapper:
        return get_swap_button_when_ready_to_swap_and_this_is_the_swapper(
            day=day, volunteer_id=volunteer_id
        )
    elif swapping_on_this_day:
        swapping_boat = get_boat_allocated_to_volunteer_on_day_at_event(
            object_store=interface.object_store,
            event=event,
            day=day,
            volunteer=volunteer_to_swap,
        )

        return get_swap_button_when_ready_to_swap_and_this_is_a_potential_swapper(
            swapping_both=swapping_both,
            volunteer_at_event_on_boat=volunteer_at_event_on_boat,
            swapping_boat=swapping_boat,
        )
    else:
        ## Can't swap across dates
        return ""


def get_swap_button_to_move_to_boat_without_swapping(
    interface: abstractInterface,
    patrol_boat: PatrolBoat,
        day: Day
) -> Union[Button, str]:
    (
        swapping_both,
        swap_day,
        volunteer_to_swap,
    ) = get_type_day_volunteer_from_swap_state(interface)

    swapping_on_this_day = swap_day == day

    if swapping_on_this_day:
        return get_swap_button_when_swapping_into_empty_boat(
            patrol_boat=patrol_boat, day=day,
            volunteer_to_swap=volunteer_to_swap
        )
    else:
        ## Can't swap across dates
        return ""

def get_swap_button_when_swapping_into_empty_boat(patrol_boat: PatrolBoat, day: Day, volunteer_to_swap: Volunteer):
    button_name = get_swap_into_empty_button_name(day=day, patrol_boat=patrol_boat)

    return Button(value=button_name, label="Move %s on to this boat" % volunteer_to_swap.name)


def get_swap_button_when_ready_to_swap_and_this_is_the_swapper(
    day: Day, volunteer_id: str
) -> Button:
    button_name = get_swap_cancel_button_name(
        day=day, volunteer_id=volunteer_id
    )

    return Button(value=button_name, label=CANCEL_SWAP_BUTTON_LABEL)


def get_swap_button_when_ready_to_swap_and_this_is_a_potential_swapper(
    swapping_both: bool,
    swapping_boat: PatrolBoat,
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> Union[Button, str]:

    if swapping_both:
        return (
            get_swap_button_when_ready_to_swap_and_this_is_a_potential_swapper_of_both(
                swapping_boat=swapping_boat,
                volunteer_at_event_on_boat=volunteer_at_event_on_boat,
            )
        )
    else:
        return get_swap_button_when_ready_to_swap_and_this_is_a_potential_swapper_of_boats_only(
            swapping_boat=swapping_boat,
            volunteer_at_event_on_boat=volunteer_at_event_on_boat,
        )


def get_swap_button_when_ready_to_swap_and_this_is_a_potential_swapper_of_both(
    swapping_boat: PatrolBoat,
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> Union[Button, str]:
    boat_at_event = volunteer_at_event_on_boat.patrol_boat
    same_boat = boat_at_event == swapping_boat

    valid_to_swap_boats = not same_boat
    valid_to_swap_roles = is_possible_to_swap_roles_on_one_day(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )

    volunteer_id = volunteer_at_event_on_boat.volunteer.id
    day = volunteer_at_event_on_boat.day

    if valid_to_swap_boats and valid_to_swap_roles:
        return get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_both(
            volunteer_id=volunteer_id, day=day
        )
    elif valid_to_swap_boats and not valid_to_swap_roles:
        return get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_boats_only(
            volunteer_id=volunteer_id, day=day
        )
    elif not valid_to_swap_boats and valid_to_swap_roles:
        return get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_roles_only(
            volunteer_id=volunteer_id, day=day
        )
    else:
        return ""


def get_swap_button_when_ready_to_swap_and_this_is_a_potential_swapper_of_boats_only(
    swapping_boat: PatrolBoat,
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> Union[Button, str]:
    boat_at_event = volunteer_at_event_on_boat.patrol_boat
    same_boat = boat_at_event == swapping_boat

    valid_to_swap_boats = not same_boat
    if valid_to_swap_boats:
        volunteer_id = volunteer_at_event_on_boat.volunteer.id
        day = volunteer_at_event_on_boat.day
        return get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_boats_only(
            volunteer_id=volunteer_id, day=day
        )
    else:
        return ""


def get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_boats_only(
    day: Day,
    volunteer_id: str,
) -> Union[Button, str]:
    button_name = get_swap_boats_button_name(day=day, volunteer_id=volunteer_id)
    return Button(value=button_name, label=SWAP_WITH_BOATS_BUTTON_LABEL)


def get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_both(
    day: Day, volunteer_id: str
) -> Union[Button, str]:
    button_name = get_swap_both_button_name(day=day, volunteer_id=volunteer_id)
    return Button(value=button_name, label=SWAP_WITH_BOTH_BUTTON_LABEL)


def get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_roles_only(
    day: Day, volunteer_id: str
) -> Union[Button, str]:
    button_name = get_swap_roles_button_name(day=day, volunteer_id=volunteer_id)
    return Button(value=button_name, label=SWAP_ROLE_ONLY_BUTTON_LABEL)


def get_swap_boats_button_name(day: Day, volunteer_id: str) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        SWAP_BOATS, day=day, volunteer_id=volunteer_id
    )

def get_swap_into_empty_button_name(day: Day, patrol_boat: PatrolBoat):
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        MOVE_INTO_EMPTY, day=day, volunteer_id=patrol_boat.id
    )

def get_swap_both_button_name(day: Day, volunteer_id: str) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        SWAP_BOTH, day=day, volunteer_id=volunteer_id
    )


def get_swap_roles_button_name(day: Day, volunteer_id: str) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        SWAP_ROLES, day=day, volunteer_id=volunteer_id
    )

def get_swap_cancel_button_name(day: Day, volunteer_id: str) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        CANCEL_SWAP, day=day, volunteer_id=volunteer_id
    )


def get_and_store_swap_state_from_button_pressed(
    interface: abstractInterface, swap_button: str
):
    swap_type = get_type_of_button_pressed(swap_button)
    day, volunteer = get_day_and_volunteer_given_button_of_type(
        interface=interface, button_name=swap_button,
        button_type=swap_type
    )
    swap_state = SwapButtonState(
        ready_to_swap=True,
        dict_of_thing_to_swap=dict(
            day_str=day.name, volunteer_id=volunteer.id, swap_type=swap_type
        ),
    )
    store_swap_state(interface=interface, swap_state=swap_state)


def revert_to_not_swapping_state(interface: abstractInterface):
    swap_state = SwapButtonState(ready_to_swap=False)
    store_swap_state(interface=interface, swap_state=swap_state)


def get_type_day_volunteer_from_swap_state(
    interface: abstractInterface,
) -> Tuple[bool, Day, Volunteer]:
    swap_state = get_swap_state(interface)
    day_str = swap_state.dict_of_thing_to_swap["day_str"]
    swap_type = swap_state.dict_of_thing_to_swap["swap_type"]
    volunteer_id = swap_state.dict_of_thing_to_swap["volunteer_id"]
    if swap_type == SWAP_BOATS:
        swap_both = False
    elif swap_type == SWAP_BOTH:
        swap_both = True
    else:
        raise Exception("Swap type %s not known" % swap_type)

    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=volunteer_id
    )
    day = Day[day_str]

    return swap_both, day, volunteer


MOVE_INTO_EMPTY = "SwapMoveIntoEmpty"
SWAP_BOATS = "SwapBoats"
SWAP_BOTH = "SwapBoth"
SWAP_ROLES = "SwapRoles"
CANCEL_SWAP = "SwapCancel"

SWAP_BOATS_BUTTON_LABEL = Line([SWAP_SHORTHAND, SWAP_SHORTHAND2, BOAT_SHORTHAND])
SWAP_BOTH_BUTTON_LABEL = Line(
    [SWAP_SHORTHAND, SWAP_SHORTHAND2, BOAT_AND_ROLE_SHORTHAND]
)
CANCEL_SWAP_BUTTON_LABEL = "SWAPPING - click to cancel"
SWAP_WITH_BOATS_BUTTON_LABEL = "Swap boats with me"
SWAP_WITH_BOTH_BUTTON_LABEL = "Swap role&boats with me"
SWAP_ROLE_ONLY_BUTTON_LABEL = "Swap role with me"

def is_swap_button(button_value):
    return is_swap_cancel_button(button_value) or\
    is_swap_both_button(button_value) or \
    is_swap_boats_button(button_value) or \
    is_swap_roles_button(button_value) or \
    is_swap_into_empty_button(button_value)

def is_swap_cancel_button(button_value:str):
    return is_button_of_type(type_to_check=CANCEL_SWAP, value_of_button_pressed=button_value)

def is_swap_into_empty_button(button_value:str):
    return is_button_of_type(type_to_check=MOVE_INTO_EMPTY, value_of_button_pressed=button_value)


def is_swap_boats_button(button_value:str):
    return is_button_of_type(type_to_check=SWAP_BOATS, value_of_button_pressed=button_value)

def is_swap_roles_button(button_value:str):
    return is_button_of_type(type_to_check=SWAP_ROLES, value_of_button_pressed=button_value)

def is_swap_both_button(button_value:str):
    return is_button_of_type(type_to_check=SWAP_BOTH, value_of_button_pressed=button_value)



def is_swapping_boats_and_or_roles_based_on_button_type(
    button_type: str,
) -> Tuple[bool, bool]:
    if button_type == SWAP_BOTH:
        return True, True
    elif button_type == SWAP_BOATS:
        return True, False
    elif button_type == SWAP_ROLES:
        return False, True
    elif button_type == CANCEL_SWAP:
        return False, False
    elif button_type == MOVE_INTO_EMPTY:
        return True, False
    else:
        raise Exception("Button type %s not recognised!" % button_type)



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


def update_if_swap_button_pressed_and_ready_to_swap(
    interface: abstractInterface, swap_button: str
):
    swap_data = get_swap_data(interface=interface, swap_button=swap_button)
    ## swap_type and swap_type_in_state should be consistent, going to use swap_type
    do_swapping_for_volunteers_boats_and_possibly_roles_in_boat_allocation(
        object_store=interface.object_store, swap_data=swap_data
    )

    revert_to_not_swapping_state(interface)


def get_swap_data(interface: abstractInterface, swap_button: str) -> SwapData:
    swap_type = get_type_of_button_pressed(swap_button)
    if swap_type == MOVE_INTO_EMPTY:
        return get_swap_data_for_move_into_empty_boat(interface, swap_button)
    else:
        return get_swap_data_for_normal_swap_with_two_volunters(interface, swap_button)

def get_swap_data_for_normal_swap_with_two_volunters(interface: abstractInterface, swap_button: str) -> SwapData:
    swap_type = get_type_of_button_pressed(swap_button)
    day_to_swap_with,        volunteer_to_swap_with, = get_day_and_volunteer_given_button_of_type(
        button_name=swap_button, interface=interface, button_type=swap_type)

    (
        __,
        original_day,
        original_volunteer,
    ) = get_type_day_volunteer_from_swap_state(interface)

    event = get_event_from_state(interface)
    swap_boats, swap_roles = is_swapping_boats_and_or_roles_based_on_button_type(
        swap_type
    )

    return SwapData(
        event=event,
        original_day=original_day,
        day_to_swap_with=day_to_swap_with,
        swap_boats=swap_boats,
        swap_roles=swap_roles,
        original_volunteer=original_volunteer,
        volunteer_to_swap_with=volunteer_to_swap_with,
    )


def get_swap_data_for_move_into_empty_boat(interface: abstractInterface, swap_button: str) -> SwapData:
    day_to_swap_with,  patrol_boat_to_swap_into = get_day_and_patrol_boat_given_button_of_type(
        button_name=swap_button, interface=interface, button_type=MOVE_INTO_EMPTY)

    (
        __,
        original_day,
        original_volunteer,
    ) = get_type_day_volunteer_from_swap_state(interface)

    event = get_event_from_state(interface)

    return SwapData(
        event=event,
        original_day=original_day,
        day_to_swap_with=day_to_swap_with,
        swap_boats=False,
        swap_roles=False,
        swapping_into_empty_boat=True,
        original_volunteer=original_volunteer,
        empty_boat_to_swap_into=patrol_boat_to_swap_into
    )


