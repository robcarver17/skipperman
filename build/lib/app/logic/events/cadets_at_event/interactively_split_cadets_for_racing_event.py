from typing import Union


from app.backend.data.mapped_events import get_row_in_mapped_event_data_given_id
from app.backend.data.cadets_at_event import  load_identified_cadets_at_event
from app.backend.cadets import confirm_cadet_exists, get_cadet_from_list_of_cadets, load_list_of_all_cadets
from app.logic.events.cadets_at_event.interactively_update_records_of_cadets_at_event import \
    display_form_interactively_update_cadets_at_event
from app.logic.events.cadets_at_event.iteratively_add_cadet_ids_in_wa_import_stage import \
    display_form_add_cadet_ids_during_import

from app.logic.events.constants import *
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.import_wa.shared_state_tracking_and_data import get_and_save_next_row_id_in_mapped_event_data, \
    get_current_row_id, clear_row_in_state
from app.backend.wa_import.add_cadet_ids_to_mapped_wa_event_data import (
    add_identified_cadet_and_row,
    get_cadet_data_from_row_of_mapped_data_no_checks,
)
from app.logic.events.cadets_at_event.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
)
from app.logic.cadets.add_cadet import add_cadet_from_form_to_data

from app.objects.constants import NoMoreData
from app.objects.mapped_wa_event import RowInMappedWAEvent
from app.objects.cadets import Cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_split_cadets_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## rest of the time is post

    clear_row_in_state(interface)
    return split_cadets_on_next_row(interface)


def split_cadets_on_next_row(
            interface: abstractInterface,
    ) -> Union[Form, NewForm]:

    event = get_event_from_state(interface)
    print("Looping through splitting rows in WA file before IDs are allocated")

    try:
        row_id = get_and_save_next_row_id_in_mapped_event_data(interface)
        next_row = get_row_in_mapped_event_data_given_id(event=event, row_id=row_id)
        print("On row %s" % str(next_row))
        return split_next_row(next_row=next_row, interface=interface)
    except NoMoreData:
        print("Finished splitting, next step is looping through allocating Cadet IDs")
        clear_row_in_state(interface)
        ## don't return to controller as need to update cadet data now
        return go_to_identify_cadets_data_form(interface)


def split_next_row(next_row: RowInMappedWAEvent, interface: abstractInterface) -> Union[Form, NewForm]:
    return split_cadets_on_next_row(interface)## FIX ME TO GET IT WORKING

def post_form_split_cadets_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    pass

def go_to_identify_cadets_data_form(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_add_cadet_ids_during_import)
