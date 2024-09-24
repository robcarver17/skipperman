from app.OLD_backend.rota.volunteer_history import  get_last_role_for_volunteer_id
from app.OLD_backend.rota.volunteer_rota import copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days, \
    update_role_and_group_at_event_for_volunteer_on_all_days_when_available, load_list_of_volunteers_at_event, \
    copy_earliest_valid_role_to_all_empty_for_volunteer, copy_earliest_valid_role_and_overwrite_for_volunteer
from app.frontend.events.volunteer_rota.button_values import \
    from_previous_role_copy_button_to_volunteer_id, from_known_button_to_volunteer_at_event_and_day, \
    from_previous_role_copy_button_to_volunteer_at_event
from app.frontend.events.volunteer_rota.volunteer_rota_buttons import copy_all_roles_button, copy_all_first_role_button, \
    get_all_copy_previous_role_buttons, get_all_copy_overwrite_individual_role_buttons, \
    get_all_copy_fill_individual_role_buttons
from app.frontend.shared.events_state import get_event_from_state
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface


def update_if_copy_button_pressed(interface: abstractInterface, copy_button: str):
    if copy_all_roles_button.pressed(copy_button):
        update_if_copy_first_role_to_empty_roles_button_pressed(interface=interface)

    elif copy_all_first_role_button.pressed(copy_button):
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
    volunteer_at_event, day = from_known_button_to_volunteer_at_event_and_day(interface=interface, copy_button_text=copy_button)

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        interface=interface,
        volunteer_at_event=volunteer_at_event,
        day=day,
        allow_replacement=True,
    )


def update_if_individual_copy_fill_button_pressed(
    interface: abstractInterface, copy_button: str
):
    volunteer_at_event, day = from_known_button_to_volunteer_at_event_and_day(interface=interface, copy_button_text=copy_button)

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        interface=interface,
        volunteer_at_event=volunteer_at_event,
        day=day,
        allow_replacement=False,
    )


def update_if_copy_previous_role_button_pressed(
    interface: abstractInterface, copy_button: str
):
    volunteer_at_event = from_previous_role_copy_button_to_volunteer_at_event(interface=interface, previous_role_copy_button_name=copy_button)
    event = get_event_from_state(interface)
    previous_role_and_group = get_last_role_for_volunteer_id(
        data_layer=interface.data,
        volunteer=volunteer_at_event.volunteer,
         avoid_event=event
    )

    if previous_role_and_group.missing:
        return

    update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
        interface=interface,
        volunteer_at_event=volunteer_at_event,
        new_role_and_group=previous_role_and_group,
    )


def update_if_copy_first_role_to_empty_roles_button_pressed(
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = interface.cache.get_from_cache(load_list_of_volunteers_at_event,
        event=event)
    event = get_event_from_state(interface)
    for volunteer_at_event in list_of_volunteers_at_event:
        copy_earliest_valid_role_to_all_empty_for_volunteer(
            interface=interface, event=event, volunteer_at_event=volunteer_at_event
        )


def update_if_copy_first_role_and_overwrite_button_pressed(
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = interface.cache.get_from_cache(load_list_of_volunteers_at_event,
        event=event)
    event = get_event_from_state(interface)

    for volunteer_at_event in list_of_volunteers_at_event:
        copy_earliest_valid_role_and_overwrite_for_volunteer(

            interface=interface, event=event, volunteer_at_event=volunteer_at_event
        )
