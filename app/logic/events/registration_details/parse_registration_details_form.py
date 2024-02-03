from app.backend.volunteers.volunteer_allocation import volunteer_ids_associated_with_cadet_at_specific_event
from app.backend.volunteers.volunteers import get_volunteer_from_volunteer_id
from app.backend.cadets import cadet_name_from_id
from app.logic.abstract_interface import abstractInterface
from app.objects.master_event import MasterEvent, RowInMasterEvent
from app.objects.events import Event
from app.backend.wa_import.update_master_event_data import save_master_event
from app.backend.form_utils import get_availablity_from_form, get_status_from_form, get_food_requirements_from_form

from app.logic.events.registration_details.registration_details_form import get_registration_data, \
    RegistrationDetailsForEvent, input_name_from_column_name_and_cadet_id, _column_can_be_edited,\
    FOOD_REQUIRED_CHECKBOX_FORM_NAME, FOOD_REQUIRED_OTHER_FORM_NAME, ROW_STATUS, DAYS_ATTENDING

from app.objects.field_list import FIELDS_WITH_INTEGERS, FIELDS_AS_STR
from app.objects.day_selectors import DaySelector
from app.objects.mapped_wa_event_with_ids import RowStatus, deleted_status, cancelled_status

def parse_registration_details_from_form(interface: abstractInterface, event: Event):
    master_event = get_registration_details_from_form(interface=interface, event=event)
    print(master_event)
    save_master_event(master_event=master_event, event=event)

def get_registration_details_from_form(interface: abstractInterface, event: Event) -> MasterEvent:
    ## This loads the existing master event data
    registration_data = get_registration_data(event=event)

    for row_in_data in registration_data.master_event_details:
        ## in place update so doesn't return anything
        get_registration_details_for_row_in_form_and_alter_registration_data(interface=interface, registration_data=registration_data,
                                                                             original_row_in_data=row_in_data)

    ## this is what is updated

    return registration_data.master_event_details

def get_registration_details_for_row_in_form_and_alter_registration_data(interface: abstractInterface,
                                                                         original_row_in_data: RowInMasterEvent,
                                                                         registration_data: RegistrationDetailsForEvent):
    ## in place updates so doesn't return anything
    get_special_fields_from_form_and_alter_registration_data(
        interface=interface,
        original_row_in_data=original_row_in_data,
        registration_data=registration_data
    )

    get_other_fields_from_form_and_alter_registration_data(
        interface=interface,
        original_row_in_data=original_row_in_data,
        registration_data=registration_data
    )


def get_special_fields_from_form_and_alter_registration_data(interface: abstractInterface, original_row_in_data: RowInMasterEvent, registration_data: RegistrationDetailsForEvent):
    get_days_attending_for_row_in_form_and_alter_registration_data(interface=interface,
                                                                   original_row_in_data=original_row_in_data,
                                                                   registration_details=registration_data)
    get_cadet_event_status_for_row_in_form_and_alter_registration_data(interface=interface,
                                                                       original_row_in_data=original_row_in_data,
                                                                       registration_details=registration_data)
    get_cadet_food_required_for_row_in_form_and_alter_registration_data(interface=interface,
                                                                        original_row_in_data=original_row_in_data)

def get_days_attending_for_row_in_form_and_alter_registration_data(interface: abstractInterface,
                                                                   original_row_in_data: RowInMasterEvent,
                                                                    registration_details: RegistrationDetailsForEvent):
    new_attendance = get_availablity_from_form(
        interface=interface,
        input_name=input_name_from_column_name_and_cadet_id(
            DAYS_ATTENDING,
            cadet_id=original_row_in_data.cadet_id
        ),
        event = registration_details.event
    )
    original_attendance = original_row_in_data.attendance
    log_alert_for_attendance_change(original_attendance=original_attendance,
                                    new_attendance = new_attendance,
                                    cadet_id = original_row_in_data.cadet_id,
                                    event = registration_details.event,
                                    interface=interface)

    original_row_in_data.attendance = new_attendance

def get_cadet_food_required_for_row_in_form_and_alter_registration_data(interface: abstractInterface, original_row_in_data: RowInMasterEvent):
    food_required = get_food_requirements_from_form(
        interface=interface,
        other_input_name=input_name_from_column_name_and_cadet_id(
            column_name=FOOD_REQUIRED_OTHER_FORM_NAME,
            cadet_id=original_row_in_data.cadet_id
        ),
        checkbox_input_name=input_name_from_column_name_and_cadet_id(
            column_name=FOOD_REQUIRED_CHECKBOX_FORM_NAME,
            cadet_id=original_row_in_data.cadet_id
        ),
    )
    original_row_in_data.food_requirements = food_required

def get_cadet_event_status_for_row_in_form_and_alter_registration_data(interface: abstractInterface,
                                                                       original_row_in_data: RowInMasterEvent,
                                                                       registration_details: RegistrationDetailsForEvent):

    new_status = get_status_from_form(interface=interface, input_name=input_name_from_column_name_and_cadet_id(
        column_name=ROW_STATUS,
        cadet_id=original_row_in_data.cadet_id
    ))
    log_alert_for_status_change(interface=interface, original_status=original_row_in_data.status,
                                new_status=new_status, cadet_id=original_row_in_data.cadet_id,
                                event=registration_details.event)
    original_row_in_data.status = new_status


def get_other_fields_from_form_and_alter_registration_data(interface: abstractInterface, original_row_in_data: RowInMasterEvent, registration_data: RegistrationDetailsForEvent):
    all_columns = registration_data.all_columns_excluding_special_fields
    for column_name in all_columns:
        if _column_can_be_edited(column_name):
            ## in place update so doesn't return anything
            get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
                column_name=column_name,
                interface=interface,
                original_row_in_data=original_row_in_data
            )


def get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(column_name: str, interface: abstractInterface, original_row_in_data: RowInMasterEvent):
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

def log_alert_for_attendance_change(interface: abstractInterface,
                                    original_attendance: DaySelector,
                                    new_attendance: DaySelector,
                                    cadet_id: str,
                                    event: Event):

    if original_attendance==new_attendance:
        return

    warning_str = "*Following volunteers associated with cadet %s for whom days attending updated - check they are still available for their nominated days, and if not update volunteer rota:" % cadet_name_from_id(cadet_id)

    log_alert_for_volunteers(warning_str=warning_str, interface=interface, cadet_id=cadet_id, event=event)


def log_alert_for_status_change(interface: abstractInterface,
                                    original_status: RowStatus,
                                    new_status: RowStatus,
                                    cadet_id: str,
                                    event: Event):

    if original_status == new_status:
        return

    if new_status==cancelled_status or new_status==deleted_status:
        warning_str = "*Following volunteers associated with cadet %s for whom status updated to deleted or cancelled - check their availability, and if no longer available update volunteer rota:" % cadet_name_from_id(cadet_id)
    else:
        warning_str = "*Following volunteers associated with cadet %s for whom status updated to active registration - check their availability on the volunteer rota and / or add new volunteers if available:" % cadet_name_from_id(cadet_id)

    log_alert_for_volunteers(warning_str=warning_str, interface=interface, cadet_id=cadet_id, event=event)

def log_alert_for_volunteers(interface: abstractInterface,
                                    cadet_id: str,
                                    event: Event,
                                    warning_str: str):

    list_of_volunteer_ids = volunteer_ids_associated_with_cadet_at_specific_event(event=event, cadet_id=cadet_id)

    volunteer_names = [get_volunteer_from_volunteer_id(volunteer_id).name for volunteer_id in list_of_volunteer_ids]
    volunteer_list_as_str = ", ".join(volunteer_names)

    if len(list_of_volunteer_ids) == 0:
        volunteer_list_as_str = "No volunteers associated with cadet"

    interface.log_error(warning_str+" "+volunteer_list_as_str)

