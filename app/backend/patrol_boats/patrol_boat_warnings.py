from typing import List

from app.backend.club_boats.people_with_club_dinghies_at_event import (
    get_dict_of_volunteers_and_club_dinghies_at_event,
)
from app.backend.events.event_warnings import (
    get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority,
    process_list_of_warnings_which_auto_clear,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.event_warnings import (
    ListOfEventWarnings,
    VOLUNTEER_QUALIFICATION,
    MISSING_DRIVER,
    DOUBLE_BOOKED,
)
from app.data_access.configuration.fixed import HIGH_PRIORITY
from app.objects.volunteers import ListOfVolunteers

from app.data_access.store.object_store import ObjectStore


from app.backend.volunteers.warnings import (
    remove_empty_values_in_warning_list,
    warn_on_volunteer_qualifications,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat

from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    load_list_of_patrol_boats_at_event,
    get_dict_of_patrol_boats_by_day_for_volunteer_at_event,
)
from app.backend.volunteers.skills import get_dict_of_existing_skills_for_volunteer


def process_all_warnings_for_patrol_boats(interface: abstractInterface, event: Event):
    warn_on_volunteer_qualifications(interface=interface, event=event)
    warn_on_pb2_drivers(interface=interface, event=event)
    warn_on_double_booking(interface=interface, event=event)


def warn_on_double_booking(interface: abstractInterface,  event: Event):
    list_of_warnings = []
    for day in event.days_in_event():
        list_of_warnings += warn_on_double_booking_on_day(interface.object_store, event, day)

    list_of_warnings = remove_empty_values_in_warning_list(list_of_warnings)

    process_list_of_warnings_which_auto_clear(
        interface=interface,
        event=event,
        list_of_warnings=list_of_warnings,
        category=DOUBLE_BOOKED,
        priority=HIGH_PRIORITY,
    )


def warn_on_double_booking_on_day(
    object_store: ObjectStore, event: Event, day: Day
) -> List[str]:
    dict_of_people_with_club_dinghies = get_dict_of_volunteers_and_club_dinghies_at_event(
        object_store=object_store, event=event
    )
    dict_of_voluteers_at_event_with_patrol_boats = (
        get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
            object_store=object_store, event=event
        )
    )
    volunteers_assigned_to_boat_and_day = dict_of_voluteers_at_event_with_patrol_boats.volunteers_assigned_to_any_boat_on_given_day(
        day=day
    )
    warnings = []
    for volunteer in volunteers_assigned_to_boat_and_day:
        if dict_of_people_with_club_dinghies.club_dinghys_for_person(
            volunteer
        ).has_any_dinghy_on_specific_day(day):
            warnings.append(
                "On %s, %s is rostered on a club sailing dinghy and a patrol boat"
                % (
                    day.name,
                    volunteer.name,
                )
            )

    return warnings


def warn_on_pb2_drivers(interface: abstractInterface,  event: Event):
    object_store=interface.object_store
    list_of_boats_at_event = load_list_of_patrol_boats_at_event(
        object_store=object_store, event=event
    )
    list_of_warnings = []
    for patrol_boat in list_of_boats_at_event:
        list_of_warnings += warn_on_pb2_drivers_for_boat(
            object_store=object_store, event=event, patrol_boat=patrol_boat
        )

    list_of_warnings = remove_empty_values_in_warning_list(list_of_warnings)

    process_list_of_warnings_which_auto_clear(
        interface=interface,
        event=event,
        list_of_warnings=list_of_warnings,
        category=MISSING_DRIVER,
        priority=HIGH_PRIORITY,
    )


def warn_on_pb2_drivers_for_boat(
    object_store: ObjectStore, event: Event, patrol_boat: PatrolBoat
) -> List[str]:
    list_of_warnings = [
        warn_on_pb2_drivers_for_boat_on_day(
            object_store=object_store, event=event, patrol_boat=patrol_boat, day=day
        )
        for day in event.days_in_event()
    ]

    return list_of_warnings


def warn_on_pb2_drivers_for_boat_on_day(
    object_store: ObjectStore, event: Event, patrol_boat: PatrolBoat, day: Day
) -> str:
    dict_of_voluteers_at_event_with_patrol_boats = (
        get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
            object_store=object_store, event=event
        )
    )
    volunteers_assigned_to_boat_and_day = (
        dict_of_voluteers_at_event_with_patrol_boats.volunteers_assigned_to_boat_on_day(
            patrol_boat=patrol_boat, day=day
        )
    )

    anyone_can_drive = any_volunteers_in_list_can_drive(
        object_store=object_store,
        list_of_volunteers=volunteers_assigned_to_boat_and_day,
    )
    if not anyone_can_drive:
        return "%s on %s has no PB2 qualified person on board" % (
            patrol_boat.name,
            day.name,
        )
    else:
        return ""


def any_volunteers_in_list_can_drive(
    object_store: ObjectStore, list_of_volunteers: ListOfVolunteers
) -> bool:
    for volunteer in list_of_volunteers:
        skills = get_dict_of_existing_skills_for_volunteer(
            object_store=object_store, volunteer=volunteer
        )
        if skills.can_drive_safety_boat:
            return True

    return False


def get_all_saved_warnings_for_patrol_boats(
    object_store: ObjectStore, event: Event
) -> ListOfEventWarnings:
    all_warnings = (
        get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority(
            object_store=object_store,
            event=event,
            list_of_categories=[VOLUNTEER_QUALIFICATION, MISSING_DRIVER, DOUBLE_BOOKED],
        )
    )

    return all_warnings
