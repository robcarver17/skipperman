from copy import copy
from dataclasses import dataclass

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.generic_objects import TRUE, FALSE
from app.objects.utilities.transform_data import dict_as_single_str, from_single_str_to_dict


@dataclass
class SwapButtonState:
    ready_to_swap: bool
    dict_of_thing_to_swap: dict = arg_not_passed

    @classmethod
    def from_string(cls, string_to_parse: str):
        super_dict = from_single_str_to_dict(string_to_parse)
        ready_to_swap_str = super_dict.pop("ready_to_swap")
        ready_to_swap = ready_to_swap_str == TRUE

        return cls(dict_of_thing_to_swap=super_dict, ready_to_swap=ready_to_swap)

    def to_string(self):
        if self.dict_of_thing_to_swap is arg_not_passed:
            super_dict = {}
        else:
            super_dict = copy(self.dict_of_thing_to_swap)

        super_dict["ready_to_swap"] = TRUE if self.ready_to_swap else FALSE
        return dict_as_single_str(super_dict)


SWAP_STATE_KEY = "swap_state"


def is_ready_to_swap(interface: abstractInterface) -> bool:
    swap_state = get_swap_state(interface)
    return swap_state.ready_to_swap


def get_swap_state(interface: abstractInterface) -> SwapButtonState:
    swap_state_str = interface.get_persistent_value(SWAP_STATE_KEY, default=None)
    if swap_state_str is None:
        return SwapButtonState(ready_to_swap=False)
    else:
        swap_state = SwapButtonState.from_string(swap_state_str)

    return swap_state


def store_swap_state(interface: abstractInterface, swap_state: SwapButtonState):
    swap_state_str = swap_state.to_string()
    interface.set_persistent_value(SWAP_STATE_KEY, swap_state_str)
