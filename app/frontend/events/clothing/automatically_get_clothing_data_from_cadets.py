from app.objects.abstract_objects.abstract_form import NewForm
from app.objects.cadets import Cadet

from app.objects.composed.cadets_at_event_with_registration_data import (
    CadetRegistrationData,
)

from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
)

from app.backend.clothing.dict_of_clothing_for_event import (
    is_cadet_already_at_event_with_clothing,
    add_new_cadet_with_clothing_to_event,
    remove_clothing_for_cadet_at_event,
)


from app.data_access.configuration.field_list import CADET_T_SHIRT_SIZE
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.frontend.shared.events_state import get_event_from_state


from app.objects.events import Event
from app.frontend.form_handler import initial_state_form


def display_call_to_update_cadet_clothing_at_event_during_import(
    interface: abstractInterface,
) -> NewForm:
    event = get_event_from_state(interface)
    dict_of_cadets_at_event_with_registration_data = (
        get_dict_of_cadets_with_registration_data(
            object_store=interface.object_store, event=event
        )
    )

    for (
        cadet,
        registration_data,
    ) in dict_of_cadets_at_event_with_registration_data.items():
        process_update_to_cadet_clothing_data(
            interface=interface,
            event=event,
            cadet=cadet,
            registration_data=registration_data,
        )
    interface.flush_cache_to_store()
    return return_to_controller(interface)


def return_to_controller(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_call_to_update_cadet_clothing_at_event_during_import
    )


def post_call_to_update_cadet_clothing_at_event_during_import(
    interface: abstractInterface,
) -> NewForm:
    interface.log_error(
        "Serious error: should never get to post_call_to_update_cadet_clothing_at_event_during_import"
    )
    return initial_state_form()


def process_update_to_cadet_clothing_data(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    registration_data: CadetRegistrationData,
):
    cadet_already_at_event = is_cadet_already_at_event_with_clothing(
        object_store=interface.object_store, event=event, cadet=cadet
    )

    if cadet_already_at_event:
        return process_update_to_existing_cadet_with_clothing(
            interface=interface,
            event=event,
            cadet=cadet,
            registration_data=registration_data,
        )

    else:
        return process_update_to_cadet_new_to_event_with_clothing(
            event=event,
            cadet=cadet,
            interface=interface,
            registration_data=registration_data,
        )


def process_update_to_existing_cadet_with_clothing(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    registration_data: CadetRegistrationData,
):
    cadet_is_active = registration_data.active
    if cadet_is_active:
        return

    remove_clothing_for_cadet_at_event(
        object_store=interface.object_store, event=event, cadet=cadet
    )

    interface.log_error(
        "Cadet %s is no longer active at event, removing clothing preferences"
    )


def process_update_to_cadet_new_to_event_with_clothing(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    registration_data: CadetRegistrationData,
):
    clothing_size_from_registration = registration_data.data_in_row.get_item(
        CADET_T_SHIRT_SIZE, None
    )
    if clothing_size_from_registration is None:
        ## probably no clothing at event
        return

    add_new_cadet_with_clothing_to_event(
        object_store=interface.object_store,
        event=event,
        cadet=cadet,
        size=clothing_size_from_registration,
    )
