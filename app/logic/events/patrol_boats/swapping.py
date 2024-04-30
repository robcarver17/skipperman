from typing import Union, Tuple

from app.backend.forms.swaps import is_ready_to_swap, SwapButtonState, store_swap_state, get_swap_state
from app.backend.volunteers.patrol_boats import get_boat_name_allocated_to_volunteer_on_day_at_event, \
    swap_boats_for_volunteers_in_allocation
from app.backend.volunteers.volunteer_rota import is_possible_to_swap_roles_on_one_day_for_non_grouped_roles_only, \
    swap_roles_for_volunteers_in_allocation, SwapData

from app.logic.events.events_in_state import get_event_from_state

from app.logic.events.patrol_boats.patrol_boat_buttons import get_list_of_generic_buttons_for_each_volunteer_day_combo, \
    generic_button_name_for_volunteer_in_boat_at_event_on_day, get_button_type_day_volunteer_id_given_button_str
from app.data_access.configuration.fixed import BOAT_SHORTHAND, BOAT_AND_ROLE_SHORTHAND, \
    SWAP_SHORTHAND1, SWAP_SHORTHAND2

from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat


def get_list_of_all_swap_buttons_in_boat_allocation(interface: abstractInterface, event: Event)-> list:
    swap_boats =get_list_of_generic_buttons_for_each_volunteer_day_combo(interface=interface, event=event, button_name_function=get_swap_boats_button_name)
    swap_both=get_list_of_generic_buttons_for_each_volunteer_day_combo(interface=interface, event=event, button_name_function=get_swap_both_button_name)
    swap_roles=get_list_of_generic_buttons_for_each_volunteer_day_combo(interface=interface, event=event, button_name_function=get_swap_roles_button_name)

    return swap_boats+swap_both+swap_roles


def get_swap_buttons_for_boat_rota(interface: abstractInterface,
                                   day: Day,
                                   event: Event,
                                   volunteer_id: str,
                                   boat_at_event: PatrolBoat) -> list:

    if is_ready_to_swap(interface):
        return [get_swap_button_when_ready_to_swap(day=day, event=event, volunteer_id=volunteer_id, interface=interface,
                                                   boat_at_event=boat_at_event)]
    else:
        return get_swap_buttons_when_not_ready_to_swap(interface=interface, day=day, volunteer_id=volunteer_id, event=event)


## NOT READY TO SWAP
def get_swap_buttons_when_not_ready_to_swap(interface: abstractInterface,
                                            event: Event,
                                day: Day,
                                volunteer_id: str) -> list:

    okay_to_swap_roles = is_possible_to_swap_roles_on_one_day_for_non_grouped_roles_only(interface=interface, event=event, volunteer_id=volunteer_id, day=day)
    list_of_buttons = [get_swap_boat_button_when_not_ready_to_swap(day=day, volunteer_id=volunteer_id)]
    if okay_to_swap_roles:
        list_of_buttons.append(get_swap_both_button_when_not_ready_to_swap(day=day, volunteer_id=volunteer_id))

    return list_of_buttons


def get_swap_boat_button_when_not_ready_to_swap(
                                day: Day,
                                volunteer_id: str) -> Button:

    return Button(value=get_swap_boats_button_name(day=day, volunteer_id=volunteer_id),
                  label=SWAP_BOATS_BUTTON_LABEL)


def get_swap_both_button_when_not_ready_to_swap(
                                day: Day,
                                volunteer_id: str) -> Button:

    return Button(value=get_swap_both_button_name(day=day, volunteer_id=volunteer_id),
                  label=SWAP_BOTH_BUTTON_LABEL)


#### READY TO SWAP

def get_swap_button_when_ready_to_swap(interface: abstractInterface,
                                       day: Day,
                                       event: Event,
                                       volunteer_id: str,
                                        boat_at_event: PatrolBoat
                                       ) -> Union[Button, str]:

    swapping_both, swap_day, volunteer_id_to_swap = get_type_day_volunteer_id_from_swap_state(interface)
    boat_name_of_swapping_boat = get_boat_name_allocated_to_volunteer_on_day_at_event(interface=interface, event=event, day=day, volunteer_id=volunteer_id_to_swap)

    this_is_the_swapper =swap_day==day and volunteer_id_to_swap==volunteer_id
    swapping_on_this_day = swap_day==day

    if this_is_the_swapper:
        return get_swap_button_when_ready_to_swap_and_this_is_the_swapper(
            day=day,
            volunteer_id=volunteer_id
        )
    elif swapping_on_this_day:
        return get_swap_button_when_ready_to_swap_and_this_is_a_potential_swapper(
            interface=interface,
            swapping_both=swapping_both,
            day=day,
            volunteer_id=volunteer_id,
            event=event,
            boat_at_event=boat_at_event,
            boat_name_of_swapping_boat=boat_name_of_swapping_boat
        )
    else:
        ## Can't swap across dates
        return ""


def get_swap_button_when_ready_to_swap_and_this_is_the_swapper(
                                                                day: Day,
                                                                volunteer_id: str) -> Button:

    button_name = get_swap_boats_button_name(day=day, volunteer_id=volunteer_id) ## button name is irrelevant

    return Button(value=button_name, label=CANCEL_SWAP_BUTTON_LABEL)


def get_swap_button_when_ready_to_swap_and_this_is_a_potential_swapper(interface: abstractInterface,
                                                                       swapping_both:bool,
                                                                day: Day,
                                                                volunteer_id: str,
                                                                       event: Event,
                                                                       boat_at_event: PatrolBoat,
                                                                    boat_name_of_swapping_boat: str) -> Union[Button, str]:

    same_boat_names = boat_name_of_swapping_boat == boat_at_event.name

    valid_to_swap_boats = not same_boat_names
    valid_to_swap_roles = is_possible_to_swap_roles_on_one_day_for_non_grouped_roles_only(interface=interface,
                                                                                          event=event,
                                                                                    day=day,
                                                                                    volunteer_id=volunteer_id)

    if swapping_both:
        if valid_to_swap_boats and valid_to_swap_roles:
            return get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_both(volunteer_id=volunteer_id, day=day)
        elif valid_to_swap_boats and not valid_to_swap_roles:
            return get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_boats_only(volunteer_id=volunteer_id,
                                                                                          day=day)
        elif not valid_to_swap_boats and valid_to_swap_roles:
            return get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_roles_only(volunteer_id=volunteer_id,
                                                                                              day=day)
    else:
        if valid_to_swap_boats:
            return get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_boats_only(volunteer_id=volunteer_id, day=day)

    return ""

def get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_boats_only(
                                                                day: Day,
                                                                volunteer_id: str,
) -> Union[Button, str]:

    button_name = get_swap_boats_button_name(day=day, volunteer_id=volunteer_id)
    return Button(value=button_name, label = SWAP_WITH_BOATS_BUTTON_LABEL)


def get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_both(
                                                                     day: Day,
                                                                     volunteer_id: str) -> Union[Button, str]:

    button_name = get_swap_both_button_name(day=day, volunteer_id=volunteer_id)
    return Button(value=button_name, label=SWAP_WITH_BOTH_BUTTON_LABEL)


def get_swap_button_when_ready_to_swap_and_this_is_a_swapper_of_roles_only(
                                                                     day: Day,
                                                                     volunteer_id: str) -> Union[Button, str]:

    button_name = get_swap_roles_button_name(day=day, volunteer_id=volunteer_id)
    return Button(value=button_name, label=SWAP_ROLE_ONLY_BUTTON_LABEL)


def get_swap_boats_button_name(
                                day: Day,
                                volunteer_id: str) -> str:

    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        SWAP_BOATS, day=day, volunteer_id=volunteer_id
    )


def get_swap_both_button_name(
                                day: Day,
                                volunteer_id: str) -> str:

    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        SWAP_BOTH, day=day, volunteer_id=volunteer_id
    )

def get_swap_roles_button_name(
                                day: Day,
                                volunteer_id: str) -> str:

    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        SWAP_ROLES, day=day, volunteer_id=volunteer_id
    )



def get_and_store_swap_state_from_button_pressed(interface:abstractInterface, swap_button: str):
    swap_type, day, volunteer_id = get_button_type_day_volunteer_id_given_button_str(swap_button)
    swap_state = SwapButtonState(ready_to_swap=True, dict_of_thing_to_swap=dict(day_str=day.name, volunteer_id=volunteer_id, swap_type=swap_type))
    store_swap_state(interface=interface, swap_state=swap_state)


def revert_to_not_swapping_state(interface: abstractInterface):
    swap_state = SwapButtonState(ready_to_swap=False)
    store_swap_state(interface=interface, swap_state=swap_state)


def get_type_day_volunteer_id_from_swap_state(interface: abstractInterface) -> Tuple[bool, Day, str]:
    swap_state = get_swap_state(interface)
    day_str = swap_state.dict_of_thing_to_swap['day_str']
    swap_type = swap_state.dict_of_thing_to_swap['swap_type']
    volunteer_id = swap_state.dict_of_thing_to_swap['volunteer_id']
    if swap_type == SWAP_BOATS:
        swap_both = False
    elif swap_type==SWAP_BOTH:
        swap_both = True
    else:
        raise Exception("Swap type %s not known" % swap_type)

    return swap_both, Day[day_str], volunteer_id



SWAP_BOATS = "SwapBoats"
SWAP_BOTH = "SwapBoth"
SWAP_ROLES = "SwapRoles"

SWAP_BOATS_BUTTON_LABEL = Line([SWAP_SHORTHAND1, SWAP_SHORTHAND2, BOAT_SHORTHAND])
SWAP_BOTH_BUTTON_LABEL = Line([SWAP_SHORTHAND1, SWAP_SHORTHAND2, BOAT_AND_ROLE_SHORTHAND])
CANCEL_SWAP_BUTTON_LABEL = "SWAPPING - click to cancel"
SWAP_WITH_BOATS_BUTTON_LABEL = "Swap boats with me"
SWAP_WITH_BOTH_BUTTON_LABEL = "Swap role&boats with me"
SWAP_ROLE_ONLY_BUTTON_LABEL = "Swap role with me"

def is_swapping_boats_and_or_roles_based_on_button_type(button_type:str) -> Tuple[bool, bool]:
    if button_type == SWAP_BOTH:
        return True, True
    elif button_type == SWAP_BOATS:
        return True, False
    elif button_type == SWAP_ROLES:
        return False, True
    else:
        raise Exception("Button type %s not recognised!" % button_type)


def get_all_swap_buttons_for_boat_allocation(interface: abstractInterface):
    event =get_event_from_state(interface)
    return get_list_of_all_swap_buttons_in_boat_allocation(interface=interface, event=event)


def update_if_swap_button_pressed(interface: abstractInterface, swap_button: str):
    if is_ready_to_swap(interface):
        update_if_swap_button_pressed_and_ready_to_swap(interface=interface, swap_button=swap_button)
    else:
        update_if_swap_button_pressed_and_not_yet_ready_to_swap(interface=interface, swap_button=swap_button)


def update_if_swap_button_pressed_and_not_yet_ready_to_swap(interface: abstractInterface, swap_button: str):
    get_and_store_swap_state_from_button_pressed(interface=interface, swap_button=swap_button)


def update_if_swap_button_pressed_and_ready_to_swap(interface: abstractInterface, swap_button: str):
    swap_data = get_swap_data(interface=interface, swap_button=swap_button)
    ## swap_type and swap_type_in_state should be consistent, going to use swap_type
    do_swapping_for_volunteers_boats_and_possibly_roles_in_boat_allocation(interface=interface, swap_data=swap_data)

    revert_to_not_swapping_state(interface)


def get_swap_data(interface: abstractInterface, swap_button: str) -> SwapData:
    swap_type, day_to_swap_with, volunteer_id_to_swap_with = get_button_type_day_volunteer_id_given_button_str(swap_button)
    __not_used_swapping_both, original_day, original_volunteer_id = get_type_day_volunteer_id_from_swap_state(interface)
    event = get_event_from_state(interface)
    swap_boats, swap_roles = is_swapping_boats_and_or_roles_based_on_button_type(swap_type)

    return SwapData(
        event=event,
        original_day=original_day,
        day_to_swap_with=day_to_swap_with,
        swap_boats=swap_boats,
        swap_roles=swap_roles,
        volunteer_id_to_swap_with=volunteer_id_to_swap_with,
        original_volunteer_id=original_volunteer_id
    )

def do_swapping_for_volunteers_boats_and_possibly_roles_in_boat_allocation(interface: abstractInterface, swap_data: SwapData):

    no_swap_required_cancel_instead = is_no_swap_required_cancel_instead(swap_data)
    if no_swap_required_cancel_instead:
        return

    if swap_data.swap_roles:
        swap_roles_for_volunteers_in_allocation(interface=interface, swap_data=swap_data)
    if swap_data.swap_boats:
        swap_boats_for_volunteers_in_allocation(interface=interface, swap_data=swap_data)

def is_no_swap_required_cancel_instead(swap_data: SwapData):
    s = swap_data
    day_matches = s.original_day == s.day_to_swap_with
    volunteer_matches = s.original_volunteer_id == s.volunteer_id_to_swap_with

    return day_matches and volunteer_matches

