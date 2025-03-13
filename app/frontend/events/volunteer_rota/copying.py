from app.backend.rota.copying import (
    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days,
    copy_earliest_valid_role_and_overwrite_for_volunteer,
    copy_earliest_valid_role_to_all_empty_for_volunteer,
)
from app.backend.rota.changes import (
    update_role_and_group_at_event_for_volunteer_on_all_days_when_available,
)
from app.backend.volunteers.volunteers_at_event import load_list_of_volunteers_at_event
from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_last_role_or_none_for_volunteer_at_previous_events,
)
from app.frontend.events.volunteer_rota.button_values import (
    from_known_button_to_volunteer_and_day,
    from_previous_role_copy_button_to_volunteer,
)
from app.frontend.events.volunteer_rota.volunteer_rota_buttons import (
    copy_all_roles_from_first_role_button,
    copy_and_overwrite_all_roles_from_first_role_button,
    get_all_copy_previous_role_buttons,
    get_all_copy_overwrite_individual_role_buttons,
    get_all_copy_fill_individual_role_buttons,
)
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface


def update_if_copy_button_pressed(interface: abstractInterface, copy_button: str):
    if copy_all_roles_from_first_role_button.pressed(copy_button):
        update_if_copy_first_role_to_empty_roles_button_pressed(interface=interface)

    elif copy_and_overwrite_all_roles_from_first_role_button.pressed(copy_button):
        update_if_copy_first_role_and_overwrite_button_pressed(interface=interface)

    elif copy_button in get_all_copy_previous_role_buttons(interface=interface):
        update_if_copy_previous_role_button_pressed(
            interface=interface, copy_button=copy_button
        )
    elif copy_button in get_all_copy_overwrite_individual_role_buttons(interface):
        update_if_individual_copy_overwrite_button_pressed(
            interface=interface, copy_button=copy_button
        )
    elif copy_button in get_all_copy_fill_individual_role_buttons(interface):
        update_if_individual_copy_fill_button_pressed(
            interface=interface, copy_button=copy_button
        )
    else:
        raise Exception("can't handle button %s" % copy_button)


def update_if_individual_copy_overwrite_button_pressed(
    interface: abstractInterface, copy_button: str
):
    volunteer, day = from_known_button_to_volunteer_and_day(
        interface=interface, copy_button_text=copy_button
    )
    event = get_event_from_state(interface)
    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        object_store=interface.object_store,
        volunteer=volunteer,
        day=day,
        event=event,
        allow_replacement=True,
    )


def update_if_individual_copy_fill_button_pressed(
    interface: abstractInterface, copy_button: str
):
    volunteer, day = from_known_button_to_volunteer_and_day(
        interface=interface, copy_button_text=copy_button
    )
    event = get_event_from_state(interface)
    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer,
        day=day,
        allow_replacement=False,
    )


def update_if_copy_previous_role_button_pressed(
    interface: abstractInterface, copy_button: str
):
    volunteer = from_previous_role_copy_button_to_volunteer(
        interface=interface, previous_role_copy_button_name=copy_button
    )
    event = get_event_from_state(interface)
    previous_role_and_group = get_last_role_or_none_for_volunteer_at_previous_events(
        object_store=interface.object_store, avoid_event=event, volunteer=volunteer
    )

    if previous_role_and_group is None:
        return

    if previous_role_and_group.is_unallocated:
        return

    update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer,
        new_role_and_group=previous_role_and_group,
    )


def update_if_copy_first_role_to_empty_roles_button_pressed(
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        object_store=interface.object_store, event=event
    )
    for volunteer in list_of_volunteers_at_event:
        copy_earliest_valid_role_to_all_empty_for_volunteer(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )


def update_if_copy_first_role_and_overwrite_button_pressed(
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        object_store=interface.object_store, event=event
    )
    for volunteer in list_of_volunteers_at_event:
        copy_earliest_valid_role_and_overwrite_for_volunteer(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )
