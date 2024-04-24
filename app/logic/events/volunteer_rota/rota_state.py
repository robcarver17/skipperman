from app.backend.data.cadets_at_event import DEPRECATED_load_cadets_at_event
from app.backend.volunteers.volunteer_rota_data import RotaSortsAndFilters
from app.data_access.configuration.configuration import VOLUNTEER_SKILLS
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.constants import arg_not_passed, missing_data, NoMoreData
from app.objects.day_selectors import Day

SORT_BY_VOLUNTEER_NAME = "Sort_volunteer_name"
SORT_BY_DAY = "Sort_by_day"



SKILLS_FILTER = "skills_filter"
def get_skills_filter_from_state(interface: abstractInterface):
    skills_dict = get_skills_filter_dict_or_default_from_state(interface)

    return skills_dict

def get_skills_filter_dict_or_default_from_state(interface: abstractInterface) -> dict:
    skills_dict = interface.get_persistent_value(SKILLS_FILTER, default=default_skills_dict)
    skills_dict = ensure_filter_has_all_skills(skills_dict)

    return skills_dict

default_skills_dict = dict([(skill, False) for skill in VOLUNTEER_SKILLS])

def ensure_filter_has_all_skills(skills_dict: dict) -> dict:
    for skill in VOLUNTEER_SKILLS:
        if not skill in skills_dict.keys():
            skills_dict[skill] = False
    return skills_dict

def save_skills_filter_to_state(interface: abstractInterface, dict_of_skills: bool):
    interface.set_persistent_value(SKILLS_FILTER, dict_of_skills)

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


def get_sorts_and_filters_from_state(interface: abstractInterface) -> RotaSortsAndFilters:
    sort_by_volunteer_name = interface.get_persistent_value(SORT_BY_VOLUNTEER_NAME, arg_not_passed)
    sort_by_day_name = interface.get_persistent_value(SORT_BY_DAY, arg_not_passed)
    print("SORTY %s isit %s" % (sort_by_day_name, str(sort_by_day_name is arg_not_passed)))
    if sort_by_day_name is arg_not_passed:
        sort_by_day = arg_not_passed
    else:
        sort_by_day = Day[sort_by_day_name]
    skills_dict = get_skills_filter_from_state(interface)

    return RotaSortsAndFilters(skills_filter=skills_dict, sort_by_volunteer_name=sort_by_volunteer_name, sort_by_day=sort_by_day)


### State of cadet
CADET_ID_IN_ROTA_AT_EVENT = "cadet_id_rota_at_event"


def get_and_save_next_cadet_id_in_event_data(interface: abstractInterface) -> str:
    current_id = get_current_cadet_id_for_rota_at_event(interface)
    if current_id is missing_data:
        new_id = get_first_cadet_id_for_rota_in_event_data(interface)
    else:
        new_id = get_next_cadet_id_for_rota_in_event_data(
            interface=interface, current_id=current_id
        )
    save_cadet_id_for_rota_at_event(interface=interface, cadet_id=new_id)

    return new_id


def get_first_cadet_id_for_rota_in_event_data(interface: abstractInterface) -> str:
    list_of_ids = list_of_cadet_ids_at_event_including_cancelled_and_deleted(interface)
    id = list_of_ids[0]

    print("Getting first ID %s from list %s " % (id, list_of_ids))

    return id


def get_next_cadet_id_for_rota_in_event_data(
    interface: abstractInterface, current_id: str
) -> str:
    list_of_ids = list_of_cadet_ids_at_event_including_cancelled_and_deleted(interface)
    current_index = list_of_ids.index(current_id)
    new_index = current_index+1

    try:
        new_id = list_of_ids[new_index]
    except:
        raise NoMoreData

    return new_id


def list_of_cadet_ids_at_event_including_cancelled_and_deleted(interface:abstractInterface) -> list:
    event = get_event_from_state(interface)

    cadets_at_event = DEPRECATED_load_cadets_at_event(event)

    cadet_ids = cadets_at_event.list_of_cadet_ids()

    return cadet_ids


def get_current_cadet_id_for_rota_at_event(interface: abstractInterface) -> str:
    cadet_id = interface.get_persistent_value(CADET_ID_IN_ROTA_AT_EVENT, default=missing_data)

    return cadet_id

def save_cadet_id_for_rota_at_event(interface: abstractInterface, cadet_id: str):
    interface.set_persistent_value(CADET_ID_IN_ROTA_AT_EVENT, cadet_id)

def clear_cadet_id_for_rota_at_event(interface: abstractInterface):
    interface.clear_persistent_value(CADET_ID_IN_ROTA_AT_EVENT)
