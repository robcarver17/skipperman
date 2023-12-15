from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.objects.master_event import MasterEvent, RowInMasterEvent
from app.objects.events import Event
from app.logic.events.backend.update_master_event_data import save_master_event

from app.logic.events.registration_details.registration_details_form import get_registration_data, \
    get_top_row_for_event, row_for_cadet_in_event, RegistrationDetailsForEvent, input_name_from_column_name_and_cadet_id, _column_can_be_edited

def parse_registration_details_from_form(interface: abstractInterface, event: Event):
    master_event = get_registration_details_from_form(interface=interface, event=event)
    #save_master_event(master_event=master_event, event=event)

def get_registration_details_from_form(interface: abstractInterface, event: Event) -> MasterEvent:
    registration_data = get_registration_data(event=event)
    for row_in_data in registration_data.master_event_details:
        ## in place update so doesn't do anything
        get_registration_details_for_row_in_form_and_alter_registration_data(interface=interface, registration_data=registration_data,
                                                                             original_row_in_data=row_in_data)

    ## this is what is updated

    return registration_data.master_event_details

def get_registration_details_for_row_in_form_and_alter_registration_data(interface: abstractInterface, original_row_in_data: RowInMasterEvent, registration_data: RegistrationDetailsForEvent):
    #status#
    #other#
    all_columns = registration_data.all_columns

    for column_name in all_columns:
        if _column_can_be_edited(column_name):
            get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
                column_name=column_name,
                interface=interface,
                original_row_in_data=original_row_in_data,

            )

def get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(column_name: str, interface: abstractInterface, original_row_in_data: RowInMasterEvent):
    #status#
    #other#
    cadet_id = original_row_in_data.cadet_id
    input_name = input_name_from_column_name_and_cadet_id(column_name=column_name, cadet_id=cadet_id)

    form_value = interface.value_from_form(input_name)

    print("%s, %s, %s" % (column_name, cadet_id, form_value))