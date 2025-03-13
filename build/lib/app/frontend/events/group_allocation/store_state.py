from app.backend.groups.sorting import DEFAULT_SORT_ORDER
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import Day

DAY = "day_in_allocation"


def no_day_set_in_state(interface: abstractInterface) -> bool:
    return get_day_from_state_or_none(interface) is None


def get_day_from_state_or_none(interface: abstractInterface) -> Day:
    day_name = interface.get_persistent_value(DAY, default=None)
    if day_name is None:
        return None
    return Day[day_name]


def set_day_in_state(interface: abstractInterface, day: Day):
    interface.set_persistent_value(DAY, day.name)


def clear_day_in_state(interface: abstractInterface):
    interface.clear_persistent_value(DAY)


SORT_ORDER = "sort_order_for_group_allocation"


def get_current_sort_order(interface: abstractInterface) -> list:

    return interface.get_persistent_value(SORT_ORDER, default=DEFAULT_SORT_ORDER)
