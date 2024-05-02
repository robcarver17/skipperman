from typing import List

from app.backend.data.security import SUPERUSER
from app.backend.data.volunteer_rota import VolunteerRotaData
from app.backend.events import get_sorted_list_of_events
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event, ListOfEvents
from app.objects.groups import Group
from app.backend.data.group_allocations import GroupAllocationsData

def get_list_of_groups_volunteer_id_can_see(interface: abstractInterface, event: Event, volunteer_id: str) -> List[Group]:
    volunteer_rota_data = VolunteerRotaData(interface.data)
    is_senior_instructor_at_event = volunteer_rota_data.is_senior_instructor(event=event, volunteer_id=volunteer_id)

    if volunteer_id == SUPERUSER or is_senior_instructor_at_event:
        return get_list_of_all_groups_at_event(interface=interface, event=event)
    else:
        return volunteer_rota_data.get_list_of_groups_volunteer_is_instructor_for(event=event, volunteer_id=volunteer_id)


def get_list_of_all_groups_at_event(interface: abstractInterface, event: Event) -> List[Group]:
    group_allocations_data = GroupAllocationsData(interface.data)
    return group_allocations_data.get_list_of_groups_at_event(event=event)

def get_list_of_events_entitled_to_see(interface: abstractInterface, volunteer_id: str, sort_by: str):
    all_events = get_sorted_list_of_events(interface, sort_by=sort_by)
    all_events = ListOfEvents([event for event in all_events if can_volunteer_id_see_event(interface=interface,
                                                                                           event=event,
                                                                                           volunteer_id=volunteer_id)])

    return all_events


def can_volunteer_id_see_event(interface: abstractInterface, event: Event, volunteer_id: str):
    if volunteer_id==SUPERUSER:
        return True

    list_of_groups = get_list_of_groups_volunteer_id_can_see(interface=interface, event=event, volunteer_id=volunteer_id)

    return len(list_of_groups)>0
