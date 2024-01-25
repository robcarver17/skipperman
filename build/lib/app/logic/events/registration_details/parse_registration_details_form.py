from app.logic.abstract_interface import abstractInterface
from app.objects.master_event import MasterEvent, RowInMasterEvent
from app.objects.events import Event
from app.backend.update_master_event_data import save_master_event

from app.logic.events.registration_details.registration_details_form import get_registration_data, \
    RegistrationDetailsForEvent, input_name_from_column_name_and_cadet_id, _column_can_be_edited

from app.objects.field_list import FIELDS_WITH_INTEGERS, FIELDS_AS_STR, DAYS_ATTENDING

def parse_registration_details_from_form(interface: abstractInterface, event: Event):
    master_event = get_registration_details_from_form(interface=interface, event=event)
    print(master_event)
    save_master_event(master_event=master_event, event=event)

def get_registration_details_from_form(interface: abstractInterface, event: Event) -> MasterEvent:
    ## This loads the existing master event
    registration_data = get_registration_data(event=event)
    for row_in_data in registration_data.master_event_details:
        ## in place update so doesn't do anything
        get_registration_details_for_row_in_form_and_alter_registration_data(interface=interface, registration_data=registration_data,
                                                                             original_row_in_data=row_in_data)

    ## this is what is updated

    return registration_data.master_event_details

def get_registration_details_for_row_in_form_and_alter_registration_data(interface: abstractInterface, original_row_in_data: RowInMasterEvent, registration_data: RegistrationDetailsForEvent):

    all_columns = registration_data.all_columns

    for column_name in all_columns:
        if _column_can_be_edited(column_name):
            get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
                column_name=column_name,
                interface=interface,
                original_row_in_data=original_row_in_data,
                registration_data=registration_data
            )

def get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(column_name: str, interface: abstractInterface, original_row_in_data: RowInMasterEvent,
                                                                                         registration_data: RegistrationDetailsForEvent):
    if column_name==DAYS_ATTENDING:
        return get_days_attending_for_row_and_column_name_in_form_and_alter_registration_data(
            column_name=column_name,
            interface=interface,
            original_row_in_data=original_row_in_data,
            registration_details=registration_data
        )
    else:
        return get_normal_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
            column_name=column_name,
            interface=interface,
            original_row_in_data=original_row_in_data

        )

def get_normal_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(column_name: str, interface: abstractInterface, original_row_in_data: RowInMasterEvent):

    cadet_id = original_row_in_data.cadet_id
    input_name = input_name_from_column_name_and_cadet_id(column_name=column_name, cadet_id=cadet_id)

    form_value = interface.value_from_form(input_name)

    original_row_in_data.data_in_row[column_name] = typecast_input_of_column(column_name=column_name, value=form_value)

def typecast_input_of_column(column_name:str, value):
    if column_name in FIELDS_AS_STR:
        return str(value)
    elif column_name in FIELDS_WITH_INTEGERS:
        return int(value)
    ## don't do dates as hopefully parsed automatically

    return value

def get_days_attending_for_row_and_column_name_in_form_and_alter_registration_data(column_name: str, interface: abstractInterface, original_row_in_data: RowInMasterEvent,
                                                                                   registration_details: RegistrationDetailsForEvent):

    cadet_id = original_row_in_data.cadet_id
    input_name = input_name_from_column_name_and_cadet_id(column_name=column_name, cadet_id=cadet_id)

    selected_days = interface.value_of_multiple_options_from_form(input_name)

    day_selector = original_row_in_data.data_in_row[DAYS_ATTENDING]
    possible_days = registration_details.weekdays_in_event
    for day in possible_days:
        if day.name in selected_days:
            day_selector[day] = True
        else:
            day_selector[day] = False

    original_row_in_data.data_in_row[column_name] = day_selector
