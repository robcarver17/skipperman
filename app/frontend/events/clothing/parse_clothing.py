from typing import Tuple

from app.objects.cadets import Cadet

from app.objects.events import Event

from app.frontend.events.clothing.render_clothing import (
    size_field_name,
    colour_field_name,
    are_we_showing_only_committee,
)

from app.objects.clothing import ClothingAtEvent
from app.backend.clothing.dict_of_clothing_for_event import (
    change_clothing_size_for_cadet,
    change_colour_group_for_cadet,
    clear_colour_group_for_cadet,
    distribute_colour_groups_at_event,
    NotEnoughColours,
)
from app.backend.clothing.active_cadets_with_clothing import (
    get_dict_of_active_cadets_with_clothing_at_event,
)

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import MISSING_FROM_FORM


def save_clothing_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    only_committee = are_we_showing_only_committee(interface)
    dict_of_cadets_with_clothing = get_dict_of_active_cadets_with_clothing_at_event(
        object_store=interface.object_store, event=event, only_committee=only_committee
    )

    for cadet, clothing in dict_of_cadets_with_clothing.items():
        save_clothing_data_for_cadet(
            interface=interface, event=event, cadet=cadet, clothing=clothing
        )


def save_clothing_data_for_cadet(
    interface: abstractInterface, event: Event, cadet: Cadet, clothing: ClothingAtEvent
):
    new_size, new_colour = get_size_and_colour_from_form(
        interface=interface, cadet=cadet
    )
    if MISSING_FROM_FORM in [new_colour, new_size]:
        interface.log_error("Can't update clothing for %s as missing values" % str(cadet))
        return

    if not new_size == clothing.size:
        change_clothing_size_for_cadet(
            object_store=interface.object_store, event=event, cadet=cadet, size=new_size
        )

    if not new_colour == clothing.colour:
        change_colour_group_for_cadet(
            object_store=interface.object_store,
            event=event,
            cadet=cadet,
            colour=new_colour,
        )


def get_size_and_colour_from_form(
    interface: abstractInterface, cadet: Cadet
) -> Tuple[str, str]:
    cadet_id = cadet.id

    new_size = interface.value_from_form(size_field_name(cadet_id=cadet_id), default=MISSING_FROM_FORM)
    new_colour = interface.value_from_form(colour_field_name(cadet_id=cadet_id), default=MISSING_FROM_FORM)

    return new_size, new_colour


def distribute_colour_groups(interface: abstractInterface):
    event = get_event_from_state(interface)
    try:
        distribute_colour_groups_at_event(
            object_store=interface.object_store, event=event
        )
    except NotEnoughColours as error:
        interface.log_error(str(error))


def clear_all_colours(interface: abstractInterface):
    event = get_event_from_state(interface)
    only_committee = are_we_showing_only_committee(interface)
    dict_of_cadets_with_clothing = get_dict_of_active_cadets_with_clothing_at_event(
        object_store=interface.object_store, event=event, only_committee=only_committee
    )

    for cadet in dict_of_cadets_with_clothing.list_of_cadets:
        clear_colour_group_for_cadet(
            object_store=interface.object_store, event=event, cadet=cadet
        )
