from typing import List

from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.frontend.events.group_allocation.render_allocation_form import (
    get_list_of_all_cadets_with_event_data,
)
from app.frontend.events.group_allocation.store_state import (
    no_day_set_in_state,
    get_day_from_state_or_none,
)

from app.objects.day_selectors import Day

from app.frontend.events.group_allocation.input_fields import (
    NOTES,
    ALLOCATION,
    CLUB_BOAT,
    PARTNER,
    BOAT_CLASS,
    SAIL_NUMBER,
    cadet_id_from_cadet_available_buttons,
    get_cadet_id_given_remove_partner_button_name,
)
from app.objects.events import Event

from app.frontend.forms.form_utils import (
    input_name_from_column_name_and_cadet_id,
    get_availablity_from_form,
)
from app.backend.boat_classes.update_boat_information import (
    CadetWithDinghySailNumberBoatClassAndPartner,
    update_boat_class_sail_number_group_club_dinghy_and_partner_for_cadets_at_event,
)
from app.objects.partners import NOT_ALLOCATED_STR
from app.objects.utils import print_list
from app.backend.registration_data.update_cadets_at_event import (
    update_notes_for_existing_cadet_at_event,
)
from app.backend.cadets_at_event.update_status_and_availability_of_cadets_at_event import (
    update_availability_of_existing_cadet_at_event_and_return_messages,
    make_cadet_available_on_day,
)

from app.frontend.events.constants import (
    ATTENDANCE,
)
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.exceptions import MISSING_FROM_FORM


def update_data_given_allocation_form(interface: abstractInterface):
    event = get_event_from_state(interface)

    list_of_cadets = get_list_of_all_cadets_with_event_data(interface=interface)
    for cadet in list_of_cadets:
        update_attendance_data_for_cadet_in_form(interface=interface, cadet=cadet)
        get_cadet_notes_for_row_in_form_and_alter_registration_data(
            interface=interface,
            event=event,
            cadet=cadet,
        )

    ## has to be done in one go because of swaps
    update_boat_class_sail_number_group_club_boat_and_partner_for_all_cadets_in_form(
        interface=interface, list_of_cadets=list_of_cadets
    )


def update_attendance_data_for_cadet_in_form(
    interface: abstractInterface, cadet: Cadet
):
    event = get_event_from_state(interface)
    new_availability = get_availablity_from_form(
        interface=interface,
        input_name=input_name_from_column_name_and_cadet_id(
            ATTENDANCE, cadet_id=cadet.id
        ),
        event=event,
    )

    list_of_messages = (
        update_availability_of_existing_cadet_at_event_and_return_messages(
            object_store=interface.object_store,
            event=event,
            new_availabilty=new_availability,
            cadet=cadet,
        )
    )

    for message in list_of_messages:
        interface.log_error(message)


def get_cadet_notes_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    cadet: Cadet,
    event: Event,
):
    new_notes = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(column_name=NOTES, cadet_id=cadet.id)
    )
    update_notes_for_existing_cadet_at_event(
        object_store=interface.object_store,
        event=event,
        cadet=cadet,
        new_notes=new_notes,
    )


def update_boat_class_sail_number_group_club_boat_and_partner_for_all_cadets_in_form(
    interface: abstractInterface, list_of_cadets: ListOfCadets
):
    event = get_event_from_state(interface)
    list_of_updates = get_list_of_updates(
        interface=interface, list_of_cadets=list_of_cadets
    )
    update_boat_class_sail_number_group_club_boat_and_partner_for_all_cadets_given_update_list(
        interface=interface,
        event=event,
        list_of_updates=list_of_updates
    )


def get_list_of_updates(
    interface: abstractInterface, list_of_cadets: ListOfCadets
) -> List[CadetWithDinghySailNumberBoatClassAndPartner]:
    list_of_updates = []
    for cadet in list_of_cadets:
        update_for_cadet = get_update_for_cadet(interface=interface, cadet=cadet)
        list_of_updates.append(update_for_cadet)

    return list_of_updates


def get_update_for_cadet(
    interface: abstractInterface, cadet: Cadet
) -> CadetWithDinghySailNumberBoatClassAndPartner:
    sail_number = str(
        interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                cadet_id=cadet.id,
                column_name=SAIL_NUMBER,
            ),
            default=MISSING_FROM_FORM,
        )
    )
    boat_class_name = str(
        interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                cadet_id=cadet.id, column_name=BOAT_CLASS
            ),
            default=MISSING_FROM_FORM,
        )
    )
    two_handed_partner_as_str = str(
        interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                cadet_id=cadet.id, column_name=PARTNER
            ),
            default=MISSING_FROM_FORM,
        )
    )
    ## remove asterixes
    two_handed_partner_as_str = remove_asterixes(two_handed_partner_as_str)

    club_boat_name = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(
            cadet_id=cadet.id,
            column_name=CLUB_BOAT,
        ),
        default=MISSING_FROM_FORM,
    )

    group_name = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(
            column_name=ALLOCATION, cadet_id=cadet.id
        ),
        default=MISSING_FROM_FORM,
    )

    return CadetWithDinghySailNumberBoatClassAndPartner(
        cadet=cadet,
        sail_number=sail_number,
        boat_class_name=boat_class_name,
        two_handed_partner_cadet_as_str=two_handed_partner_as_str,
        club_boat_name=club_boat_name,
        group_name=group_name,
    )


def remove_asterixes(field_value: str) -> str:
    return field_value.replace("*", "")


def update_boat_class_sail_number_group_club_boat_and_partner_for_all_cadets_given_update_list( interface: abstractInterface, event: Event, list_of_updates: List[CadetWithDinghySailNumberBoatClassAndPartner]):
    if no_day_set_in_state(interface):
        list_of_days = event.days_in_event()
    else:
        day = get_day_from_state_or_none(interface)
        list_of_days = [day]

    update_boat_class_sail_number_group_club_boat_and_partner_for_all_cadets_in_form_across_days(
        interface=interface, event=event, list_of_updates=list_of_updates, list_of_days = list_of_days
    )



def update_boat_class_sail_number_group_club_boat_and_partner_for_all_cadets_in_form_across_days(
    interface: abstractInterface, event: Event, list_of_updates: List[CadetWithDinghySailNumberBoatClassAndPartner], list_of_days: List[Day]
):

    for day in list_of_days:
        update_boat_class_sail_number_group_club_dinghy_and_partner_for_cadets_at_event(
            object_store=interface.object_store,
            event=event,
            list_of_updates=list_of_updates,
            day=day,
        )


def make_cadet_available_on_current_day(
    interface: abstractInterface, add_availability_button_name: str
):
    day = get_day_from_state_or_none(interface)
    if day is None:
        interface.log_error(
            "Can't make cadet available on day when no day set - this shouldn't happen contact support"
        )

    cadet_id = cadet_id_from_cadet_available_buttons(add_availability_button_name)
    event = get_event_from_state(interface)
    cadet = get_cadet_from_id(object_store=interface.object_store, cadet_id=cadet_id)

    make_cadet_available_on_day(
        object_store=interface.object_store, event=event, cadet=cadet, day=day
    )
    interface.flush_cache_to_store()

def remove_partnership_for_cadet_from_group_allocation_button(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    cadet_id = get_cadet_id_given_remove_partner_button_name(last_button)
    event = get_event_from_state(interface)
    cadet = get_cadet_from_id(object_store=interface.object_store, cadet_id=cadet_id)
    day = get_day_from_state_or_none(interface)
    update = get_pseudo_update_to_remove_partner_from_cadet(interface=interface, event=event, cadet=cadet)

    list_of_updates = [update]

    update_boat_class_sail_number_group_club_boat_and_partner_for_all_cadets_given_update_list(interface=interface,
                                                                                               event=event,
                                                                                               list_of_updates=list_of_updates)

def get_pseudo_update_to_remove_partner_from_cadet(interface: abstractInterface, event: Event, cadet: Cadet) -> CadetWithDinghySailNumberBoatClassAndPartner:
    update = get_update_for_cadet(interface, cadet)
    update.two_handed_partner_cadet_as_str = NOT_ALLOCATED_STR

    return update