from dataclasses import dataclass
from typing import List, Dict

from app.backend.events import get_list_of_events
from app.backend.group_allocations.cadet_event_allocations import load_allocation_for_event, get_unallocated_cadets
from app.backend.volunteers.volunteer_allocation import get_volunteer_at_event, update_volunteer_at_event, \
    get_volunteer_data_for_event
from app.backend.volunteers import get_list_of_volunteers
from app.objects.cadets import ListOfCadets
from app.objects.constants import missing_data
from app.objects.events import Event, SORT_BY_START_ASC
from app.objects.groups import Group, ListOfCadetIdsWithGroups, GROUP_UNALLOCATED, ALL_GROUPS_NAMES, GROUP_UNALLOCATED_TEXT
from app.objects.volunteers_at_event import VolunteerAtEvent, ListOfVolunteersAtEvent
from app.objects.volunteers import Volunteer
from app.objects.volunteers import ListOfVolunteerSkills
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent, ListOfVolunteersInRoleAtEvent, VOLUNTEER_ROLES, \
    NO_ROLE_SET

from app.objects.day_selectors import Day

from app.data_access.data import data


@dataclass
class DataToBeStoredWhilstConstructingTableBody:
    event: Event
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
    unallocated_cadets_at_event: ListOfCadets
    volunteer_skills: ListOfVolunteerSkills
    volunteers_in_roles_at_event: ListOfVolunteersInRoleAtEvent
    list_of_volunteers_at_event: ListOfVolunteersAtEvent
    dict_of_volunteers_with_last_roles: Dict[str, str]

    def group_given_cadet_id(self, cadet_id):
        try:
            cadet_with_group = self.list_of_cadet_ids_with_groups.item_with_cadet_id(cadet_id)
            return cadet_with_group.group
        except:
            try:
                __unallocated_cadet_unused = self.unallocated_cadets_at_event.object_with_id(cadet_id)
                return GROUP_UNALLOCATED
            except:
                return missing_data

    def list_of_skills_given_volunteer_id(self, volunteer_id: str)->dict:
        return self.volunteer_skills.skills_for_volunteer_id(volunteer_id)

    def volunteer_in_role_at_event_on_day(self, volunteer_id: str, day: Day) -> VolunteerInRoleAtEvent:
        return self.volunteers_in_roles_at_event.member_matching_volunteer_id_and_day(volunteer_id=volunteer_id, day=day)

    def all_roles_match_across_event(self, volunteer_id: str)->bool:
        all_volunteers_in_roles_at_event = [self.volunteer_in_role_at_event_on_day(volunteer_id=volunteer_id,
                                                                                   day=day)
                                            for day in self.event.weekdays_in_event()]
        all_roles = [volunteer_in_role_at_event_on_day.role for volunteer_in_role_at_event_on_day in all_volunteers_in_roles_at_event]
        all_groups = [volunteer_in_role_at_event_on_day.group for volunteer_in_role_at_event_on_day in all_volunteers_in_roles_at_event]


        all_groups_match = len(set(all_groups))<=1
        all_roles_match = len(set(all_roles))<=1

        return all_roles_match and all_groups_match

def sort_volunteer_data_for_event_by_name_sort_order(volunteers_at_event: ListOfVolunteersAtEvent, sort_order) -> ListOfVolunteersAtEvent:
    list_of_volunteers = get_list_of_volunteers(sort_by=sort_order)
    ## this works because if an ID is missing we just ignore it
    return volunteers_at_event.sort_by_list_of_volunteer_ids(list_of_volunteers.list_of_ids)

def sort_volunteer_data_for_event_by_day_sort_order(
            list_of_volunteers_at_event: ListOfVolunteersAtEvent,
        sort_by_day: Day,
        data_to_be_stored: DataToBeStoredWhilstConstructingTableBody) -> ListOfVolunteersAtEvent:

    tuple_of_volunteers_at_event_and_roles = [(volunteer_at_event,
                                                    data_to_be_stored.volunteer_in_role_at_event_on_day(
                                                    volunteer_id=volunteer_at_event.volunteer_id, day=sort_by_day).role_and_group
                                               )
                            for volunteer_at_event in list_of_volunteers_at_event]

    tuple_of_volunteers_at_event_and_roles.sort(key=lambda tup: tup[1])

    list_of_volunteers = [volunteer_at_event for volunteer_at_event, __ in tuple_of_volunteers_at_event_and_roles]

    return ListOfVolunteersAtEvent(list_of_volunteers)

def get_data_to_be_stored(event: Event) -> DataToBeStoredWhilstConstructingTableBody:
    list_of_cadet_ids_with_groups = load_allocation_for_event(event=event)
    unallocated_cadets_at_event = get_unallocated_cadets(event=event, list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups)
    volunteer_skills = get_all_skills_from_data()
    volunteers_in_roles_at_event = get_volunteers_in_role_at_event(event)
    list_of_volunteers_at_event = get_volunteer_data_for_event(event)
    dict_of_volunteers_with_last_roles = get_dict_of_volunteers_with_last_roles(list_of_volunteers_at_event.list_of_volunteer_ids,
                                                                                avoid_event=event)

    return DataToBeStoredWhilstConstructingTableBody(
        event=event,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        unallocated_cadets_at_event=unallocated_cadets_at_event,
        volunteer_skills=volunteer_skills,
        volunteers_in_roles_at_event=volunteers_in_roles_at_event,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        dict_of_volunteers_with_last_roles=dict_of_volunteers_with_last_roles
    )


def get_all_skills_from_data()-> ListOfVolunteerSkills:
    skills = data.data_list_of_volunteer_skills.read()

    return skills

def get_dict_of_volunteers_with_last_roles(list_of_volunteer_ids: List[str], avoid_event: Event) -> Dict[str, str]:
    return dict([
        (volunteer_id, get_last_role_for_volunteer_id(volunteer_id=volunteer_id, avoid_event=avoid_event))
        for volunteer_id in list_of_volunteer_ids
    ])


def get_last_role_for_volunteer_id(volunteer_id: str, avoid_event: Event) -> str:
    all_previous_events = get_list_of_events(SORT_BY_START_ASC) ## latest last
    all_previous_events.pop_with_id(avoid_event.id)
    roles = [get_role_for_event_and_volunteer_id(volunteer_id, event) for event in all_previous_events]
    roles = [role for role in roles if role is not missing_data]
    if len(roles)==0:
        return ""

    return roles[-1] ## most recent role

def get_role_for_event_and_volunteer_id(volunteer_id: str, event: Event) -> str:
    volunteer_data = get_volunteers_in_role_at_event(event)
    role = volunteer_data.most_common_role_at_event_for_volunteer(volunteer_id=volunteer_id)
    if role==NO_ROLE_SET:
        return missing_data
    return role

def get_volunteers_in_role_at_event(event: Event) -> ListOfVolunteersInRoleAtEvent:
    return data.data_list_of_volunteers_in_roles_at_event.read(event_id=event.id)

def get_cadet_location_string(data_to_be_stored: DataToBeStoredWhilstConstructingTableBody, volunteer_at_event: VolunteerAtEvent):
    list_of_cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    if len(list_of_cadet_ids)==0:
        return "No associated cadets"
    list_of_groups = [data_to_be_stored.group_given_cadet_id(cadet_id) for cadet_id in list_of_cadet_ids]
    list_of_groups = [group for group in list_of_groups if group is not missing_data]

    return str_type_of_group_given_list_of_groups(list_of_groups)


def str_type_of_group_given_list_of_groups(list_of_groups: List[Group]):
    types_of_groups = [group.type_of_group() for group in list_of_groups]
    unique_list_of_groups = list(set(types_of_groups))

    return ", ".join(unique_list_of_groups)

def str_dict_skills(volunteer: Volunteer, data_to_be_stored: DataToBeStoredWhilstConstructingTableBody):
    list_of_skills = data_to_be_stored.list_of_skills_given_volunteer_id(volunteer.id)
    if len(list_of_skills)==0:
        return "No skills recorded"

    return ", ".join(list_of_skills)

def dict_of_groups_for_dropdown():
    dict_of_groups = {group:group for group in ALL_GROUPS_NAMES}
    dict_of_groups[GROUP_UNALLOCATED_TEXT]= GROUP_UNALLOCATED_TEXT

    return dict_of_groups

MAKE_UNAVAILABLE = "Unavailable"
def dict_of_roles_for_dropdown():
    dict_of_roles = {role:role for role in VOLUNTEER_ROLES}
    dict_of_roles[NO_ROLE_SET] = NO_ROLE_SET
    dict_of_roles[MAKE_UNAVAILABLE] = MAKE_UNAVAILABLE

    return dict_of_roles


def make_volunteer_available_on_day(volunteer_id: str, event: Event, day: Day):
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    volunteer_at_event.availablity.make_available_on_day(day)
    update_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)

def make_volunteer_unavailable_on_day(volunteer_id: str, event: Event, day: Day):
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    volunteer_at_event.availablity.make_unavailable_on_day(day)
    update_volunteer_at_event(volunteer_at_event=volunteer_at_event, event=event)

def update_role_at_event_for_volunteer_on_day(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                    new_role: str,
                                     event: Event):

    volunteers_in_roles_data = data.data_list_of_volunteers_in_roles_at_event.read(event_id=event.id)
    volunteers_in_roles_data.update_volunteer_in_role_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
                                                             new_role=new_role)
    data.data_list_of_volunteers_in_roles_at_event.write(event_id=event.id,
                                                         list_of_volunteers_in_roles_at_event=volunteers_in_roles_data)


def update_group_at_event_for_volunteer_on_day(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                               new_group: str,
                                              event: Event):
    volunteers_in_roles_data = data.data_list_of_volunteers_in_roles_at_event.read(event_id=event.id)
    volunteers_in_roles_data.update_volunteer_in_group_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
                                                              new_group=new_group)
    data.data_list_of_volunteers_in_roles_at_event.write(event_id=event.id,
                                                         list_of_volunteers_in_roles_at_event=volunteers_in_roles_data)

def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(event: Event,
                                                                             volunteer_id: str,
                                                                             day: Day):

    volunteers_in_roles_data = data.data_list_of_volunteers_in_roles_at_event.read(event_id=event.id)
    volunteers_in_roles_data.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        volunteer_id=volunteer_id,
        day=day,
        list_of_all_days=days_at_event_when_volunteer_available(event=event, volunteer_id=volunteer_id)
    )
    data.data_list_of_volunteers_in_roles_at_event.write(event_id=event.id,
                                                         list_of_volunteers_in_roles_at_event=volunteers_in_roles_data)

def days_at_event_when_volunteer_available(event: Event,
                                                                             volunteer_id: str) -> List[Day]:
    volunteer_at_event = get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    all_days = [day
                    for day in event.weekdays_in_event()
                        if volunteer_at_event.availablity.available_on_day(day)]

    return all_days