from copy import copy

from app.OLD_backend.group_allocations.sorting import DEFAULT_SORT_ORDER, SORT_GROUP
from app.frontend.shared.events_state import get_event_from_state
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.objects_OLD.day_selectors import Day

DAY = "day"


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


SORT_ORDER = "sort_order"


def get_current_sort_order(interface: abstractInterface) -> list:
    event = get_event_from_state(interface)
    default_order = copy(DEFAULT_SORT_ORDER)
    if not event.contains_groups:
        default_order.remove(SORT_GROUP)
    return interface.get_persistent_value(SORT_ORDER, default=DEFAULT_SORT_ORDER)
