from typing import List

from app.objects.cadets import Cadet

from app.objects.utils import in_x_not_in_y

from app.OLD_backend.data.volunteers import SORT_BY_FIRSTNAME

from app.objects.volunteers import ListOfVolunteers, Volunteer

from app.data_access.store.data_access import DataLayer

from app.objects.exceptions import missing_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects_OLD.volunteers_at_event import (
    ListOfVolunteersAtEvent,
    DEPRECATE_VolunteerAtEvent,
)
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId, ListOfVolunteersAtEventWithId
from app.objects_OLD.primtive_with_id.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent
from app.OLD_backend.data.volunteers import VolunteerData


class VolunteerAllocationData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def add_volunteer_and_cadet_association_for_existing_volunteer(
        self,  event: Event,  volunteer: Volunteer, cadet: Cadet
    ):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        list_of_volunteers_at_event.add_cadet_id_to_existing_volunteer(
            volunteer_id=volunteer.id, cadet_id=cadet.id
        )
        self.save_list_of_volunteers_at_event(
            list_of_volunteers_at_event=list_of_volunteers_at_event, event=event
        )

    def remove_volunteer_and_cadet_association_at_event(
        self,  event: Event, cadet: Cadet, volunteer: Volunteer
    ):
        self.remove_volunteer_and_cadet_with_ids_association_at_event(event=event,
                                                                      volunteer_id = volunteer.id,
                                                                      cadet_id=cadet.id)


    def remove_volunteer_and_cadet_with_ids_association_at_event(
        self, cadet_id: str, volunteer_id: str, event: Event
    ):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        list_of_volunteers_at_event.remove_cadet_id_association_from_volunteer(
            cadet_id=cadet_id, volunteer_id=volunteer_id
        )
        self.save_list_of_volunteers_at_event(
            list_of_volunteers_at_event=list_of_volunteers_at_event, event=event
        )

    def delete_volunteer_with_id_at_event(self, volunteer_id: str, event: Event):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        list_of_volunteers_at_event.remove_volunteer_with_id(volunteer_id=volunteer_id)
        self.save_list_of_volunteers_at_event(
            list_of_volunteers_at_event=list_of_volunteers_at_event, event=event
        )

    def add_volunteer_to_event_with_just_id(self, volunteer_id: str, event: Event):
        availability = (
            event.day_selector_with_covered_days()
        )  ## assume available all days in event
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        list_of_volunteers_at_event.add_volunteer_with_just_id(
            volunteer_id, availability=availability
        )
        self.save_list_of_volunteers_at_event(
            list_of_volunteers_at_event=list_of_volunteers_at_event, event=event
        )

    def update_volunteer_notes_at_event(
        self, event: Event, volunteer_id: str, new_notes: str
    ):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        list_of_volunteers_at_event.update_volunteer_notes_at_event(
            volunteer_id=volunteer_id, new_notes=new_notes
        )
        self.save_list_of_volunteers_at_event(
            list_of_volunteers_at_event=list_of_volunteers_at_event, event=event
        )

    def make_volunteer_available_on_day(
        self, volunteer: Volunteer, event: Event, day: Day
    ):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(
            volunteer.id
        )
        volunteer_at_event.availablity.make_available_on_day(day)
        self.save_list_of_volunteers_at_event(
            list_of_volunteers_at_event=list_of_volunteers_at_event, event=event
        )

    def make_volunteer_unavailable_on_day(
        self, volunteer: Volunteer, event: Event, day: Day
    ):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        volunteer_at_event = list_of_volunteers_at_event.volunteer_at_event_with_id(
            volunteer.id
        )
        volunteer_at_event.availablity.make_unavailable_on_day(day)
        self.save_list_of_volunteers_at_event(
            list_of_volunteers_at_event=list_of_volunteers_at_event, event=event
        )

    def volunteer_ids_associated_with_cadet_at_specific_event(
        self, event: Event, cadet_id: str
    ) -> List[str]:
        volunteer_data = self.load_list_of_volunteers_with_ids_at_event(event)
        volunteer_ids = volunteer_data.list_of_volunteer_ids_associated_with_cadet_id(
            cadet_id
        )

        return volunteer_ids

    def add_volunteer_at_event(
        self, event: Event, volunteer_at_event: VolunteerAtEventWithId
    ):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        list_of_volunteers_at_event.add_new_volunteer(volunteer_at_event)
        self.save_list_of_volunteers_at_event(
            list_of_volunteers_at_event=list_of_volunteers_at_event, event=event
        )

    def add_cadet_id_to_existing_volunteer(
        self, event: Event, volunteer_id: str, cadet_id: str
    ):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        list_of_volunteers_at_event.add_cadet_id_to_existing_volunteer(
            cadet_id=cadet_id, volunteer_id=volunteer_id
        )
        self.save_list_of_volunteers_at_event(
            event=event, list_of_volunteers_at_event=list_of_volunteers_at_event
        )

    def get_volunteer_at_this_event(
        self, event: Event, volunteer_id: str
    ) -> VolunteerAtEventWithId:
        list_of_volunteers = self.load_list_of_volunteers_with_ids_at_event(event)
        volunteer_at_event = list_of_volunteers.volunteer_at_event_with_id(volunteer_id)

        return volunteer_at_event

    def get_sorted_list_of_volunteers_except_those_already_at_event(
        self, event: Event, sort_by: str = SORT_BY_FIRSTNAME
    ) -> ListOfVolunteers:
        volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(event)
        volunteers_at_event_ids = volunteers_at_event.list_of_volunteer_ids
        master_list_of_volunteers = self.sorted_list_of_all_volunteers(sort_by)
        all_volunteer_ids = master_list_of_volunteers.list_of_ids
        ids_of_volunteers_not_at_event = in_x_not_in_y(
            x=all_volunteer_ids, y=volunteers_at_event_ids
        )

        return ListOfVolunteers.subset_from_list_of_ids(
            master_list_of_volunteers, ids_of_volunteers_not_at_event
        )

    def is_volunteer_already_at_event(self, event: Event, volunteer_id: str):
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )
        return list_of_volunteers_at_event.is_volunteer_already_at_event(volunteer_id)

    def mark_volunteer_as_skipped(
        self, event: Event, row_id: str, volunteer_index: int
    ):
        list_of_identified_volunteers_at_event = (
            self.load_list_of_identified_volunteers_at_event(event)
        )
        list_of_identified_volunteers_at_event.identified_as_processed_not_allocated(
            row_id=row_id, volunteer_index=volunteer_index
        )
        self.save_list_of_identified_volunteers_at_event(
            event=event, list_of_volunteers=list_of_identified_volunteers_at_event
        )

    def add_identified_volunteer(
        self, volunteer_id: str, event: Event, row_id: str, volunteer_index: int
    ):
        list_of_volunteers_identified = (
            self.load_list_of_identified_volunteers_at_event(event)
        )
        list_of_volunteers_identified.add(
            row_id=row_id, volunteer_index=volunteer_index, volunteer_id=volunteer_id
        )
        self.save_list_of_identified_volunteers_at_event(
            list_of_volunteers=list_of_volunteers_identified, event=event
        )

    def volunteer_for_this_row_and_index_already_identified(
        self, event: Event, row_id: str, volunteer_index: int
    ) -> bool:
        list_of_volunteers_identified = (
            self.load_list_of_identified_volunteers_at_event(event)
        )
        volunteer_id = (
            list_of_volunteers_identified.volunteer_id_given_row_id_and_index(
                row_id=row_id, volunteer_index=volunteer_index
            )
        )
        return volunteer_id is not missing_data

    def get_list_of_volunteers_at_event(self, event: Event) -> ListOfVolunteersAtEvent:
        list_of_volunteers_at_event = self.load_list_of_volunteers_with_ids_at_event(
            event
        )

        return ListOfVolunteersAtEvent(
            [
                DEPRECATE_VolunteerAtEvent.from_volunteer_and_voluteer_at_event_with_id(
                    volunteer=self.volunteer_data.volunteer_with_id(
                        volunteer_with_id_at_event.volunteer_id
                    ),
                    volunteer_at_event_with_id=volunteer_with_id_at_event,
                    event=event
                )
                for volunteer_with_id_at_event in list_of_volunteers_at_event
            ]
        )

    def load_list_of_identified_volunteers_at_event(
        self, event: Event
    ) -> ListOfIdentifiedVolunteersAtEvent:
        return self.data_api.get_list_of_identified_volunteers_at_event(event=event)

    def save_list_of_identified_volunteers_at_event(
        self, event: Event, list_of_volunteers: ListOfIdentifiedVolunteersAtEvent
    ):
        return self.data_api.save_list_of_identified_volunteers_at_event(
            list_of_volunteers=list_of_volunteers, event=event
        )

    def load_list_of_volunteers_with_ids_at_event(
        self, event: Event
    ) -> ListOfVolunteersAtEventWithId:
        return self.data_api.get_list_of_volunteers_at_event(event=event)

    def save_list_of_volunteers_at_event(
        self, event: Event, list_of_volunteers_at_event: ListOfVolunteersAtEventWithId
    ):
        self.data_api.save_list_of_volunteers_at_event(
            event=event, list_of_volunteers_at_event=list_of_volunteers_at_event
        )

    def sorted_list_of_all_volunteers(self, sort_by: str) -> ListOfVolunteers:
        return self.volunteer_data.get_sorted_list_of_volunteers(sort_by)

    @property
    def volunteer_data(self) -> VolunteerData:
        return VolunteerData(self.data_api)
