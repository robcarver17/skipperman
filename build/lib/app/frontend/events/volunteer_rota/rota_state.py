from dataclasses import dataclass
from typing import Union, Dict

from app.backend.rota.sorting_and_filtering import RotaSortsAndFilters, FILTER_ALL, from_str_to_dict_of_filter_options, \
    from_dict_of_filter_options_to_single_str
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import arg_not_passed, missing_data
from app.objects.day_selectors import Day
from app.objects.composed.volunteers_with_skills import SkillsDict
from app.objects.utilities.transform_data import dict_as_str, dict_from_str, str_from_list, list_from_str
from app.objects.volunteer_skills import ListOfSkills

SORT_BY_VOLUNTEER_NAME = "Sort_volunteer_name"
SORT_BY_DAY = "Sort_by_volunteer_day"
SORT_BY_CADET_LOCATION = "Sort_by_volunteer_cw"

AVAILABILTY_FILTER = "av_filter_volunteer"
SKILLS_FILTER = "skills_filter_volunteer"

from app.backend.volunteers.skills import get_list_of_skills


def get_skills_filter_from_state(interface: abstractInterface) -> SkillsDict:
    all_skills = get_list_of_skills(object_store=interface.object_store)

    skill_as_list = interface.get_persistent_value(
        SKILLS_FILTER, default=None
    )  ### dict of enum okay to store?
    if skill_as_list is None:
        skills_dict = SkillsDict()  ##
    else:
        held_skills_as_list_of_id = list_from_str(skill_as_list, type_to_use=str)
        held_skills = ListOfSkills([all_skills.skill_with_id(skill_id) for skill_id in held_skills_as_list_of_id])
        skills_dict = SkillsDict.from_list_of_skills(held_skills)

    skills_dict.pad_with_missing_skills(all_skills=all_skills)

    return skills_dict


def save_skills_filter_to_state(
    interface: abstractInterface, dict_of_skills: SkillsDict
):
    skills_true_only = dict_of_skills.list_of_held_skills()
    list_of_skill_ids = [str(skill.id) for skill in skills_true_only]
    skills_as_list = str_from_list(list_of_skill_ids)

    interface.set_persistent_value(SKILLS_FILTER, skills_as_list)


def save_availablity_filter_to_state(
    interface: abstractInterface, availability_filter_dict: Dict[str,str]
):
    availability_filter_as_str = from_dict_of_filter_options_to_single_str(availability_filter_dict)

    interface.set_persistent_value(AVAILABILTY_FILTER, availability_filter_as_str)


@dataclass
class SortParameters:
    sort_by_volunteer_name: str = arg_not_passed
    sort_by_day: Day = arg_not_passed
    sort_by_location: bool = False


def save_sorts_to_state(interface: abstractInterface, sort_parameters: SortParameters):
    if sort_parameters.sort_by_volunteer_name is not arg_not_passed:
        interface.set_persistent_value(
            SORT_BY_VOLUNTEER_NAME, sort_parameters.sort_by_volunteer_name
        )
    else:
        interface.clear_persistent_value(SORT_BY_VOLUNTEER_NAME)

    if sort_parameters.sort_by_day is not arg_not_passed:
        interface.set_persistent_value(SORT_BY_DAY, sort_parameters.sort_by_day.name)
    else:
        interface.clear_persistent_value(SORT_BY_DAY)

    if sort_parameters.sort_by_location:
        interface.set_persistent_value(SORT_BY_CADET_LOCATION, True)
    else:
        interface.clear_persistent_value(SORT_BY_CADET_LOCATION)

def clear_all_sorts(interface: abstractInterface):
    interface.clear_persistent_value(SORT_BY_CADET_LOCATION)
    interface.clear_persistent_value(SORT_BY_DAY)
    interface.clear_persistent_value(SORT_BY_VOLUNTEER_NAME)

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


def get_availability_filter_from_state(interface: abstractInterface) -> Dict[str, str]:
    availability_filter_as_str = interface.get_persistent_value(
        AVAILABILTY_FILTER, missing_data
    )
    if availability_filter_as_str is missing_data:
        return default_availability_filter(interface)

    availability_filter= from_str_to_dict_of_filter_options(availability_filter_as_str)

    return availability_filter



def default_availability_filter(interface: abstractInterface) -> Dict[str,str]:
    event = get_event_from_state(interface=interface)
    return dict([(day.name, FILTER_ALL) for day in event.days_in_event()])


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
