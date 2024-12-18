from dataclasses import dataclass
from typing import List

from app.backend.registration_data.volunteer_registration_data import \
    get_dict_of_registration_data_for_volunteers_at_event

from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import \
    get_dict_of_volunteers_with_roles_and_groups_at_event

from app.objects.exceptions import arg_not_passed

from app.OLD_backend.data.patrol_boats import PatrolBoatsData
from app.data_access.store.object_store import ObjectStore

from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import \
    get_dict_of_patrol_boats_by_day_for_volunteer_at_event, update_dict_of_patrol_boats_by_day_for_volunteer_at_event

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import \
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoats

from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat
from app.objects.volunteers import Volunteer


@dataclass
class BoatDayVolunteer:
    boat: PatrolBoat
    day: Day
    volunteer: Volunteer


NO_ADDITION_TO_MAKE = "No addition to make"


class ListOfBoatDayVolunteer(list):
    def __init__(self, input: List[BoatDayVolunteer]):
        super().__init__(input)

    def remove_no_additions(self):
        return ListOfBoatDayVolunteer(
            [bdv for bdv in self if not bdv is NO_ADDITION_TO_MAKE]
        )


def add_list_of_new_boat_day_volunteer_allocations_to_data_reporting_conflicts(
    interface: abstractInterface,
    list_of_volunteer_additions_to_boats: ListOfBoatDayVolunteer,
    event: Event,
):

    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(object_store=interface.object_store,
                                                                              event=event)

    for boat_day_volunteer in list_of_volunteer_additions_to_boats:
        try:
            patrol_boat_data.add_volunteer_with_boat(
                volunteer=boat_day_volunteer.volunteer,
                patrol_boat = boat_day_volunteer.boat,
                day = boat_day_volunteer.day
            )
        except Exception as e:
            interface.log_error(
                "Can't add volunteer %s to boat %s on day %s; error %s"
                % (
                    boat_day_volunteer.volunteer.name,
                    boat_day_volunteer.boat.name,
                    boat_day_volunteer.day.name,
                    str(e),
                )
            )

    update_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        dict_of_volunteers_at_event_with_patrol_boats=patrol_boat_data,
        object_store=interface.object_store
    )


def copy_across_earliest_allocation_of_boats_at_event(
    object_store: ObjectStore, volunteer_with_boat_data: VolunteerAtEventWithSkillsAndRolesAndPatrolBoats,
        allow_overwrite: bool
):
    earliest_day = earliest_day_with_boat_for_volunteer_or_none(
        volunteer_with_boat_data
    )
    if earliest_day is None:
        return

    copy_across_boats_at_event(
        object_store=object_store,
        event = volunteer_with_boat_data.event,
        volunteer = volunteer_with_boat_data.volunteer,
        volunteer_availablility_at_event = volunteer_with_boat_data.availability,
    day=earliest_day,
        allow_overwrite=allow_overwrite,
    )


def copy_across_boats_at_event(
    object_store: ObjectStore,
        event: Event,
    volunteer: Volunteer,
    day: Day,
        allow_overwrite: bool,
        volunteer_availablility_at_event: DaySelector = arg_not_passed,
):
    if volunteer_availablility_at_event is arg_not_passed:
        registration_data_for_volunteers_at_event  = get_dict_of_registration_data_for_volunteers_at_event(
            object_store=object_store,
            event=event
        )
        volunteer_availablility_at_event = registration_data_for_volunteers_at_event.get_data_for_volunteer(volunteer).availablity

    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(object_store=object_store,
                                                                              event=event)

    patrol_boat_data.copy_across_boats_at_event(
        volunteer=volunteer,
        volunteer_availablility_at_event=volunteer_availablility_at_event,
        day=day,
        allow_overwrite=allow_overwrite
    )

    update_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        dict_of_volunteers_at_event_with_patrol_boats=patrol_boat_data,
        object_store=object_store
    )


def earliest_day_with_boat_for_volunteer_or_none(
    volunteer_with_boat_data: VolunteerAtEventWithSkillsAndRolesAndPatrolBoats
) -> Day:
    for day in volunteer_with_boat_data.event.weekdays_in_event():
        if volunteer_with_boat_data.patrol_boat_by_day.on_any_patrol_boat_on_given_day(day):
            return day

    return None


from app.backend.patrol_boats.list_of_patrol_boats import from_patrol_boat_name_to_boat

def add_named_boat_to_event_with_no_allocation(
    object_store: ObjectStore, name_of_boat_added: str, event: Event
):
    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(object_store=object_store,
                                                                              event=event)

    patrol_boat = from_patrol_boat_name_to_boat(object_store=object_store, boat_name=name_of_boat_added)

    patrol_boat_data.add_boat_to_event_with_no_allocation(patrol_boat)
    update_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        dict_of_volunteers_at_event_with_patrol_boats=patrol_boat_data,
        object_store=object_store
    )


def remove_patrol_boat_and_all_associated_volunteers_from_event(
    object_store: ObjectStore, event: Event, patrol_boat_name: str
):
    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(object_store=object_store,
                                                                              event=event)

    patrol_boat = from_patrol_boat_name_to_boat(object_store=object_store, boat_name=patrol_boat_name)

    patrol_boat_data.remove_patrol_boat_and_all_associated_volunteers_from_event(patrol_boat)
    update_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        dict_of_volunteers_at_event_with_patrol_boats=patrol_boat_data,
        object_store=object_store
    )


def delete_volunteer_from_patrol_boat_on_day_at_event(
    object_store: ObjectStore,
        event: Event,
        volunteer: Volunteer,
        day: Day
):
    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(object_store=object_store,
                                                                              event=event)

    patrol_boat_data.delete_patrol_boat_for_volunteer_on_day(volunteer=volunteer, day=day)

    update_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        dict_of_volunteers_at_event_with_patrol_boats=patrol_boat_data,
        object_store=object_store
    )
