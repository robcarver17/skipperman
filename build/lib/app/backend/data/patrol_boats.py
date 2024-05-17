from typing import List

from app.objects.day_selectors import Day

from app.objects.constants import missing_data

from app.data_access.storage_layer.api import DataLayer

from app.objects.events import Event
from app.objects.patrol_boats import ListOfPatrolBoats, ListOfVolunteersAtEventWithPatrolBoats, PatrolBoat

from app.data_access.data import DEPRECATED_data
from app.objects.utils import in_x_not_in_y, in_both_x_and_y
from app.backend.data.volunteer_allocation import VolunteerAllocationData


class PatrolBoatsData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def swap_boats_for_volunteers_in_allocation(self,
                                                event: Event,
                                                original_day: Day,
                                                day_to_swap_with: Day,
                                                original_volunteer_id:str,
                                                volunteer_id_to_swap_with: str):

        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        list_of_voluteers_at_event_with_patrol_boats.swap_boats_for_volunteers_in_allocation(
            original_volunteer_id=original_volunteer_id,
            volunteer_id_to_swap_with=volunteer_id_to_swap_with,
            day_to_swap_with=day_to_swap_with,
            original_day=original_day
        )

        self.save_list_of_voluteers_at_event_with_patrol_boats(list_of_volunteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                                                               event=event)

    def copy_across_allocation_of_boats_at_event(self, event: Event, day: Day,
                                                 volunteer_id: str):

        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        list_of_voluteers_at_event_with_patrol_boats.copy_across_allocation_of_boats_at_event(day=day,
                                                                                              volunteer_id=volunteer_id,
                                                                                              event=event)
        self.save_list_of_voluteers_at_event_with_patrol_boats(list_of_volunteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                                                               event=event)

    def remove_patrol_boat_and_all_associated_volunteer_connections_from_event(self,
                                                                               event: Event, patrol_boat_name: str):
        patrol_boat_id = self.patrol_boat_id_given_name(patrol_boat_name)
        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        list_of_voluteers_at_event_with_patrol_boats.remove_patrol_boat_id_and_all_associated_volunteer_connections_from_event(
            patrol_boat_id)
        self.save_list_of_voluteers_at_event_with_patrol_boats(list_of_volunteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                                                               event=event)

    def add_named_boat_to_event_with_no_allocation(self, name_of_boat_added: str, event: Event):
        patrol_boat_id = self.patrol_boat_id_given_name(name_of_boat_added)

        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        list_of_voluteers_at_event_with_patrol_boats.add_unallocated_boat(patrol_boat_id=patrol_boat_id)

        self.save_list_of_voluteers_at_event_with_patrol_boats(list_of_volunteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                                                               event=event)

    def patrol_boat_id_given_name(self, patrol_boat_name: str) -> str:
        list_of_patrol_boats = self.get_list_of_patrol_boats()
        patrol_boat_id = list_of_patrol_boats.id_given_name(patrol_boat_name)

        return patrol_boat_id

    def remove_volunteer_from_patrol_boat_on_day_at_event(self, volunteer_id: str, day: Day,
                                                          event: Event):

        print("Removing %s %s %s" % (volunteer_id, day.name, event.event_name))
        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        list_of_voluteers_at_event_with_patrol_boats.remove_volunteer_from_patrol_boat_on_day_at_event(
            volunteer_id=volunteer_id,
            day=day
        )
        self.save_list_of_voluteers_at_event_with_patrol_boats(list_of_volunteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                                                               event=event)

    def get_sorted_list_of_boats_excluding_boats_already_at_event(self,
                                                                  event: Event) -> ListOfPatrolBoats:
        list_of_all_patrol_boats = self.get_list_of_patrol_boats()
        list_of_patrol_boats_at_event = self.list_of_unique_boats_at_event_including_unallocated(event)
        boats_not_already_at_event = in_x_not_in_y(x=list_of_all_patrol_boats, y=list_of_patrol_boats_at_event)
        sorted_boats_not_already_at_event = [boat for boat in list_of_all_patrol_boats if
                                             boat in boats_not_already_at_event]

        return ListOfPatrolBoats(sorted_boats_not_already_at_event)

    def get_all_volunteer_ids_allocated_to_any_boat_or_day(self,
                                                           event: Event) -> List[str]:

        list_of_voluteers_at_event_with_patrol_boats = DEPRECATE_load_list_of_voluteers_at_event_with_patrol_boats(event)
        list_of_volunteer_ids_allocated_to_any_boat_or_day = list_of_voluteers_at_event_with_patrol_boats.list_of_all_volunteer_ids_at_event()
        list_of_volunteer_ids_at_event = self.load_list_of_volunteer_ids_at_event(event)

        return in_both_x_and_y(list_of_volunteer_ids_at_event, list_of_volunteer_ids_allocated_to_any_boat_or_day)


    def get_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(self,
                                                                                           event: Event,
                                                                                           day: Day):
        volunteer_ids_already_allocated = self.get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(
             event = event, day = day)

        list_of_volunteer_ids_at_event_on_given_day = self.get_volunteer_ids_at_event_on_given_day(event=event, day=day)

        volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day = in_x_not_in_y(
            x=list_of_volunteer_ids_at_event_on_given_day,
            y=volunteer_ids_already_allocated
        )

        return volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day

    def get_volunteer_ids_at_event_on_given_day(self,
                                                                                           event: Event,
                                                                                           day: Day) -> List[str]:

        list_of_volunteers_at_event = self.get_list_of_volunteers_at_event(event)
        list_of_volunteers_at_event_on_given_day = list_of_volunteers_at_event.list_of_volunteers_available_on_given_day(
            day=day)
        list_of_volunteer_ids_at_event_on_given_day = list_of_volunteers_at_event_on_given_day.list_of_volunteer_ids

        return list_of_volunteer_ids_at_event_on_given_day



    def get_boat_name_allocated_to_volunteer_on_day_at_event(self, event: Event, day: Day,
                                                             volunteer_id: str) -> str:
        boat = self.get_boat_allocated_to_volunteer_on_day_at_event(
            event=event,
            day=day,
            volunteer_id=volunteer_id
        )
        if boat is missing_data:
            return missing_data

        return boat.name

    def get_boat_allocated_to_volunteer_on_day_at_event(self, event: Event, day: Day,
                                                             volunteer_id: str) -> PatrolBoat:
        patrol_boat_id = self.get_boat_id_is_volunteer_on_today(event=event,
                                                                day=day,
                                                                volunteer_id=volunteer_id)
        if patrol_boat_id is missing_data:
            return missing_data

        boats = self.get_list_of_patrol_boats()
        boat = boats.object_with_id(patrol_boat_id)

        return boat


    def get_boat_id_is_volunteer_on_today(self, event: Event, day: Day,
                                                             volunteer_id: str) -> str:
        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        patrol_boat_id = list_of_voluteers_at_event_with_patrol_boats.which_boat_id_is_volunteer_on_today(day=day,
                                                                                                          volunteer_id=volunteer_id)
        return patrol_boat_id


    def volunteer_is_on_same_boat_for_all_days(self,
                                               event: Event,
                                               volunteer_id: str) -> bool:

        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        return list_of_voluteers_at_event_with_patrol_boats.volunteer_is_on_same_boat_for_all_days(
            volunteer_id=volunteer_id, event=event)

    def list_of_volunteer_ids_assigned_to_boat_and_day(self, event: Event, patrol_boat: PatrolBoat, day: Day):

        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)

        list_of_volunteer_ids_assigned_to_boat_and_day= list_of_voluteers_at_event_with_patrol_boats.list_of_volunteer_ids_assigned_to_boat_and_day(
            day=day,
            patrol_boat=patrol_boat)
        list_of_volunteer_ids_at_event = self.load_list_of_volunteer_ids_at_event(event)

        return in_both_x_and_y(list_of_volunteer_ids_at_event, list_of_volunteer_ids_assigned_to_boat_and_day)


    def get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(self,
                                                                       event: Event,
                                                                       day: Day) :
        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        list_of_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day = list_of_voluteers_at_event_with_patrol_boats.list_of_volunteer_ids_assigned_to_any_boat_on_day(day=day)

        list_of_volunteer_ids_at_event = self.load_list_of_volunteer_ids_at_event(event)

        return in_both_x_and_y(list_of_volunteer_ids_at_event, list_of_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day)


    def list_of_unique_boats_at_event_including_unallocated(self, event: Event):
        list_of_patrol_boats = self.get_list_of_patrol_boats()
        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        list_of_boats_at_event = list_of_voluteers_at_event_with_patrol_boats.list_of_unique_boats_at_event_including_unallocated(
            list_of_patrol_boats)

        return list_of_boats_at_event

    def get_list_of_patrol_boats(self) -> ListOfPatrolBoats:
        return self.data_api.get_list_of_patrol_boats()

    def save_list_of_patrol_boats(self, list_of_boats: ListOfPatrolBoats):
        self.data_api.save_list_of_patrol_boats(list_of_boats)

    def get_list_of_voluteers_at_event_with_patrol_boats(self, event: Event) -> ListOfVolunteersAtEventWithPatrolBoats:
        return self.data_api.get_list_of_voluteers_at_event_with_patrol_boats(event)

    def save_list_of_voluteers_at_event_with_patrol_boats(self, event: Event, list_of_volunteers_at_event_with_patrol_boats: ListOfVolunteersAtEventWithPatrolBoats):
        self.data_api.save_list_of_voluteers_at_event_with_patrol_boats(list_of_voluteers_at_event_with_patrol_boats=list_of_volunteers_at_event_with_patrol_boats, event=event)

    def load_list_of_volunteer_ids_at_event(self, event: Event) -> List[str]:
        list_of_volunteers = self.get_list_of_volunteers_at_event(event)
        return list_of_volunteers.list_of_volunteer_ids

    def get_list_of_volunteers_at_event(self, event: Event):
        return self.volunteers_at_event_data.load_list_of_volunteers_at_event(event)

    @property
    def volunteers_at_event_data(self) -> VolunteerAllocationData:
        return VolunteerAllocationData(self.data_api)



def from_patrol_boat_name_to_boat(boat_name: str) -> PatrolBoat:
    list_of_patrol_boats = DEPRECATED_load_list_of_patrol_boats()
    return list_of_patrol_boats.boat_given_name(boat_name)

def DEPRECATED_load_list_of_patrol_boats() -> ListOfPatrolBoats:
    list_of_patrol_boats = DEPRECATED_data.data_list_of_patrol_boats.read()

    return list_of_patrol_boats


def DEPRECATE_load_list_of_voluteers_at_event_with_patrol_boats(event: Event) -> ListOfVolunteersAtEventWithPatrolBoats:
    volunteers_with_boats_at_event = DEPRECATED_data.data_list_of_volunteers_at_event_with_patrol_boats.read(event_id=event.id)

    return volunteers_with_boats_at_event



