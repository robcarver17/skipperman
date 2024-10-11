from app.objects.events import Event

from app.frontend.events.clothing.render_clothing import (
    size_field_name,
    colour_field_name,
    are_we_showing_only_committee,
)

from app.objects_OLD.clothing import CadetWithClothingAtEvent

from app.OLD_backend.clothing import (
    get_list_of_active_cadet_ids_with_clothing_at_event,
    change_clothing_size_for_cadet,
    change_colour_group_for_cadet,
    distribute_colour_groups_at_event,
    clear_colour_group_for_cadet,
)

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_interface import abstractInterface


def save_clothing_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    only_committee = are_we_showing_only_committee(interface)
    list_of_cadets_with_clothing = get_list_of_active_cadet_ids_with_clothing_at_event(
        interface=interface, event=event, only_committee=only_committee
    )

    for cadet_with_clothing in list_of_cadets_with_clothing:
        save_clothing_data_for_cadet(
            interface=interface, cadet_with_clothing=cadet_with_clothing, event=event
        )


def save_clothing_data_for_cadet(
    interface: abstractInterface,
    event: Event,
    cadet_with_clothing: CadetWithClothingAtEvent,
):
    cadet_id = cadet_with_clothing.cadet_id

    new_size = interface.value_from_form(size_field_name(cadet_id=cadet_id))
    new_colour = interface.value_from_form(colour_field_name(cadet_id=cadet_id))

    if not new_size == cadet_with_clothing.size:
        change_clothing_size_for_cadet(
            interface=interface, event=event, cadet_id=cadet_id, size=new_size
        )

    if not new_colour == cadet_with_clothing.colour:
        change_colour_group_for_cadet(
            interface=interface, event=event, cadet_id=cadet_id, colour=new_colour
        )


def distribute_colour_groups(interface: abstractInterface):
    event = get_event_from_state(interface)
    distribute_colour_groups_at_event(interface=interface, event=event)


def clear_all_colours(interface: abstractInterface):
    event = get_event_from_state(interface)
    only_committee = are_we_showing_only_committee(interface)
    list_of_cadets_with_clothing = get_list_of_active_cadet_ids_with_clothing_at_event(
        interface=interface, event=event, only_committee=only_committee
    )

    for cadet_with_clothing in list_of_cadets_with_clothing:
        clear_colour_group_for_cadet(
            interface=interface, event=event, cadet_id=cadet_with_clothing.cadet_id
        )
