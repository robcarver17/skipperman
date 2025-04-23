from app.backend.patrol_boats.changes import (
    copy_across_earliest_allocation_of_boats_at_event, copy_across_boats_at_event,
)
from app.backend.patrol_boats.volunteers_patrol_boats_skills_and_roles_in_event import (
    get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats,
)
from app.backend.rota.copying import (
    copy_earliest_valid_role_for_volunteer,
    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days,
)

from app.frontend.events.patrol_boats.copy_buttons import     from_copy_button_type_to_copy_parameters

from app.frontend.events.patrol_boats.patrol_boat_buttons import get_day_and_volunteer_given_button_of_type
from app.frontend.shared.buttons import get_type_of_button_pressed

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_interface import abstractInterface


def update_if_copy_individual_button_pressed(interface: abstractInterface, copy_button: str):
    event = get_event_from_state(interface)
    copy_type = get_type_of_button_pressed(copy_button)
    day, volunteer = get_day_and_volunteer_given_button_of_type(
        interface=interface, button_name=copy_button,
        button_type=copy_type
    )

    copy_parameters = from_copy_button_type_to_copy_parameters(copy_type)

    if copy_parameters.copy_boat:
        copy_across_boats_at_event(
            object_store=interface.object_store,
            day=day,
            volunteer=volunteer,
            event=event,
            allow_overwrite=copy_parameters.overwrite,
        )

    if copy_parameters.copy_role:
        copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer,
            day=day,
            allow_replacement=copy_parameters.overwrite,
        )



def copy_across_all_boats(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=False,
        )


def overwrite_allocation_across_all_boats(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=True,
        )


def copy_across_all_boats_and_roles(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=False,
        )
        copy_earliest_valid_role_for_volunteer(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer_with_boat_data.volunteer,
            allow_overwrite=False
        )


def overwrite_copy_across_all_boats_and_roles(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers_on_boats = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )
    for volunteer_with_boat_data in all_volunteers_on_boats:
        copy_across_earliest_allocation_of_boats_at_event(
            object_store=interface.object_store,
            volunteer_with_boat_data=volunteer_with_boat_data,
            allow_overwrite=True,
        )
        copy_earliest_valid_role_for_volunteer(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer_with_boat_data.volunteer,
            allow_overwrite=True
        )


