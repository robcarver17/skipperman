from typing import Tuple

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.constants import arg_not_passed
from app.objects.day_selectors import Day

SORT_BY_VOLUNTEER_NAME = "Sort_volunteer_name"
SORT_BY_DAY = "Sort_by_day"


def save_sorts_to_state(interface: abstractInterface,
                        sort_by_volunteer_name: str = arg_not_passed,
                        sort_by_day: Day = arg_not_passed
                        ):
    if sort_by_volunteer_name is not arg_not_passed:
        interface.set_persistent_value(SORT_BY_VOLUNTEER_NAME, sort_by_volunteer_name)
    else:
        interface.clear_persistent_value(SORT_BY_VOLUNTEER_NAME)

    if sort_by_day is not arg_not_passed:
        interface.set_persistent_value(SORT_BY_DAY, sort_by_day.name)
    else:
        interface.clear_persistent_value(SORT_BY_DAY)


def get_sorts_from_state(interface: abstractInterface) -> Tuple[str, Day]:
    sort_by_volunteer_name = interface.get_persistent_value(SORT_BY_VOLUNTEER_NAME, arg_not_passed)
    sort_by_day_name = interface.get_persistent_value(SORT_BY_DAY, arg_not_passed)
    print("SORTY %s isit %s" % (sort_by_day_name, str(sort_by_day_name is arg_not_passed)))
    if sort_by_day_name is arg_not_passed:
        sort_by_day = arg_not_passed
    else:
        sort_by_day = Day[sort_by_day_name]

    return sort_by_volunteer_name, sort_by_day
