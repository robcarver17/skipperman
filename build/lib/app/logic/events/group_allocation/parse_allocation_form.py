from typing import List

from app.backend.data.group_allocations import GroupAllocationsData
from app.logic.events.group_allocation.store_state import no_day_set_in_state, get_day_from_state_or_none

from app.objects.day_selectors import Day

from app.logic.events.group_allocation.input_fields import NOTES
from app.objects.events import Event

from app.backend.forms.form_utils import input_name_from_column_name_and_cadet_id, get_availablity_from_form
from app.backend.group_allocations.boat_allocation import update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available, \
    update_boat_info_for_cadets_at_event, CadetWithDinghyInputs
from app.backend.group_allocations.group_allocations_data import get_allocation_data, AllocationData
from app.backend.wa_import.update_cadets_at_event import update_availability_of_existing_cadet_at_event, \
    update_notes_for_existing_cadet_at_event

from app.logic.events.constants import ALLOCATION, ATTENDANCE, CLUB_BOAT, SAIL_NUMBER, PARTNER, BOAT_CLASS
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.groups import Group


def update_data_given_allocation_form(interface: abstractInterface):
    event = get_event_from_state(interface)
    allocation_data = get_allocation_data(interface=interface, event=event)
    list_of_cadets = allocation_data.list_of_cadets_in_event_active_only
    for cadet in list_of_cadets:

        if event.contains_groups:
            do_allocation_for_cadet_at_event(
                interface=interface,
                cadet=cadet,
            )
        update_attendance_data_for_cadet_in_form(interface=interface, cadet=cadet)
        update_club_boat_for_cadet_in_form(interface=interface, cadet=cadet)
        get_cadet_notes_for_row_in_form_and_alter_registration_data(interface=interface, allocation_data=allocation_data, event=event, cadet=cadet)

    ## has to be done in one go because of swaps
    update_boat_info_for_all_cadets_in_form(interface=interface, allocation_data=allocation_data)

    interface.save_stored_items()


def do_allocation_for_cadet_at_event(
    cadet: Cadet,
    interface: abstractInterface,
):
    if no_day_set_in_state(interface):
        do_allocation_for_cadet_at_event_across_days(cadet=cadet,
                                                     interface=interface)
    else:
        day = get_day_from_state_or_none(interface)
        do_allocation_for_cadet_at_event_on_day(
            interface=interface,
            cadet=cadet,
            day=day,
        )


def do_allocation_for_cadet_at_event_on_day(
        cadet: Cadet,
        day: Day,
        interface: abstractInterface,
):
    event = get_event_from_state(interface)
    try:
        allocation_str = interface.value_from_form(
            input_name_from_column_name_and_cadet_id(column_name=ALLOCATION, cadet_id=cadet.id)
        )
        print("Allocation %s for cadet %s" % (allocation_str, str(cadet)))
    except Exception as e:
        print("No allocation available on day for %s, probably because not available today" % cadet.name)
        return

    chosen_group = Group(allocation_str)

    group_allocation_data =  GroupAllocationsData(interface.data)
    group_allocation_data.add_or_upate_group_for_cadet_on_day_if_cadet_available_on_day(
        event=event,
        cadet=cadet,day=day, group=chosen_group
    )

def do_allocation_for_cadet_at_event_across_days(
        cadet: Cadet,
        interface: abstractInterface,
):
    event = get_event_from_state(interface)
    try:
        allocation_str = interface.value_from_form(
            input_name_from_column_name_and_cadet_id(column_name=ALLOCATION, cadet_id=cadet.id)
        )
        print("Allocation %s for cadet %s" % (allocation_str, str(cadet)))
    except Exception as e:
        print("No allocation available for %s, probably because can't be edited" % cadet.name)
        return

    chosen_group = Group(allocation_str)

    group_allocation_data =  GroupAllocationsData(interface.data)
    for day in event.weekdays_in_event():
        ## Won't update cadets who aren't available on a given day
        group_allocation_data.add_or_upate_group_for_cadet_on_day_if_cadet_available_on_day(
            event=event,
            cadet=cadet,day=day, group=chosen_group
        )


def update_attendance_data_for_cadet_in_form(interface: abstractInterface, cadet: Cadet):
    event = get_event_from_state(interface)
    try:
        new_attendance = get_availablity_from_form(
            interface=interface,
            input_name=input_name_from_column_name_and_cadet_id(
                ATTENDANCE,
                cadet_id=cadet.id
            ),
            event = event
        )
    except Exception as e:
        print("Error %s whilst updating attendance for %s" % (str(e), cadet.name))
        return
    
    update_availability_of_existing_cadet_at_event(interface=interface, event=event, cadet_id=cadet.id, new_availabilty=new_attendance)

def update_club_boat_for_cadet_in_form(interface: abstractInterface, cadet: Cadet):
    event = get_event_from_state(interface)
    if no_day_set_in_state(interface):
        update_club_boat_for_cadet_across_days(interface=interface, cadet=cadet, event=event)
    else:
        day = get_day_from_state_or_none(interface)
        update_club_boat_for_cadet_on_day_in_form(
            interface=interface,
            event=event,
            cadet=cadet,
            day=day
        )


def update_club_boat_for_cadet_on_day_in_form(interface: abstractInterface, event: Event, day: Day, cadet: Cadet):
    try:
        boat_name = interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                cadet_id=cadet.id,
                column_name=CLUB_BOAT,
            )
        )
    except Exception as e:
        print("No club boat available on day for %s, probably because not available today" % cadet.name)
        return


    update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available(interface=interface, boat_name = boat_name, cadet_id=cadet.id, event=event, day=day)


def update_club_boat_for_cadet_across_days(interface: abstractInterface, event: Event,  cadet: Cadet):
    try:
        boat_name = interface.value_from_form(
            input_name_from_column_name_and_cadet_id(
                cadet_id=cadet.id,
                column_name=CLUB_BOAT,
            )
        )
    except Exception as e:
        print("No club boat available for %s, probably because can't be edited" % cadet.name)
        return


    for day in event.weekdays_in_event():
        update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available(interface=interface, boat_name = boat_name, cadet_id=cadet.id, event=event, day=day)



def get_cadet_notes_for_row_in_form_and_alter_registration_data(interface: abstractInterface,
                                                                       cadet: Cadet,
                                                                       event: Event,
                                                                allocation_data: AllocationData,
                                                                ):
    new_notes = interface.value_from_form(input_name_from_column_name_and_cadet_id(
        column_name=NOTES,
        cadet_id=cadet.id
    ))
    cadet_at_event = allocation_data.cadets_at_event_including_non_active.cadet_at_event(cadet.id)
    original_notes = cadet_at_event.notes
    if original_notes == new_notes:
        return
    else:
        update_notes_for_existing_cadet_at_event(interface=interface, cadet_id=cadet.id, event=event, new_notes=new_notes)


def update_boat_info_for_all_cadets_in_form(interface: abstractInterface, allocation_data: AllocationData):
    if no_day_set_in_state(interface):
        update_boat_info_for_all_cadets_in_form_across_days(interface=interface, allocation_data=allocation_data)
    else:
        day = get_day_from_state_or_none(interface)
        update_boat_info_for_all_cadets_in_form_on_day(interface=interface,
                                                       allocation_data=allocation_data,
                                                       day=day)

def update_boat_info_for_all_cadets_in_form_on_day(interface: abstractInterface, allocation_data: AllocationData, day: Day):
    event = get_event_from_state(interface)
    list_of_updates = get_list_of_updates(interface=interface, allocation_data=allocation_data)
    update_boat_info_for_cadets_at_event(
        interface=interface,
        event=event,list_of_updates=list_of_updates,
        day= day
    )

def update_boat_info_for_all_cadets_in_form_across_days(interface: abstractInterface, allocation_data: AllocationData):
    event = get_event_from_state(interface)
    list_of_updates = get_list_of_updates(interface=interface, allocation_data=allocation_data)
    for day in event.weekdays_in_event():
        update_boat_info_for_cadets_at_event(
            interface=interface,
            event=event,list_of_updates=list_of_updates,
            day= day
        )


def get_list_of_updates(interface: abstractInterface, allocation_data: AllocationData)-> List[CadetWithDinghyInputs]:
    list_of_updates = []
    list_of_cadets = allocation_data.list_of_cadets_in_event_active_only
    for cadet in list_of_cadets:
        try:
            update_for_cadet = get_update_for_cadet(interface=interface, cadet=cadet)
        except Exception as e:
            print("Error %s whilst updating boat updates for %s perfectly normal if field can't be edited" % (str(e), cadet.name))
            continue

        list_of_updates.append(update_for_cadet)

    return list_of_updates

def get_update_for_cadet(interface: abstractInterface, cadet: Cadet) -> CadetWithDinghyInputs:
    sail_number = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(cadet_id=cadet.id, column_name=SAIL_NUMBER)
    )
    boat_class_name = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(cadet_id=cadet.id, column_name=BOAT_CLASS)
    )
    two_handed_partner_name = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(cadet_id=cadet.id, column_name=PARTNER)
    )

    return CadetWithDinghyInputs(
        sail_number=sail_number,
        boat_class_name=boat_class_name,
        two_handed_partner_name=two_handed_partner_name,
        cadet_id=cadet.id,
    )