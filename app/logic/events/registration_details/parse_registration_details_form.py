from app.backend.data.cadets_at_event import save_cadets_at_event
from app.backend.volunteers.volunteer_allocation import volunteer_ids_associated_with_cadet_at_specific_event
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.backend.cadets import cadet_name_from_id
from app.backend.wa_import.update_cadets_at_event import update_availability_of_existing_cadet_at_event, \
    update_status_of_existing_cadet_at_event, update_data_row_for_existing_cadet_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadet_at_event import ListOfCadetsAtEvent, CadetAtEvent
from app.objects.events import Event
from app.backend.form_utils import get_availablity_from_form, get_status_from_form

from app.logic.events.registration_details.registration_details_form import get_registration_data, \
    RegistrationDetailsForEvent, input_name_from_column_name_and_cadet_id, _column_can_be_edited,\
 ROW_STATUS, DAYS_ATTENDING

from app.objects.field_list import FIELDS_WITH_INTEGERS, FIELDS_AS_STR
from app.objects.day_selectors import DaySelector
from app.objects.mapped_wa_event import RegistrationStatus, cancelled_status, deleted_status


def parse_registration_details_from_form(interface: abstractInterface, event: Event):
    ## This loads the existing data
    registration_data = get_registration_data(event=event)

    for cadet_in_data in registration_data.cadets_at_event:
        ## in place update so doesn't return anything
        get_registration_details_for_row_in_form_and_alter_registration_data(interface=interface, registration_data=registration_data,
                                                                             original_cadet_in_data = cadet_in_data)


def get_registration_details_for_row_in_form_and_alter_registration_data(interface: abstractInterface,
                                                                         original_cadet_in_data: CadetAtEvent,
                                                                         registration_data: RegistrationDetailsForEvent):
    ## in place updates so doesn't return anything
    get_special_fields_from_form_and_alter_registration_data(
        interface=interface,
        original_cadet_in_data=original_cadet_in_data,
        event = registration_data.event
    )

    get_other_fields_from_form_and_alter_registration_data(
        interface=interface,
        original_cadet_in_data=original_cadet_in_data,
        registration_data=registration_data
    )


def get_special_fields_from_form_and_alter_registration_data(interface: abstractInterface, original_cadet_in_data: CadetAtEvent, event: Event):
    get_days_attending_for_row_in_form_and_alter_registration_data(interface=interface,
                                                                   original_cadet_in_data=original_cadet_in_data,
                                                                   event=event)
    get_cadet_event_status_for_row_in_form_and_alter_registration_data(interface=interface,
                                                                       original_cadet_in_data=original_cadet_in_data,
                                                                       event=event)


def get_days_attending_for_row_in_form_and_alter_registration_data(interface: abstractInterface,
                                                                   original_cadet_in_data: CadetAtEvent,
                                                                    event: Event):


    new_attendance = get_availablity_from_form(
        interface=interface,
        input_name=input_name_from_column_name_and_cadet_id(
            DAYS_ATTENDING,
            cadet_id=original_cadet_in_data.cadet_id
        ),
        event = event
    )
    original_attendance = original_cadet_in_data.availability
    if new_attendance == original_attendance:
        return
    else:
        update_availability_of_existing_cadet_at_event(event=event, cadet_id=original_cadet_in_data.cadet_id, new_availabilty=new_attendance)
        log_alert_for_attendance_change(interface=interface, new_attendance=new_attendance, cadet_id=original_cadet_in_data.cadet_id,
                                        event=event, original_attendance=original_attendance)


def get_cadet_event_status_for_row_in_form_and_alter_registration_data(interface: abstractInterface,
                                                                       original_cadet_in_data: CadetAtEvent,
                                                                       event: Event):

    new_status = get_status_from_form(interface=interface, input_name=input_name_from_column_name_and_cadet_id(
        column_name=ROW_STATUS,
        cadet_id=original_cadet_in_data.cadet_id
    ))
    original_status = original_cadet_in_data.status

    if original_status == new_status:
        return
    else:
        update_status_of_existing_cadet_at_event(cadet_id=original_cadet_in_data.cadet_id, event=event, new_status=new_status)
        log_alert_for_status_change(interface=interface, new_status=new_status, original_status=original_status,
                                    cadet_id=original_cadet_in_data.cadet_id, event=event)



def get_other_fields_from_form_and_alter_registration_data(interface: abstractInterface, original_cadet_in_data: CadetAtEvent, registration_data: RegistrationDetailsForEvent):
    all_columns = registration_data.all_columns_excluding_special_fields
    for column_name in all_columns:
        if _column_can_be_edited(column_name):
            ## in place update so doesn't return anything
            get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
                column_name=column_name,
                interface=interface,
                original_cadet_in_data=original_cadet_in_data,
                event = registration_data.event
            )


def get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(column_name: str, interface: abstractInterface,
                                                                                         original_cadet_in_data: CadetAtEvent,
                                                                                         event: Event):
    cadet_id = original_cadet_in_data.cadet_id
    input_name = input_name_from_column_name_and_cadet_id(column_name=column_name, cadet_id=cadet_id)

    form_value = interface.value_from_form(input_name)
    data_in_row = original_cadet_in_data.data_in_row
    data_in_row[column_name] = typecast_input_of_column(column_name=column_name, value=form_value)

    update_data_row_for_existing_cadet_at_event(new_data_in_row=data_in_row, cadet_id=original_cadet_in_data.cadet_id,
                                                event = event)

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
                                original_status: RegistrationStatus,
                                new_status: RegistrationStatus,
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

    volunteer_names = [get_volunteer_from_id(volunteer_id).name for volunteer_id in list_of_volunteer_ids]
    volunteer_list_as_str = ", ".join(volunteer_names)

    if len(list_of_volunteer_ids) == 0:
        # no warning needed
        return

    interface.log_error(warning_str+" "+volunteer_list_as_str)

