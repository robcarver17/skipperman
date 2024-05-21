from dataclasses import dataclass
from typing import List

from app.backend.data.group_allocations import GroupAllocationsData
from app.backend.data.volunteer_allocation import VolunteerAllocationData

from app.backend.volunteers.volunteers import get_volunteer_name_from_id
from app.data_access.data import DEPRECATED_data

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.volunteer_rota import VolunteerRotaData, \
    get_volunteer_roles
from app.backend.data.patrol_boats import PatrolBoatsData
from app.data_access.configuration.configuration import VOLUNTEER_ROLES

from app.backend.data.volunteers import DEPRECATED_get_sorted_list_of_volunteers
from app.objects.constants import missing_data
from app.objects.events import Event
from app.objects.groups import Group, ALL_GROUPS_NAMES, GROUP_UNALLOCATED_TEXT, LAKE_TRAINING
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfVolunteersAtEvent, ListOfIdentifiedVolunteersAtEvent
from app.objects.volunteers_in_roles import NO_ROLE_SET, VolunteerInRoleAtEvent, ListOfVolunteersInRoleAtEvent

from app.objects.day_selectors import Day


@dataclass
class SwapData:
    event: Event
    original_day: Day
    day_to_swap_with: Day
    swap_boats: bool
    swap_roles: bool
    volunteer_id_to_swap_with: str
    original_volunteer_id: str

def update_role_at_event_for_volunteer_on_day_at_event(interface: abstractInterface,
                                                       event: Event,
                                                       day: Day,
                                                       volunteer_id: str,
                                                       new_role: str):

    volunteer_in_role_at_event_on_day =  VolunteerInRoleAtEvent(day=day, volunteer_id=volunteer_id)
    update_role_at_event_for_volunteer_on_day(interface=interface, event=event, volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
                                              new_role=new_role)


def get_volunteer_role_at_event_on_day(interface: abstractInterface, event: Event, volunteer_id: str, day: Day) -> str:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteer_role_at_event_on_day(event=event, volunteer_id=volunteer_id, day=day)

def get_volunteer_with_role_at_event_on_day(interface: abstractInterface, event: Event, volunteer_id: str, day: Day) -> VolunteerInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteer_with_role_at_event_on_day(event=event, volunteer_id=volunteer_id, day=day)





def sort_volunteer_data_for_event_by_name_sort_order(volunteers_at_event: ListOfVolunteersAtEvent, sort_order) -> ListOfVolunteersAtEvent:
    list_of_volunteers = DEPRECATED_get_sorted_list_of_volunteers(sort_by=sort_order)
    ## this works because if an ID is missing we just ignore it
    return volunteers_at_event.sort_by_list_of_volunteer_ids(list_of_volunteers.list_of_ids)


def dict_of_groups_for_dropdown(interface: abstractInterface): ## Future proof to when groups come from files
    dict_of_groups = {group:group for group in ALL_GROUPS_NAMES}
    dict_of_groups[GROUP_UNALLOCATED_TEXT]= GROUP_UNALLOCATED_TEXT

    return dict_of_groups

MAKE_UNAVAILABLE = "* UNAVAILABLE *"
def dict_of_roles_for_dropdown(interface: abstractInterface):
    volunteer_roles = get_volunteer_roles(interface)
    dict_of_roles = {role:role for role in volunteer_roles}
    dict_of_roles[NO_ROLE_SET] = NO_ROLE_SET
    dict_of_roles[MAKE_UNAVAILABLE] = MAKE_UNAVAILABLE

    return dict_of_roles


def boat_related_role_str_on_day_for_volunteer_id(interface: abstractInterface, day: Day, event: Event, volunteer_id: str)-> str:
    volunteer_rota = VolunteerRotaData(interface.data)
    volunteer_on_day = volunteer_rota.get_volunteer_with_role_at_event_on_day(event=event, day=day, volunteer_id=volunteer_id)
    if volunteer_on_day is missing_data:
        return ""
    elif volunteer_on_day.requires_boat:
        return volunteer_on_day.role
    else:
        return ""


def is_possible_to_copy_roles_for_non_grouped_roles_only(interface: abstractInterface, event: Event, volunteer_id:str) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    all_volunteer_positions = get_list_of_volunteer_with_role_across_days_for_volunteer_at_event(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id
    )

    all_roles = [volunteer_with_role.role for volunteer_with_role in all_volunteer_positions]

    no_roles_to_copy = len(all_roles)==0
    all_roles_match = len(set(all_roles))<=1

    roles_require_groups = [volunteer_with_role.requires_group for volunteer_with_role in all_volunteer_positions]
    at_least_one_role_require_group = any(roles_require_groups)

    ## copy not possible if all roles the same, or at least one requires a group, or nothing to copy
    if all_roles_match or at_least_one_role_require_group or no_roles_to_copy:
        return False
    else:
        return True


def get_list_of_volunteer_with_role_across_days_for_volunteer_at_event(interface: abstractInterface, event: Event, volunteer_id:str) ->\
    List[VolunteerInRoleAtEvent]:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteers_with_roles_in_event_including_missing_data = [get_volunteer_with_role_at_event_on_day(interface=interface,
                                                                                                     volunteer_id=volunteer_id,
                                                                                                    day=day, event=event)
                                                             for day in event.weekdays_in_event()]

    all_volunteer_positions = [volunteer_with_role for volunteer_with_role in volunteers_with_roles_in_event_including_missing_data
                               if volunteer_with_role is not missing_data]

    return all_volunteer_positions

def is_possible_to_swap_roles_on_one_day_for_non_grouped_roles_only(interface: abstractInterface,
                                                                    event: Event,
                                                                    volunteer_id:str,
                                                                    day: Day) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    volunteer_with_role = get_volunteer_with_role_at_event_on_day(interface=interface,
                                                                  volunteer_id=volunteer_id,
                                                                            day=day, event=event)
    role_requires_group = volunteer_with_role.requires_group
    possible_to_swap = not role_requires_group

    return possible_to_swap




def swap_roles_for_volunteers_in_allocation(interface: abstractInterface,
                                            swap_data: SwapData):

    volunteer_rota_data = VolunteerRotaData(interface.data)
    try:
        volunteer_rota_data.swap_roles_for_volunteers_in_allocation(
            event=swap_data.event,
            original_volunteer_id=swap_data.original_volunteer_id,
            volunteer_id_to_swap_with=swap_data.volunteer_id_to_swap_with,
            day_to_swap_with=swap_data.day_to_swap_with,
            original_day=swap_data.original_day
        )
    except Exception as e:
        first_name = get_volunteer_name_from_id(interface=interface, volunteer_id=swap_data.original_volunteer_id)
        second_name = get_volunteer_name_from_id(interface=interface, volunteer_id=swap_data.volunteer_id_to_swap_with)
        interface.log_error("Swap roles of %s and %s failed on day %s, error %s" % (first_name, second_name, swap_data.day_to_swap_with.name, str(e)))

def swap_and_groups_for_volunteers_in_allocation(interface:abstractInterface,
                                                                            event: Event,
                                                                           original_day: Day,
                                                                           original_volunteer_id: str,
                                                                           day_to_swap_with: Day,
                                                                           volunteer_id_to_swap_with: str):
    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.swap_and_groups_for_volunteers_in_allocation(event=event,
                                                                     original_day=original_day,
                                                                     day_to_swap_with=day_to_swap_with,
                                                                     original_volunteer_id=original_volunteer_id,
                                                                     volunteer_id_to_swap_with=volunteer_id_to_swap_with)


def volunteer_is_on_lake(interface: abstractInterface, event: Event, volunteer_id: str) -> bool:
    volunteer_rota_data = VolunteerRotaData(interface.data)
    return volunteer_rota_data.volunteer_is_on_lake(event=event, volunteer_id=volunteer_id)



def list_of_cadet_groups_associated_with_volunteer(interface: abstractInterface, event: Event, volunteer_at_event: VolunteerAtEvent) -> List[Group]:
    group_data = GroupAllocationsData(interface.data)
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    list_of_groups = []
    for cadet_id in list_of_cadet_ids:
        list_of_groups_this_cadet = [group_data.get_list_of_cadet_ids_with_groups_at_event(event).group_for_cadet_id_on_day(cadet_id,day ) for day in event.weekdays_in_event()]
        list_of_groups+=list_of_groups_this_cadet

    list_of_groups = list(set(list_of_groups))
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

    return list_of_groups


def lake_in_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.type_of_group() for group in list_of_groups]
    return LAKE_TRAINING in types_of_groups

def groups_for_volunteer(interface: abstractInterface, event: Event, volunteer_id: str) -> List[Group]:
    list_of_groups = [ get_volunteer_with_role_at_event_on_day(interface=interface,
                                                                  volunteer_id=volunteer_id,
                                                                            day=day, event=event).group
                      for day in event.weekdays_in_event()]
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

    return list(set(list_of_groups))


def DEPRECATED_load_list_of_identified_volunteers_at_event(event: Event) -> ListOfIdentifiedVolunteersAtEvent:
    return DEPRECATED_data.data_list_of_identified_volunteers_at_event.read(event_id=event.id)


def load_list_of_identified_volunteers_at_event(interface: abstractInterface, event: Event) -> ListOfIdentifiedVolunteersAtEvent:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return volunteer_allocation_data.load_list_of_identified_volunteers_at_event(event)


def DEPRECATED_load_list_of_volunteers_at_event(event: Event)-> ListOfVolunteersAtEvent:
    return DEPRECATED_data.data_list_of_volunteers_at_event.read(event_id=event.id)


def load_list_of_volunteers_at_event(interface:abstractInterface, event: Event)-> ListOfVolunteersAtEvent:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return volunteer_allocation_data.load_list_of_volunteers_at_event(event)


def remove_volunteer_and_cadet_association_at_event(interface: abstractInterface, cadet_id: str, volunteer_id: str, event: Event):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.remove_volunteer_and_cadet_association_at_event(event=event, volunteer_id=volunteer_id, cadet_id=cadet_id)


def delete_volunteer_with_id_at_event(interface: abstractInterface, volunteer_id: str, event: Event):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.delete_volunteer_with_id_at_event(event=event, volunteer_id=volunteer_id)

    patrol_boat_data = PatrolBoatsData(interface.data)
    patrol_boat_data.delete_volunteer_with_id_at_event(event=event, volunteer_id=volunteer_id)

    delete_role_at_event_for_volunteer_on_all_days(interface=interface, volunteer_id=volunteer_id, event=event)


def update_volunteer_notes_at_event(interface: abstractInterface, event: Event, volunteer_id: str, new_notes: str):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.update_volunteer_notes_at_event(event=event, volunteer_id=volunteer_id, new_notes=new_notes)


def add_volunteer_and_cadet_association_for_existing_volunteer(interface: abstractInterface, cadet_id:str, volunteer_id: str, event: Event):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_volunteer_and_cadet_association_for_existing_volunteer(event=event, volunteer_id=volunteer_id, cadet_id=cadet_id)


def add_volunteer_to_event_with_just_id(interface: abstractInterface, volunteer_id: str, event: Event):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_volunteer_to_event_with_just_id(event=event, volunteer_id=volunteer_id)




def DEPRECATE_get_volunteer_at_event(volunteer_id: str, event: Event) -> VolunteerAtEvent:
    volunteers_at_event_data = DEPRECATED_load_list_of_volunteers_at_event(event)
    volunteer_at_event = volunteers_at_event_data.volunteer_at_event_with_id(volunteer_id)
    if volunteer_at_event is missing_data:
        raise Exception("Weirdly volunteer with id %s is no longer in event %s" % (volunteer_id, event))

    return volunteer_at_event


def get_volunteer_at_event(interface: abstractInterface, volunteer_id: str, event: Event) -> VolunteerAtEvent:
    volunteers_at_event_data = VolunteerAllocationData(interface.data)
    list_of_volunteers = volunteers_at_event_data.load_list_of_volunteers_at_event(event)
    volunteer_at_event = list_of_volunteers.volunteer_at_event_with_id(volunteer_id)
    if volunteer_at_event is missing_data:
        raise Exception("Weirdly volunteer with id %s is no longer in event %s" % (volunteer_id, event))

    return volunteer_at_event


def is_volunteer_already_at_event(interface: abstractInterface, volunteer_id: str, event: Event) -> bool:
    volunteers_at_event_data = VolunteerAllocationData(interface.data)
    return volunteers_at_event_data.is_volunteer_already_at_event(volunteer_id=volunteer_id, event=event)


def delete_role_at_event_for_volunteer_on_day(interface: abstractInterface,
                                              volunteer_id: str, day: Day,
                                                        event: Event):

    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.delete_role_at_event_for_volunteer_on_day(event=event, day=day, volunteer_id=volunteer_id)

def delete_role_at_event_for_volunteer_on_all_days(interface: abstractInterface,
                                              volunteer_id: str,
                                                        event: Event):

    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.delete_role_at_event_for_volunteer_on_all_days(event=event, volunteer_id=volunteer_id)



def DEPRECATE_load_volunteers_in_role_at_event(event: Event) -> ListOfVolunteersInRoleAtEvent:
    return DEPRECATED_data.data_list_of_volunteers_in_roles_at_event.read(event_id=event.id)


def get_volunteers_in_role_at_event_with_active_allocations(interface: abstractInterface, event: Event) -> ListOfVolunteersInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteers_in_role_at_event_who_are_also_allocated_to_event(event)


def update_role_at_event_for_volunteer_on_day(interface: abstractInterface,
                                              volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                    new_role: str,
                                     event: Event):

    volunteer_rota_data=  VolunteerRotaData(interface.data)
    volunteer_rota_data.update_role_at_event_for_volunteer_on_day_at_event(
        event=event,
        volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
        new_role=new_role
    )


def update_group_at_event_for_volunteer_on_day(interface: abstractInterface,
                                               volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                               new_group: str,
                                              event: Event):
    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_rota_data.update_group_at_event_for_volunteer_on_day(event=event,
                                                                   volunteer_in_role_at_event_on_day=volunteer_in_role_at_event_on_day,
                                                                   new_group=new_group)


def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(interface: abstractInterface,
                    event: Event,
                                                                                       volunteer_id: str,
                                                                                       day: Day):


    volunteer_data = VolunteerRotaData(interface.data)
    try:
        volunteer_data.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(event=event,
                                                                                                day=day,
                                                                                                volunteer_id=volunteer_id)
    except Exception as e:
        name = get_volunteer_name_from_id(interface=interface, volunteer_id=volunteer_id)
        interface.log_error("Can't copy across role data for %s on %s, error %s, conflicting change made?" % (name, day.name, str(e)))
