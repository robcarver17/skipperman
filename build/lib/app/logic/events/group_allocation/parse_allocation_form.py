from app.backend.data.group_allocations import save_current_allocations_for_event
from app.backend.forms.form_utils import input_name_from_column_name_and_cadet_id, get_availablity_from_form
from app.backend.group_allocations.boat_allocation import update_club_boat_allocation_for_cadet_at_event
from app.backend.group_allocations.group_allocations_data import get_allocation_data, AllocationData
from app.backend.wa_import.update_cadets_at_event import update_availability_of_existing_cadet_at_event

from app.logic.events.constants import ALLOCATION, ATTENDANCE, CLUB_BOAT
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.groups import Group


def update_data_given_allocation_form(interface: abstractInterface):
    event = get_event_from_state(interface)
    allocation_data = get_allocation_data(event)
    list_of_cadets = allocation_data.list_of_cadets_in_event
    for cadet in list_of_cadets:
        do_allocation_for_cadet_at_event(
            interface=interface,
            cadet=cadet,
            allocation_data=allocation_data,
        )
        update_attendance_data_for_cadet_in_form(interface=interface, cadet=cadet)
        update_club_boat_for_cadet_in_form(interface=interface, cadet=cadet)
        update_partner_for_cadet_in_form(interface)
        update_boat_class_for_cadet_in_form(interface)
        update_sail_number_for_cadet_in_form(interface)



def do_allocation_for_cadet_at_event(
    cadet: Cadet,
    allocation_data: AllocationData,
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    allocation_str = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(ALLOCATION, cadet_id=cadet.id)
    )
    print("Allocation %s for cadet %s" % (allocation_str, str(cadet)))
    chosen_group = Group(allocation_str)
    allocation_data.current_allocation_for_event.update_group_for_cadet(
        cadet=cadet, chosen_group=chosen_group
    )
    save_current_allocations_for_event(
        list_of_cadets_with_groups=allocation_data.current_allocation_for_event,
        event=event,
    )

def update_attendance_data_for_cadet_in_form(interface: abstractInterface, cadet: Cadet):
    event = get_event_from_state(interface)
    new_attendance = get_availablity_from_form(
        interface=interface,
        input_name=input_name_from_column_name_and_cadet_id(
            ATTENDANCE,
            cadet_id=cadet.id
        ),
        event = event
    )
    update_availability_of_existing_cadet_at_event(event=event, cadet_id=cadet.id, new_availabilty=new_attendance)

def update_club_boat_for_cadet_in_form(interface: abstractInterface, cadet: Cadet):
    event = get_event_from_state(interface)
    boat_name = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(
            cadet_id=cadet.id,
            column_name=CLUB_BOAT
        )
    )
    update_club_boat_allocation_for_cadet_at_event(boat_name = boat_name, cadet_id=cadet.id, event=event)


def update_partner_for_cadet_in_form(interface: abstractInterface):
    event = get_event_from_state(interface)

def update_boat_class_for_cadet_in_form(interface: abstractInterface):
    event = get_event_from_state(interface)

def update_sail_number_for_cadet_in_form(interface: abstractInterface):
    event = get_event_from_state(interface)
