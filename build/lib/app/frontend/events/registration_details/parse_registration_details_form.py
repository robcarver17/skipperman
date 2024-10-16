from app.OLD_backend.volunteers.volunteer_allocation import (
    DEPRECATE_get_list_of_volunteer_names_associated_with_cadet_at_event,
)
from app.OLD_backend.cadets import  cadet_name_from_id
from app.OLD_backend.wa_import.update_cadets_at_event import (
    update_data_row_for_existing_cadet_at_event,
    update_availability_of_existing_cadet_at_event,
    update_status_of_existing_cadet_at_event_to_cancelled_or_deleted,
    update_status_of_existing_cadet_at_event,
    update_notes_for_existing_cadet_at_event,
    update_health_for_existing_cadet_at_event,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent
from app.objects.events import Event
from app.frontend.forms.form_utils import (
    get_availablity_from_form,
    get_status_from_form,
    input_name_from_column_name_and_cadet_id,
)

from app.frontend.events.registration_details.registration_details_form import (
    get_registration_data,
    RegistrationDetailsForEvent,
    _column_can_be_edited,
    ROW_STATUS,
    DAYS_ATTENDING,
    NOTES,
    HEALTH,
)

from app.data_access.configuration.field_list_groups import (
    FIELDS_WITH_INTEGERS,
    FIELDS_AS_STR,
)
from app.objects.day_selectors import DaySelector
from app.objects.registration_data import RegistrationStatus


def parse_registration_details_from_form(interface: abstractInterface, event: Event):
    ## This loads the existing data
    registration_data = get_registration_data(interface=interface, event=event)

    for cadet_in_data in registration_data.cadets_at_event:
        ## in place update so doesn't return anything
        get_registration_details_for_row_in_form_and_alter_registration_data(
            interface=interface,
            registration_data=registration_data,
            original_cadet_in_data=cadet_in_data,
        )

    interface.flush_cache_to_store()


def get_registration_details_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    original_cadet_in_data: CadetWithIdAtEvent,
    registration_data: RegistrationDetailsForEvent,
):
    ## in place updates so doesn't return anything
    get_special_fields_from_form_and_alter_registration_data(
        interface=interface,
        original_cadet_in_data=original_cadet_in_data,
        event=registration_data.event,
    )

    get_other_fields_from_form_and_alter_registration_data(
        interface=interface,
        original_cadet_in_data=original_cadet_in_data,
        registration_data=registration_data,
    )


def get_special_fields_from_form_and_alter_registration_data(
    interface: abstractInterface,
    original_cadet_in_data: CadetWithIdAtEvent,
    event: Event,
):
    get_days_attending_for_row_in_form_and_alter_registration_data(
        interface=interface, original_cadet_in_data=original_cadet_in_data, event=event
    )
    get_cadet_event_status_for_row_in_form_and_alter_registration_data(
        interface=interface, original_cadet_in_data=original_cadet_in_data, event=event
    )
    get_cadet_notes_for_row_in_form_and_alter_registration_data(
        interface=interface, original_cadet_in_data=original_cadet_in_data, event=event
    )

    get_cadet_health_for_row_in_form_and_alter_registration_data(
        interface=interface, original_cadet_in_data=original_cadet_in_data, event=event
    )


def get_days_attending_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    original_cadet_in_data: CadetWithIdAtEvent,
    event: Event,
):
    new_attendance = get_availablity_from_form(
        interface=interface,
        input_name=input_name_from_column_name_and_cadet_id(
            DAYS_ATTENDING, cadet_id=original_cadet_in_data.cadet_id
        ),
        event=event,
    )
    original_attendance = original_cadet_in_data.availability
    if new_attendance == original_attendance:
        return

    update_availability_of_existing_cadet_at_event(
        interface=interface,
        event=event,
        cadet_id=original_cadet_in_data.cadet_id,
        new_availabilty=new_attendance,
    )
    log_alert_for_attendance_change(
        interface=interface,
        new_attendance=new_attendance,
        cadet_id=original_cadet_in_data.cadet_id,
        event=event,
        original_attendance=original_attendance,
    )


def get_cadet_event_status_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    original_cadet_in_data: CadetWithIdAtEvent,
    event: Event,
):
    new_status = get_status_from_form(
        interface=interface,
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=ROW_STATUS, cadet_id=original_cadet_in_data.cadet_id
        ),
    )
    original_status = original_cadet_in_data.status

    print("was %s now %s" % (original_status, new_status))

    if original_status == new_status:
        return
    if new_status.is_cancelled_or_deleted:
        update_status_of_existing_cadet_at_event_to_cancelled_or_deleted(
            interface=interface,
            event=event,
            cadet_id=original_cadet_in_data.cadet_id,
            new_status=new_status,
        )
    elif new_status.is_active:
        update_status_of_existing_cadet_at_event(
            interface=interface,
            cadet_id=original_cadet_in_data.cadet_id,
            event=event,
            new_status=new_status,
        )
    else:
        interface.log_error(
            "Status change to cadet ID %s for %s not recognised contact support"
            % (original_cadet_in_data.cadet_id, str(new_status))
        )

    log_alert_for_status_change(
        interface=interface,
        event=event,
        cadet_id=original_cadet_in_data.cadet_id,
        original_status=original_status,
        new_status=new_status,
    )


def get_cadet_notes_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    original_cadet_in_data: CadetWithIdAtEvent,
    event: Event,
):
    new_notes = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(
            column_name=NOTES, cadet_id=original_cadet_in_data.cadet_id
        )
    )
    original_notes = original_cadet_in_data.notes
    if original_notes == new_notes:
        return

    update_notes_for_existing_cadet_at_event(
        interface=interface,
        cadet_id=original_cadet_in_data.cadet_id,
        event=event,
        new_notes=new_notes,
    )


def get_cadet_health_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    original_cadet_in_data: CadetWithIdAtEvent,
    event: Event,
):
    new_health = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(
            column_name=HEALTH, cadet_id=original_cadet_in_data.cadet_id
        )
    )
    original_health = original_cadet_in_data.health
    if original_health == new_health:
        return

    update_health_for_existing_cadet_at_event(
        interface=interface,
        cadet_id=original_cadet_in_data.cadet_id,
        event=event,
        new_health=new_health,
    )


def get_other_fields_from_form_and_alter_registration_data(
    interface: abstractInterface,
    original_cadet_in_data: CadetWithIdAtEvent,
    registration_data: RegistrationDetailsForEvent,
):
    all_columns = registration_data.all_columns_excluding_special_fields
    for column_name in all_columns:
        if _column_can_be_edited(column_name):
            ## in place update so doesn't return anything
            get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
                column_name=column_name,
                interface=interface,
                original_cadet_in_data=original_cadet_in_data,
                event=registration_data.event,
            )


def get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
    column_name: str,
    interface: abstractInterface,
    original_cadet_in_data: CadetWithIdAtEvent,
    event: Event,
):
    cadet_id = original_cadet_in_data.cadet_id
    input_name = input_name_from_column_name_and_cadet_id(
        column_name=column_name, cadet_id=cadet_id
    )

    form_value = interface.value_from_form(input_name)
    data_in_row = original_cadet_in_data.data_in_row
    data_in_row[column_name] = typecast_input_of_column(
        column_name=column_name, value=form_value
    )

    update_data_row_for_existing_cadet_at_event(
        interface=interface,
        new_data_in_row=data_in_row,
        cadet_id=original_cadet_in_data.cadet_id,
        event=event,
    )


def typecast_input_of_column(column_name: str, value):
    if column_name in FIELDS_AS_STR:
        return str(value)
    elif column_name in FIELDS_WITH_INTEGERS:
        return int(value)
    ## don't do dates as hopefully parsed automatically

    return value


def log_alert_for_attendance_change(
    interface: abstractInterface,
    original_attendance: DaySelector,
    new_attendance: DaySelector,
    cadet_id: str,
    event: Event,
):
    if original_attendance == new_attendance:
        return

    warning_str = (
        "*Following volunteers associated with cadet %s for whom days attending updated - check they are still available for their nominated days, and if not update volunteer rota:"
        % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
    )

    log_alert_for_volunteers(
        warning_str=warning_str, interface=interface, cadet_id=cadet_id, event=event
    )


def log_alert_for_status_change(
    interface: abstractInterface,
    original_status: RegistrationStatus,
    new_status: RegistrationStatus,
    cadet_id: str,
    event: Event,
):
    if original_status == new_status:
        return

    if new_status.is_cancelled_or_deleted:
        warning_str = (
            "*Following volunteers associated with cadet %s for whom status updated to deleted or cancelled - check their availability, and if no longer available update volunteer rota:"
            % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        )
    elif original_status.is_cancelled_or_deleted and new_status.is_active:
        warning_str = (
            "*Following volunteers associated with cadet %s for whom status updated to active registration - check their availability on the volunteer rota and / or add new volunteers if available:"
            % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        )
    else:
        return

    log_alert_for_volunteers(
        warning_str=warning_str, interface=interface, cadet_id=cadet_id, event=event
    )


def log_alert_for_volunteers(
    interface: abstractInterface, cadet_id: str, event: Event, warning_str: str
):
    volunteer_names = DEPRECATE_get_list_of_volunteer_names_associated_with_cadet_at_event(
        interface=interface, cadet_id=cadet_id, event=event
    )
    if len(volunteer_names) == 0:
        return

    volunteer_list_as_str = ", ".join(volunteer_names)
    interface.log_error(warning_str + " " + volunteer_list_as_str)


