from typing import List

from app.objects.utils import in_x_not_in_y

from app.backend.data.volunteers import SORT_BY_FIRSTNAME

from app.objects.volunteers import ListOfVolunteers

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.storage_layer.api import DataLayer

from app.data_access.data import DEPRECATED_data
from app.objects.constants import missing_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers_at_event import ListOfVolunteersAtEvent, ListOfIdentifiedVolunteersAtEvent,\
    VolunteerAtEvent
from app.backend.data.volunteers import VolunteerData

class VolunteerAllocationData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def add_volunteer_and_cadet_association_for_existing_volunteer(self, cadet_id: str,
                                                                   volunteer_id: str, event: Event):

        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        list_of_volunteers_at_event.add_cadet_id_to_existing_volunteer(volunteer_id=volunteer_id, cadet_id=cadet_id)
        self.save_list_of_volunteers_at_event(list_of_volunteers_at_event=list_of_volunteers_at_event, event=event)

    def remove_volunteer_and_cadet_association_at_event(self, cadet_id: str, volunteer_id: str,
                                                        event: Event):

        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        list_of_volunteers_at_event.remove_cadet_id_association_from_volunteer(cadet_id=cadet_id,
                                                                               volunteer_id=volunteer_id)
        self.save_list_of_volunteers_at_event(list_of_volunteers_at_event=list_of_volunteers_at_event, event=event)

    def delete_volunteer_with_id_at_event(self, volunteer_id: str, event: Event):
        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        list_of_volunteers_at_event.remove_volunteer_with_id(volunteer_id=volunteer_id)
        self.save_list_of_volunteers_at_event(list_of_volunteers_at_event=list_of_volunteers_at_event, event=event)

    def add_volunteer_to_event_with_just_id(self, volunteer_id: str, event: Event):
        availability = event.day_selector_with_covered_days()  ## assume available all days in event
        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        list_of_volunteers_at_event.add_volunteer_with_just_id(volunteer_id,
                                                               availability=availability)
        self.save_list_of_volunteers_at_event(list_of_volunteers_at_event=list_of_volunteers_at_event, event=event)

    def update_volunteer_notes_at_event(self, event: Event, volunteer_id: str, new_notes: str):
        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        list_of_volunteers_at_event.update_volunteer_notes_at_event(volunteer_id=volunteer_id, new_notes=new_notes)
        self.save_list_of_volunteers_at_event(list_of_volunteers_at_event=list_of_volunteers_at_event, event=event)

    def make_volunteer_available_on_day(self, volunteer_id: str, event: Event, day: Day):
        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id)
        volunteer_at_event.availablity.make_available_on_day(day)
        self.save_list_of_volunteers_at_event(list_of_volunteers_at_event=list_of_volunteers_at_event, event=event)

    def make_volunteer_unavailable_on_day(self, volunteer_id: str, event: Event, day: Day):
        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(volunteer_id)
        volunteer_at_event.availablity.make_unavailable_on_day(day)
        self.save_list_of_volunteers_at_event(list_of_volunteers_at_event=list_of_volunteers_at_event, event=event)

    def volunteer_ids_associated_with_cadet_at_specific_event(self, event: Event,
                                                              cadet_id: str) -> List[str]:
        volunteer_data = self.load_list_of_volunteers_at_event(event)
        volunteer_ids = volunteer_data.list_of_volunteer_ids_associated_with_cadet_id(cadet_id)

        return volunteer_ids

    def add_volunteer_at_event(self, event: Event, volunteer_at_event: VolunteerAtEvent):
        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        list_of_volunteers_at_event.add_new_volunteer(volunteer_at_event)
        self.save_list_of_volunteers_at_event(list_of_volunteers_at_event=list_of_volunteers_at_event, event=event)

    def add_cadet_id_to_existing_volunteer(self, event: Event,
                                                                      volunteer_id: str,
                                                                      cadet_id: str):

        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        list_of_volunteers_at_event.add_cadet_id_to_existing_volunteer(cadet_id=cadet_id, volunteer_id=volunteer_id)
        self.save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)

    def get_volunteer_at_this_event(self, event: Event, volunteer_id: str) -> VolunteerAtEvent:
        list_of_volunteers = self.load_list_of_volunteers_at_event(event)
        volunteer_at_event = list_of_volunteers.volunteer_at_event_with_id(volunteer_id)

        return volunteer_at_event

    def get_sorted_list_of_volunteers_except_those_already_at_event(self,
                                                                    event: Event,
                                                                    sort_by: str = SORT_BY_FIRSTNAME) -> ListOfVolunteers:
        volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        volunteers_at_event_ids = volunteers_at_event.list_of_volunteer_ids
        master_list_of_volunteers = self.sorted_list_of_all_volunteers(sort_by)
        all_volunteer_ids = master_list_of_volunteers.list_of_ids
        ids_of_volunteers_not_at_event = in_x_not_in_y(x=all_volunteer_ids, y=volunteers_at_event_ids)

        return ListOfVolunteers.subset_from_list_of_ids(master_list_of_volunteers, ids_of_volunteers_not_at_event)

    def is_volunteer_already_at_event(self, event: Event, volunteer_id: str):
        list_of_volunteers_at_event = self.load_list_of_volunteers_at_event(event)
        return list_of_volunteers_at_event.is_volunteer_already_at_event(volunteer_id)

    def mark_volunteer_as_skipped(self,
                                  event: Event,
                                  row_id: str,
                                  volunteer_index: int):

        list_of_identified_volunteers_at_event = self.load_list_of_identified_volunteers_at_event(event)
        list_of_identified_volunteers_at_event.identified_as_processed_not_allocated(row_id=row_id, volunteer_index=volunteer_index)
        self.save_list_of_identified_volunteers_at_event(event=event, list_of_volunteers=list_of_identified_volunteers_at_event)

    def add_identified_volunteer(self,
        volunteer_id: str,
    event: Event,
    row_id: str,
    volunteer_index: int):
        list_of_volunteers_identified = self.load_list_of_identified_volunteers_at_event(event)
        list_of_volunteers_identified.add(row_id=row_id, volunteer_index=volunteer_index, volunteer_id=volunteer_id)
        self.save_list_of_identified_volunteers_at_event(list_of_volunteers=list_of_volunteers_identified, event=event)

    def volunteer_for_this_row_and_index_already_identified(self, event: Event, row_id: str,
                                                            volunteer_index: int) -> bool:
        list_of_volunteers_identified = self.load_list_of_identified_volunteers_at_event(event)
        volunteer_id = list_of_volunteers_identified.volunteer_id_given_row_id_and_index(row_id=row_id,
                                                                              volunteer_index=volunteer_index)
        return volunteer_id is not missing_data

    def load_list_of_identified_volunteers_at_event(self, event: Event)-> ListOfIdentifiedVolunteersAtEvent:
        return self.data_api.get_list_of_identified_volunteers_at_event(event=event)

    def save_list_of_identified_volunteers_at_event(self, event: Event, list_of_volunteers: ListOfIdentifiedVolunteersAtEvent):
        return self.data_api.save_list_of_identified_volunteers_at_event(list_of_volunteers=list_of_volunteers, event=event)

    def load_list_of_volunteers_at_event(self, event: Event) -> ListOfVolunteersAtEvent:
        return self.data_api.get_list_of_volunteers_at_event(event=event)

    def save_list_of_volunteers_at_event(self, event: Event, list_of_volunteers_at_event: ListOfVolunteersAtEvent):
        self.data_api.save_list_of_volunteers_at_event(event=event,
                                                               list_of_volunteers_at_event=list_of_volunteers_at_event)

    def sorted_list_of_all_volunteers(self, sort_by: str) -> ListOfVolunteers:
        return self.volunteer_data.get_sorted_list_of_volunteers(sort_by)

    @property
    def volunteer_data(self) -> VolunteerData:
        return VolunteerData(self.data_api)

def DEPRECATED_load_list_of_identified_volunteers_at_event(event: Event) -> ListOfIdentifiedVolunteersAtEvent:
    return DEPRECATED_data.data_list_of_identified_volunteers_at_event.read(event_id=event.id)

def load_list_of_identified_volunteers_at_event(interface: abstractInterface, event: Event) -> ListOfIdentifiedVolunteersAtEvent:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return volunteer_allocation_data.load_list_of_identified_volunteers_at_event(event)

def DEPRECATED_save_list_of_identified_volunteers_at_event(event: Event, list_of_volunteers: ListOfIdentifiedVolunteersAtEvent):
    DEPRECATED_data.data_list_of_identified_volunteers_at_event.write(list_of_identified_volunteers=list_of_volunteers, event_id=event.id)

def DEPRECATED_load_list_of_volunteers_at_event(event: Event)-> ListOfVolunteersAtEvent:
    return DEPRECATED_data.data_list_of_volunteers_at_event.read(event_id=event.id)

def load_list_of_volunteers_at_event(interface:abstractInterface, event: Event)-> ListOfVolunteersAtEvent:
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    return volunteer_allocation_data.load_list_of_volunteers_at_event(event)


def DEPRECATED_save_list_of_volunteers_at_event(event: Event, list_of_volunteers_at_event: ListOfVolunteersAtEvent):
    DEPRECATED_data.data_list_of_volunteers_at_event.write(event_id=event.id, list_of_volunteers_at_event=list_of_volunteers_at_event)








def DEPRECATE_remove_volunteer_and_cadet_association_at_event(cadet_id: str, volunteer_id: str, event: Event):
    list_of_volunteers_at_event = DEPRECATED_load_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.remove_cadet_id_association_from_volunteer(cadet_id=cadet_id, volunteer_id=volunteer_id)
    DEPRECATED_save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def remove_volunteer_and_cadet_association_at_event(interface: abstractInterface, cadet_id: str, volunteer_id: str, event: Event):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.remove_volunteer_and_cadet_association_at_event(event=event, volunteer_id=volunteer_id, cadet_id=cadet_id)


def DEPRECATE_delete_volunteer_with_id_at_event(volunteer_id: str, event: Event):
    list_of_volunteers_at_event= DEPRECATED_load_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.remove_volunteer_with_id(volunteer_id=volunteer_id)
    DEPRECATED_save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)

def delete_volunteer_with_id_at_event(interface: abstractInterface, volunteer_id: str, event: Event):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.delete_volunteer_with_id_at_event(event=event, volunteer_id=volunteer_id)


def update_volunteer_notes_at_event(interface: abstractInterface, event: Event, volunteer_id: str, new_notes: str):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.update_volunteer_notes_at_event(event=event, volunteer_id=volunteer_id, new_notes=new_notes)


def add_volunteer_and_cadet_association_for_existing_volunteer(interface: abstractInterface, cadet_id:str, volunteer_id: str, event: Event):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_volunteer_and_cadet_association_for_existing_volunteer(event=event, volunteer_id=volunteer_id, cadet_id=cadet_id)


def add_volunteer_to_event_with_just_id(interface: abstractInterface, volunteer_id: str, event: Event):
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteer_allocation_data.add_volunteer_to_event_with_just_id(event=event, volunteer_id=volunteer_id)




def DEPRECATE_update_volunteer_at_event(volunteer_at_event: VolunteerAtEvent, event: Event):
    list_of_volunteers_at_event = DEPRECATED_load_list_of_volunteers_at_event(event)
    list_of_volunteers_at_event.update_volunteer_at_event(volunteer_at_event)
    DEPRECATED_save_list_of_volunteers_at_event(event=event, list_of_volunteers_at_event=list_of_volunteers_at_event)


def days_at_event_when_volunteer_available(event: Event,
                                                                             volunteer_id: str) -> List[Day]:
    volunteer_at_event = DEPRECATE_get_volunteer_at_event(volunteer_id=volunteer_id, event=event)
    all_days = [day
                    for day in event.weekdays_in_event()
                        if volunteer_at_event.availablity.available_on_day(day)]

    return all_days


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

