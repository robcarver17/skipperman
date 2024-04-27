from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.volunteer_allocation import days_at_event_when_volunteer_available
from app.backend.data.volunteer_allocation import VolunteerAllocationData
from app.data_access.data import DEPRECATED_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers_in_roles import VolunteerInRoleAtEvent, ListOfVolunteersInRoleAtEvent, NO_ROLE_SET

from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.storage_layer.api import DataLayer

from app.data_access.data import DEPRECATED_data
from app.objects.constants import missing_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers_at_event import ListOfVolunteersAtEvent, ListOfIdentifiedVolunteersAtEvent,\
    VolunteerAtEvent


class VolunteerRotaData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def get_volunteers_in_role_at_event_with_active_allocations(self, event: Event)-> ListOfVolunteersInRoleAtEvent:
        list_of_volunteers_at_event = self.volunteer_allocation_data.load_list_of_volunteers_at_event(event)
        list_of_volunteer_ids_at_event = list_of_volunteers_at_event.list_of_volunteer_ids
        list_of_volunteers_in_role_at_event = self.get_list_of_volunteers_in_roles_at_event(event)
        volunteers_in_roles_and_at_event = list_of_volunteers_in_role_at_event.list_if_volunteer_id_in_list_of_ids(list_of_volunteer_ids_at_event)

        return volunteers_in_roles_and_at_event

    def get_list_of_volunteers_in_roles_at_event(self, event: Event) -> ListOfVolunteersInRoleAtEvent:
        return self.data_api.get_list_of_volunteers_in_roles_at_event(event=event)

    def save_list_of_volunteers_in_roles_at_event(self, event: Event, list_of_volunteers_in_role_at_event: ListOfVolunteersInRoleAtEvent):
        self.data_api.save_list_of_volunteers_in_roles_at_event(event=event,
                                                               list_of_volunteers_in_role_at_event=list_of_volunteers_in_role_at_event)


    @property
    def volunteer_allocation_data(self) -> VolunteerAllocationData:
        return VolunteerAllocationData(self.data_api)

def delete_role_at_event_for_volunteer_on_day(volunteer_id: str, day: Day,
                                     event: Event):
    volunteer_in_role_at_event_on_day = VolunteerInRoleAtEvent(volunteer_id=volunteer_id,
                                                               day=day)

    list_of_volunteers_in_roles_at_event = DEPRECATE_load_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.delete_volunteer_in_role_at_event_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day)
    save_volunteers_in_role_at_event(event=event,
                                                         list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def DEPRECATE_load_volunteers_in_role_at_event(event: Event) -> ListOfVolunteersInRoleAtEvent:
    return DEPRECATED_data.data_list_of_volunteers_in_roles_at_event.read(event_id=event.id)

def get_volunteers_in_role_at_event_with_active_allocations(interface: abstractInterface, event: Event) -> ListOfVolunteersInRoleAtEvent:
    volunteer_role_data = VolunteerRotaData(interface.data)
    return volunteer_role_data.get_volunteers_in_role_at_event_with_active_allocations(event)


def save_volunteers_in_role_at_event(event: Event, list_of_volunteers_in_roles_at_event:ListOfVolunteersInRoleAtEvent):
    DEPRECATED_data.data_list_of_volunteers_in_roles_at_event.write(event_id=event.id,
                                                                    list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def update_role_at_event_for_volunteer_on_day(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                    new_role: str,
                                     event: Event):


    list_of_volunteers_in_roles_at_event = DEPRECATE_load_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.update_volunteer_in_role_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
                                                             new_role=new_role)
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def remove_role_at_event_for_volunteer_on_day(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                     event: Event):


    list_of_volunteers_in_roles_at_event = DEPRECATE_load_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.delete_volunteer_in_role_at_event_on_day(volunteer_in_role_at_event_on_day)
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)



def update_group_at_event_for_volunteer_on_day(volunteer_in_role_at_event_on_day: VolunteerInRoleAtEvent,
                                               new_group: str,
                                              event: Event):
    list_of_volunteers_in_roles_at_event = DEPRECATE_load_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.update_volunteer_in_group_on_day(volunteer_in_role_at_event=volunteer_in_role_at_event_on_day,
                                                              new_group=new_group)
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(event: Event,
                                                                             volunteer_id: str,
                                                                             day: Day):

    list_of_volunteers_in_roles_at_event = DEPRECATE_load_volunteers_in_role_at_event(event)
    list_of_volunteers_in_roles_at_event.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        volunteer_id=volunteer_id,
        day=day,
        list_of_all_days=days_at_event_when_volunteer_available(event=event, volunteer_id=volunteer_id)
    )
    save_volunteers_in_role_at_event(event=event, list_of_volunteers_in_roles_at_event=list_of_volunteers_in_roles_at_event)


def delete_role_at_event_for_volunteer_on_all_days(volunteer_id: str,
                                     event: Event):

    for day in event.weekdays_in_event():
        delete_role_at_event_for_volunteer_on_day(volunteer_id=volunteer_id,
                                                  day=day,
                                                  event=event)
