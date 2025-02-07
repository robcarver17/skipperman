from typing import List

from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.backend.events.list_of_events import get_list_of_events
from app.backend.groups.cadets_with_groups_at_event import (
    add_or_upate_group_for_cadet_on_day_if_cadet_available_on_day,
)
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
    SAIL_NUMBER, cadet_id_from_cadet_available_buttons,
)
from app.objects.events import Event

from app.frontend.forms.form_utils import (
    input_name_from_column_name_and_cadet_id,
    get_availablity_from_form,
)
from app.backend.boat_classes.update_boat_information import (
    CadetWithDinghyInputs,
    update_boat_info_for_cadets_at_event,
)
from app.backend.club_boats.cadets_with_club_dinghies_at_event import (
    update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available,
)
from app.backend.registration_data.update_cadets_at_event import (
    update_notes_for_existing_cadet_at_event,
)
from app.backend.cadets_at_event.update_status_and_availability_of_cadets_at_event import (
    update_availability_of_existing_cadet_at_event_and_return_messages, make_cadet_available_on_day,
)

from app.frontend.events.constants import (
    ATTENDANCE,
)
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet, ListOfCadets


def update_data_given_allocation_form(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_cadets = get_list_of_all_cadets_with_event_data(interface=interface)
    for cadet in list_of_cadets:
        do_group_allocation_for_cadet_at_event(
            interface=interface,
            cadet=cadet,
        )
        update_attendance_data_for_cadet_in_form(interface=interface, cadet=cadet)
        update_club_boat_for_cadet_in_form(interface=interface, cadet=cadet)
        get_cadet_notes_for_row_in_form_and_alter_registration_data(
            interface=interface,
            event=event,
            cadet=cadet,
        )

    ## has to be done in one go because of swaps
    update_boat_info_for_all_cadets_in_form(
        interface=interface, list_of_cadets=list_of_cadets
    )


def do_group_allocation_for_cadet_at_event(
    cadet: Cadet,
    interface: abstractInterface,
):
    if no_day_set_in_state(interface):
        do_allocation_for_cadet_at_event_across_days(cadet=cadet, interface=interface)
    else:
        day = get_day_from_state_or_none(interface)
        do_allocation_for_cadet_at_event_on_day(
            interface=interface,
            cadet=cadet,
            day=day,
        )


from app.backend.groups.list_of_groups import get_group_with_name


def do_allocation_for_cadet_at_event_on_day(
    cadet: Cadet,
    day: Day,
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    try:
        allocation_str = interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                column_name=ALLOCATION, cadet_id=cadet.id
            )
        )
        print("Allocation %s for cadet %s" % (allocation_str, str(cadet)))
    except Exception as e:
        print(
            "No allocation available on day for %s, probably because not available today"
            % cadet.name
        )
        return

    chosen_group = get_group_with_name(
        object_store=interface.object_store, group_name=allocation_str
    )

    add_or_upate_group_for_cadet_on_day_if_cadet_available_on_day(
        object_store=interface.object_store,
        event=event,
        cadet=cadet,
        day=day,
        group=chosen_group,
    )


def do_allocation_for_cadet_at_event_across_days(
    cadet: Cadet,
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    try:
        allocation_str = interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                column_name=ALLOCATION, cadet_id=cadet.id
            )
        )
        print("Allocation %s for cadet %s" % (allocation_str, str(cadet)))
    except Exception as e:
        print(
            "No allocation available for %s, probably because can't be edited"
            % cadet.name
        )
        return

    chosen_group = get_group_with_name(
        object_store=interface.object_store, group_name=allocation_str
    )

    for day in event.days_in_event():
        ## Won't update cadets who aren't available on a given day
        add_or_upate_group_for_cadet_on_day_if_cadet_available_on_day(
            object_store=interface.object_store,
            event=event,
            cadet=cadet,
            day=day,
            group=chosen_group,
        )


def update_attendance_data_for_cadet_in_form(
    interface: abstractInterface, cadet: Cadet
):
    event = get_event_from_state(interface)
    try:
        new_availability = get_availablity_from_form(
            interface=interface,
            input_name=input_name_from_column_name_and_cadet_id(
                ATTENDANCE, cadet_id=cadet.id
            ),
            event=event,
        )
    except Exception as e:
        print("Error %s whilst updating attendance for %s" % (str(e), cadet.name))
        return

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


def update_club_boat_for_cadet_in_form(interface: abstractInterface, cadet: Cadet):
    event = get_event_from_state(interface)
    if no_day_set_in_state(interface):
        update_club_boat_for_cadet_across_days(
            interface=interface, cadet=cadet, event=event
        )
    else:
        day = get_day_from_state_or_none(interface)
        update_club_boat_for_cadet_on_day_in_form(
            interface=interface, event=event, cadet=cadet, day=day
        )


def update_club_boat_for_cadet_on_day_in_form(
    interface: abstractInterface, event: Event, day: Day, cadet: Cadet
):
    try:
        boat_name = interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                cadet_id=cadet.id,
                column_name=CLUB_BOAT,
            )
        )
    except Exception as e:
        print(
            "No club boat available on day for %s, probably because not available today"
            % cadet.name
        )
        return

    update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available(
        object_store=interface.object_store,
        boat_name=boat_name,
        cadet=cadet,
        event=event,
        day=day,
    )


def update_club_boat_for_cadet_across_days(
    interface: abstractInterface, event: Event, cadet: Cadet
):
    try:
        boat_name = interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                cadet_id=cadet.id,
                column_name=CLUB_BOAT,
            )
        )
    except Exception as e:
        print(
            "No club boat available for %s, probably because can't be edited"
            % cadet.name
        )
        return

    for day in event.days_in_event():
        update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available(
            object_store=interface.object_store,
            boat_name=boat_name,
            cadet=cadet,
            event=event,
            day=day,
        )


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


def update_boat_info_for_all_cadets_in_form(
    interface: abstractInterface, list_of_cadets: ListOfCadets
):
    if no_day_set_in_state(interface):
        update_boat_info_for_all_cadets_in_form_across_days(
            interface=interface, list_of_cadets=list_of_cadets
        )
    else:
        day = get_day_from_state_or_none(interface)
        update_boat_info_for_all_cadets_in_form_on_day(
            interface=interface, list_of_cadets=list_of_cadets, day=day
        )


def update_boat_info_for_all_cadets_in_form_on_day(
    interface: abstractInterface, list_of_cadets: ListOfCadets, day: Day
):
    event = get_event_from_state(interface)
    list_of_updates = get_list_of_updates(
        interface=interface, list_of_cadets=list_of_cadets
    )
    update_boat_info_for_cadets_at_event(
        object_store=interface.object_store,
        event=event,
        list_of_updates=list_of_updates,
        day=day,
    )


def update_boat_info_for_all_cadets_in_form_across_days(
    interface: abstractInterface, list_of_cadets: ListOfCadets
):
    event = get_event_from_state(interface)
    list_of_updates = get_list_of_updates(
        interface=interface, list_of_cadets=list_of_cadets
    )
    for day in event.days_in_event():
        update_boat_info_for_cadets_at_event(
            object_store=interface.object_store,
            event=event,
            list_of_updates=list_of_updates,
            day=day,
        )


def get_list_of_updates(
    interface: abstractInterface, list_of_cadets: ListOfCadets
) -> List[CadetWithDinghyInputs]:
    list_of_updates = []
    for cadet in list_of_cadets:
        try:
            update_for_cadet = get_update_for_cadet(interface=interface, cadet=cadet)
        except Exception as e:
            print(
                "Error %s whilst updating boat updates for %s perfectly normal if field can't be edited"
                % (str(e), cadet.name)
            )
            continue

        list_of_updates.append(update_for_cadet)

    return list_of_updates


def get_update_for_cadet(
    interface: abstractInterface, cadet: Cadet
) -> CadetWithDinghyInputs:
    sail_number = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(
            cadet_id=cadet.id, column_name=SAIL_NUMBER
        )
    )
    boat_class_name = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(
            cadet_id=cadet.id, column_name=BOAT_CLASS
        )
    )
    two_handed_partner_as_str = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(cadet_id=cadet.id, column_name=PARTNER)
    )

    return CadetWithDinghyInputs(
        cadet=cadet,
        sail_number=sail_number,
        boat_class_name=boat_class_name,
        two_handed_partner_cadet_as_str=two_handed_partner_as_str,
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
