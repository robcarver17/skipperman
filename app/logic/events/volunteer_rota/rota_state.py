from typing import Union

from app.backend.volunteers.volunteer_rota_data import RotaSortsAndFilters
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.constants import arg_not_passed, missing_data, NoMoreData
from app.objects.day_selectors import Day
from app.objects.volunteers_in_roles import FILTER_ALL
from app.objects.volunteer_skills import all_skills, default_skills_dict, SkillsDict

SORT_BY_VOLUNTEER_NAME = "Sort_volunteer_name"
SORT_BY_DAY = "Sort_by_day"
SORT_BY_CADET_LOCATION = "Sort_by_cw"

AVAILABILTY_FILTER = "av_filter"
SKILLS_FILTER = "skills_filter"


def get_skills_filter_from_state(interface: abstractInterface) -> SkillsDict:
    skills_dict_with_str = interface.get_persistent_value(
        SKILLS_FILTER, default=None
    ) ### dict of enum okay to store?
    if skills_dict_with_str is None:
        skills_dict = default_skills_dict
    else:
        skills_dict = SkillsDict.from_dict_of_str_and_bool(skills_dict_with_str)

    skills_dict.pad_with_missing_skills()

    return skills_dict


def save_skills_filter_to_state(interface: abstractInterface, dict_of_skills: SkillsDict):
    dict_of_skills_with_str = dict_of_skills.as_dict_of_str_and_bool()
    interface.set_persistent_value(SKILLS_FILTER, dict_of_skills_with_str)


def save_availablity_filter_to_state(
    interface: abstractInterface, availability_filter_dict: dict
):
    interface.set_persistent_value(AVAILABILTY_FILTER, availability_filter_dict)


def save_sorts_to_state(
    interface: abstractInterface,
    sort_by_volunteer_name: str = arg_not_passed,
    sort_by_day: Day = arg_not_passed,
    sort_by_location: bool = False,
):
    if sort_by_volunteer_name is not arg_not_passed:
        interface.set_persistent_value(SORT_BY_VOLUNTEER_NAME, sort_by_volunteer_name)
    else:
        interface.clear_persistent_value(SORT_BY_VOLUNTEER_NAME)

    if sort_by_day is not arg_not_passed:
        interface.set_persistent_value(SORT_BY_DAY, sort_by_day.name)
    else:
        interface.clear_persistent_value(SORT_BY_DAY)

    if sort_by_location:
        interface.set_persistent_value(SORT_BY_CADET_LOCATION, True)
    else:
        interface.clear_persistent_value(SORT_BY_CADET_LOCATION)


def get_sorts_and_filters_from_state(
    interface: abstractInterface,
) -> RotaSortsAndFilters:
    sort_by_volunteer_name = interface.get_persistent_value(
        SORT_BY_VOLUNTEER_NAME, arg_not_passed
    )
    sort_by_day = get_sort_by_day_from_state(interface)
    sort_by_location = interface.get_persistent_value(SORT_BY_CADET_LOCATION, False)
    availability_filter = get_availability_filter_from_state(interface)

    skills_dict = get_skills_filter_from_state(interface)

    return RotaSortsAndFilters(
        skills_filter=skills_dict,
        sort_by_volunteer_name=sort_by_volunteer_name,
        sort_by_day=sort_by_day,
        availability_filter=availability_filter,
        sort_by_location=sort_by_location,
    )


def get_availability_filter_from_state(interface: abstractInterface) -> dict:
    availability_filter = interface.get_persistent_value(
        AVAILABILTY_FILTER, missing_data
    )
    if availability_filter is missing_data:
        return default_availability_filter(interface)
    else:
        return availability_filter


def default_availability_filter(interface: abstractInterface) -> dict:
    event = get_event_from_state(interface=interface)
    return dict([(day.name, FILTER_ALL) for day in event.weekdays_in_event()])


def get_sort_by_day_from_state(interface: abstractInterface) -> Union[str, Day, object]:
    sort_by_day_name_or_location = interface.get_persistent_value(
        SORT_BY_DAY, arg_not_passed
    )
    if sort_by_day_name_or_location is arg_not_passed:
        sort_by_day_or_location = arg_not_passed
    else:
        sort_by_day_or_location = Day[sort_by_day_name_or_location]

    return sort_by_day_or_location


def clear_all_filters(interface: abstractInterface):
    interface.clear_persistent_value(SKILLS_FILTER)
    interface.clear_persistent_value(AVAILABILTY_FILTER)
