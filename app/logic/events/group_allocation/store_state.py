from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import Day

DAY = 'day'


def get_day_from_state_or_none(interface:abstractInterface) -> Day:
    day_name = interface.get_persistent_value(DAY, default=None)
    if day_name is None:
        return  None
    return Day[day_name]

def set_day_in_state(interface: abstractInterface, day: Day):
    interface.set_persistent_value(DAY, day.name)

def clear_day_in_state(interface: abstractInterface):
    interface.clear_persistent_value(DAY)