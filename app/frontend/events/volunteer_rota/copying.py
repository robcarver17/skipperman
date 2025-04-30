from app.backend.rota.copying import (
    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days,
    copy_earliest_valid_role_for_volunteer,
)
from app.backend.rota.changes import (
    update_role_and_group_at_event_for_volunteer_on_all_days_when_available,
)
from app.backend.volunteers.volunteers_at_event import load_list_of_volunteers_at_event
from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_last_role_or_none_for_volunteer_at_previous_events,
)
from app.frontend.events.volunteer_rota.button_values import (
    from_previous_role_copy_button_to_volunteer,
    from_copyoverwrite_button_to_volunteer_and_day,
    from_copyfill_button_to_volunteer_and_day,
)

from app.frontend.events.volunteer_rota.button_values import (
    last_button_was_copy_previous_role,
    last_button_pressed_was_copyover_button,
    last_button_pressed_was_copyfill_button,
)

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface


def update_if_copy_button_pressed(interface: abstractInterface, copy_button: str):
    if last_button_was_copy_previous_role(copy_button):
        update_if_copy_previous_role_button_pressed(
            interface=interface, copy_button=copy_button
        )
    elif last_button_pressed_was_copyover_button(copy_button):
        update_if_individual_copy_overwrite_button_pressed(
            interface=interface, copy_button=copy_button
        )
    elif last_button_pressed_was_copyfill_button(copy_button):
        update_if_individual_copy_fill_button_pressed(
            interface=interface, copy_button=copy_button
        )
    else:
        raise Exception("can't handle copy button %s" % copy_button)


def update_if_individual_copy_overwrite_button_pressed(
    interface: abstractInterface, copy_button: str
):
    volunteer, day = from_copyoverwrite_button_to_volunteer_and_day(
        interface.object_store, copy_button
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
    volunteer, day = from_copyfill_button_to_volunteer_and_day(
        interface.object_store, copy_button
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
        object_store=interface.object_store, previous_role_copy_button_name=copy_button
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
        copy_earliest_valid_role_for_volunteer(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer,
            allow_overwrite=False,
        )


def update_if_copy_first_role_and_overwrite_button_pressed(
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(
        object_store=interface.object_store, event=event
    )
    for volunteer in list_of_volunteers_at_event:
        copy_earliest_valid_role_for_volunteer(
            object_store=interface.object_store,
            event=event,
            volunteer=volunteer,
            allow_overwrite=True,
        )
