from typing import List, Union

from app.backend.patrol_boats.volunteers_patrol_boats_skills_and_roles_in_event import (
    get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats,
)
from app.backend.rota.changes import update_role_at_event_for_volunteer_on_day
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import (
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
)
from app.objects.exceptions import MISSING_FROM_FORM
from app.objects.volunteers import Volunteer

from app.backend.volunteers.skills import (
    get_dict_of_existing_skills_for_volunteer,
    add_boat_related_skill_for_volunteer,
    remove_boat_related_skill_for_volunteer,
)

from app.frontend.forms.swaps import is_ready_to_swap

from app.backend.patrol_boats.changes import (
    BoatDayVolunteer,
    NO_ADDITION_TO_MAKE,
    ListOfBoatDayVolunteer,
    add_list_of_new_boat_day_volunteer_allocations_to_data_reporting_conflicts,
    copy_across_boats_at_event,
    add_named_boat_to_event_with_no_allocation,
    remove_patrol_boat_and_all_associated_volunteers_from_event,
    delete_volunteer_from_patrol_boat_on_day_at_event,
)
from app.backend.rota.copying import (
    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days,
)
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.patrol_boats.elements_in_patrol_boat_table import (
    get_unique_list_of_volunteers_for_skills_checkboxes,
    is_volunteer_skill_checkbox_ticked,
)
from app.frontend.events.patrol_boats.patrol_boat_dropdowns import (
    TOP_ROW_OF_VOLUNTEER_DROPDOWN,
    from_allocation_dropdown_input_name_to_boat_and_day,
    from_selected_dropdown_to_volunteer,
    get_list_of_dropdown_names_for_adding_volunteers,
    ADD_BOAT_DROPDOWN,
    which_volunteer_role_selected_in_boat_allocation,
)
from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    from_delete_button_name_to_boat_name,
    list_of_delete_buttons_in_patrol_boat_table,
    from_volunter_remove_button_name_to_volunteer_and_day,
    get_all_remove_volunteer_button_names,
    get_button_type_day_volunteer_given_button_name,
)
from app.frontend.events.patrol_boats.copying import (
    COPY_BOAT_OVERWRITE,
    COPY_ROLE_OVERWRITE,
    COPY_BOTH_OVERWRITE,
    get_list_of_all_types_of_copy_buttons,
    COPY_ROLE_FILL,
    COPY_BOAT_FILL,
    COPY_BOTH_FILL,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface


def get_all_copy_boat_buttons_for_boat_allocation(interface: abstractInterface) -> list:
    event = get_event_from_state(interface)
    return get_list_of_all_types_of_copy_buttons(interface=interface, event=event)


def update_if_copy_button_pressed(interface: abstractInterface, copy_button: str):
    event = get_event_from_state(interface)
    copy_type, day, volunteer = get_button_type_day_volunteer_given_button_name(
        interface=interface, button_name=copy_button
    )

    if copy_type == COPY_BOAT_OVERWRITE:
        copy_boat = True
        copy_role = False
        overwrite = True
    elif copy_type == COPY_BOAT_FILL:
        copy_boat = True
        copy_role = False
        overwrite = False
    elif copy_type == COPY_ROLE_OVERWRITE:
        copy_boat = False
        copy_role = True
        overwrite = True
    elif copy_type == COPY_ROLE_FILL:
        copy_boat = False
        copy_role = True
        overwrite = False

    elif copy_type == COPY_BOTH_OVERWRITE:
        copy_boat = True
        copy_role = True
        overwrite = True
    elif copy_type == COPY_BOTH_FILL:
        copy_boat = True
        copy_role = True
        overwrite = False

    else:
        raise Exception("button type %s not recognised" % copy_type)

    if copy_boat:
        copy_across_boats_at_event(
            object_store=interface.object_store,
            day=day,
            volunteer=volunteer,
            event=event,
            allow_overwrite=overwrite,
        )

    if copy_role:
        copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer,
            day=day,
            allow_replacement=overwrite,
        )


def get_all_delete_buttons_for_patrol_boat_table(
    interface: abstractInterface,
) -> List[str]:
    event = get_event_from_state(interface)
    return list_of_delete_buttons_in_patrol_boat_table(interface=interface, event=event)


def get_all_delete_volunteer_buttons_for_patrol_boat_table(
    interface: abstractInterface,
) -> List[str]:
    event = get_event_from_state(interface)
    return get_all_remove_volunteer_button_names(interface=interface, event=event)


def update_if_delete_boat_button_pressed(
    interface: abstractInterface, delete_button: str
):
    patrol_boat_name = from_delete_button_name_to_boat_name(delete_button)
    event = get_event_from_state(interface)
    print("Deleting %s" % patrol_boat_name)
    try:
        remove_patrol_boat_and_all_associated_volunteers_from_event(
            object_store=interface.object_store,
            event=event,
            patrol_boat_name=patrol_boat_name,
        )
    except Exception as e:
        interface.log_error(
            "Error deleting patrol boat %s: %s" % (patrol_boat_name, str(e))
        )


def update_data_from_form_entries_in_patrol_boat_allocation_page(
    interface: abstractInterface,
):
    ## Any added volunteers
    update_skills_checkbox(interface)
    if is_ready_to_swap(interface):
        return
    else:
        update_role_dropdowns(interface)
        update_adding_volunteers_to_specific_boats_and_days(
            interface
        )  ## must come last or will confuse role and skills


def update_adding_volunteers_to_specific_boats_and_days(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_volunteer_additions_to_boats = get_list_of_volunteer_additions_to_boats(
        interface
    )
    list_of_volunteer_additions_to_boats = (
        list_of_volunteer_additions_to_boats.remove_no_additions()
    )

    add_list_of_new_boat_day_volunteer_allocations_to_data_reporting_conflicts(
        interface=interface,
        list_of_volunteer_additions_to_boats=list_of_volunteer_additions_to_boats,
        event=event,
    )


def get_list_of_volunteer_additions_to_boats(
    interface: abstractInterface,
) -> ListOfBoatDayVolunteer:
    event = get_event_from_state(interface)
    list_of_names = get_list_of_dropdown_names_for_adding_volunteers(
        interface=interface, event=event
    )
    list_of_updates = [
        get_boat_day_volunteer_for_dropdown_name_or_none(
            interface=interface, dropdown_name=dropdown_name
        )
        for dropdown_name in list_of_names
    ]
    list_of_volunteer_additions_to_boats = ListOfBoatDayVolunteer(list_of_updates)

    return list_of_volunteer_additions_to_boats


def get_boat_day_volunteer_for_dropdown_name_or_none(
    interface: abstractInterface, dropdown_name: str
) -> Union[BoatDayVolunteer, str]:
    selected_dropdown = interface.value_from_form(dropdown_name, default=MISSING_FROM_FORM)

    if selected_dropdown == TOP_ROW_OF_VOLUNTEER_DROPDOWN:
        return NO_ADDITION_TO_MAKE
    if selected_dropdown == MISSING_FROM_FORM:
        return NO_ADDITION_TO_MAKE


    boat, day = from_allocation_dropdown_input_name_to_boat_and_day(
        interface=interface, dropdown_input_name=dropdown_name
    )

    volunteer = from_selected_dropdown_to_volunteer(
        interface=interface, selected_dropdown=selected_dropdown
    )
    boat_day_volunteer = BoatDayVolunteer(boat=boat, day=day, volunteer=volunteer)

    return boat_day_volunteer


def update_skills_checkbox(interface: abstractInterface):
    event = get_event_from_state(interface)
    unique_volunteers = get_unique_list_of_volunteers_for_skills_checkboxes(
        object_store=interface.object_store, event=event
    )

    for volunteer in unique_volunteers:
        update_skills_checkbox_for_specific_volunteer(
            volunteer=volunteer, interface=interface
        )


def update_skills_checkbox_for_specific_volunteer(
    interface: abstractInterface, volunteer: Volunteer
):
    skills = get_dict_of_existing_skills_for_volunteer(
        object_store=interface.object_store, volunteer=volunteer
    )

    currently_has_boat_skill = skills.can_drive_safety_boat
    is_ticked = is_volunteer_skill_checkbox_ticked(
        interface=interface, volunteer_id=volunteer.id
    )

    if currently_has_boat_skill == is_ticked:
        return

    if is_ticked:
        add_boat_related_skill_for_volunteer(
            object_store=interface.object_store, volunteer=volunteer
        )
    else:
        remove_boat_related_skill_for_volunteer(
            object_store=interface.object_store, volunteer=volunteer
        )


def update_role_dropdowns(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_volunteers = (
        get_list_of_volunteers_at_event_with_skills_and_roles_and_patrol_boats(
            object_store=interface.object_store, event=event
        )
    )

    for day in event.days_in_event():
        volunteers_on_boat_on_day = all_volunteers.assigned_to_any_boat_on_day(day)
        for volunteer_on_boat in volunteers_on_boat_on_day:
            try:
                update_role_dropdown_for_volunteer_on_day(
                    interface=interface, volunteer_on_boat=volunteer_on_boat
                )
            except Exception as e:
                interface.log_error(
                    "Couldn't update volunteer role for %s on day %s - perhaps a conflicting change was made? Error code %s"
                    % (volunteer_on_boat.volunteer.name, day.name, str(e))
                )


def update_role_dropdown_for_volunteer_on_day(
    interface: abstractInterface,
    volunteer_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
):
    volunteer_id = volunteer_on_boat.volunteer.id
    day = volunteer_on_boat.day

    role_selected = which_volunteer_role_selected_in_boat_allocation(
        interface=interface, volunteer_id=volunteer_id, day=day
    )
    current_role = volunteer_on_boat.role_and_group.role

    if role_selected == current_role:
        return

    update_role_at_event_for_volunteer_on_day(
        object_store=interface.object_store,
        event=volunteer_on_boat.event,
        volunteer=volunteer_on_boat.volunteer,
        day=day,
        new_role=role_selected,
        remove_power_boat_if_deleting_role=False
    )


def update_adding_boat(interface: abstractInterface):
    event = get_event_from_state(interface)
    name_of_boat_added = interface.value_from_form(ADD_BOAT_DROPDOWN)

    try:
        add_named_boat_to_event_with_no_allocation(
            object_store=interface.object_store,
            name_of_boat_added=name_of_boat_added,
            event=event,
        )
    except Exception as e:
        interface.log_error(
            "Can't add boat %s, error %s" % (name_of_boat_added, str(e))
        )


def update_if_delete_volunteer_button_pressed(
    interface: abstractInterface, delete_button: str
):
    event = get_event_from_state(interface)
    volunteer, day = from_volunter_remove_button_name_to_volunteer_and_day(
        interface=interface, button_name=delete_button
    )

    try:
        delete_volunteer_from_patrol_boat_on_day_at_event(
            object_store=interface.object_store,
            event=event,
            day=day,
            volunteer=volunteer,
        )
    except Exception as e:
        interface.log_error(
            "Couldn't remove volunteer %s from rescue boat on day %s - perhaps a conflicting change was made? Error: %s"
            % (volunteer.name, day.name, str(e))
        )
