from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    ListOfBoatDayVolunteer,
    BoatDayVolunteer,
)

from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat
from app.objects.volunteers import Volunteer


def add_list_of_new_boat_day_volunteer_allocations_to_data_reporting_conflicts(
    interface: abstractInterface,
    list_of_volunteer_additions_to_boats: ListOfBoatDayVolunteer,
    event: Event,
) -> List[str]:
    messages = []
    for boat_day_volunteer in list_of_volunteer_additions_to_boats:
        try:
            add_new_boat_day_volunteer_allocation(
                interface=interface,
                event=event,
                boat_day_volunteer=boat_day_volunteer,
            )
        except Exception as e:
            messages.append(
                "Can't add volunteer %s to boat %s on day %s; error %s"
                % (
                    boat_day_volunteer.volunteer.name,
                    boat_day_volunteer.boat.name,
                    boat_day_volunteer.day.name,
                    str(e),
                )
            )

    return messages


def add_new_boat_day_volunteer_allocation(
    interface: abstractInterface, event: Event, boat_day_volunteer: BoatDayVolunteer
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.add_new_boat_day_volunteer_allocation,
        event_id=event.id,
        patrol_boat_id=boat_day_volunteer.boat.id,
        day=boat_day_volunteer.day,
        volunteer_id=boat_day_volunteer.volunteer.id,
    )


from app.backend.patrol_boats.list_of_patrol_boats import from_patrol_boat_name_to_boat


def add_named_boat_to_event_with_no_allocation(
    interface: abstractInterface, name_of_boat_added: str, event: Event
):
    patrol_boat = from_patrol_boat_name_to_boat(
        object_store=interface.object_store, boat_name=name_of_boat_added
    )
    for day in event.days_in_event():
        add_patrol_boat_to_event_with_no_allocation_on_day(
            interface=interface, boat_added=patrol_boat, event=event, day=day
        )


def add_patrol_boat_to_event_with_no_allocation_on_day(
    interface: abstractInterface, event: Event, boat_added: PatrolBoat, day: Day
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.add_unallocated_boat_on_day,
        event_id=event.id,
        patrol_boat_id=boat_added.id,
        day=day,
    )


def remove_patrol_boat_and_all_associated_volunteers_from_event(
    interface: abstractInterface, event: Event, patrol_boat_name: str
):
    patrol_boat = from_patrol_boat_name_to_boat(
        object_store=interface.object_store, boat_name=patrol_boat_name
    )
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.remove_patrol_boat_and_all_associated_volunteers_from_event,
        event_id=event.id,
        patrol_boat_id=patrol_boat.id,
    )


def delete_volunteer_from_patrol_boat_on_day_at_event(
    interface: abstractInterface, event: Event, volunteer: Volunteer, day: Day
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.delete_volunteer_from_patrol_boat_on_day_at_event,
        event_id=event.id,
        volunteer_id=volunteer.id,
        day=day,
    )


def delete_volunteer_from_patrol_boat_on_all_days_of_event(
    interface: abstractInterface, event: Event, volunteer: Volunteer
):
    for day in event.days_in_event():
        delete_volunteer_from_patrol_boat_on_day_at_event(
            interface=interface, event=event, volunteer=volunteer, day=day
        )
