from app.backend.volunteers.connected_cadets import (
    get_list_of_volunteers_associated_with_cadet,
)

from app.objects.cadets import Cadet

from app.backend.registration_data.update_cadets_at_event import (
    update_notes_for_existing_cadet_at_event,
    update_health_for_existing_cadet_at_event,
    update_data_row_for_existing_cadet_at_event,
)
from app.backend.cadets_at_event.update_status_and_availability_of_cadets_at_event import (
    update_status_of_existing_cadet_at_event_to_cancelled_or_deleted_and_return_messages,
    update_availability_of_existing_cadet_at_event_and_return_messages,
    update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
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
from app.objects.registration_status import RegistrationStatus
from app.objects.utilities.exceptions import MISSING_FROM_FORM


def parse_registration_details_from_form(interface: abstractInterface, event: Event):
    ## This loads the existing data
    registration_details = get_registration_data(interface=interface, event=event)
    registration_data = registration_details.registration_data

    for cadet in registration_data.list_of_cadets():
        ## in place update so doesn't return anything
        get_registration_details_for_row_in_form_and_alter_registration_data(
            interface=interface,
            registration_details=registration_details,
            cadet=cadet,
        )


def get_registration_details_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
):
    ## in place updates so doesn't return anything
    get_special_fields_from_form_and_alter_registration_data(
        interface=interface,
        cadet=cadet,
        registration_details=registration_details,
    )

    get_other_fields_from_form_and_alter_registration_data(
        interface=interface,
        cadet=cadet,
        registration_details=registration_details,
    )


def get_special_fields_from_form_and_alter_registration_data(
    interface: abstractInterface,
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
):
    get_days_attending_for_row_in_form_and_alter_registration_data(
        interface=interface, cadet=cadet, registration_details=registration_details
    )
    get_cadet_event_status_for_row_in_form_and_alter_registration_data(
        interface=interface, cadet=cadet, registration_details=registration_details
    )
    get_cadet_notes_for_row_in_form_and_alter_registration_data(
        interface=interface, cadet=cadet, registration_details=registration_details
    )

    get_cadet_health_for_row_in_form_and_alter_registration_data(
        interface=interface, cadet=cadet, registration_details=registration_details
    )


def get_days_attending_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
):
    new_attendance = get_availablity_from_form(
        interface=interface,
        input_name=input_name_from_column_name_and_cadet_id(
            DAYS_ATTENDING, cadet_id=cadet.id
        ),
        event=registration_details.event,
        default=MISSING_FROM_FORM
    )
    if new_attendance is MISSING_FROM_FORM:
        interface.log_error("attendance not in form for %s" % cadet)
        return

    original_attendance = (
        registration_details.registration_data.registration_data_for_cadet(
            cadet
        ).availability
    )
    if new_attendance == original_attendance:
        return

    messages = update_availability_of_existing_cadet_at_event_and_return_messages(
        object_store=interface.object_store,
        event=registration_details.event,
        cadet=cadet,
        new_availabilty=new_attendance,
    )
    if len(messages) > 0:
        for message in messages:
            interface.log_error(message)

    log_alert_for_attendance_change(
        interface=interface,
        new_attendance=new_attendance,
        cadet=cadet,
        original_attendance=original_attendance,
    )


def get_cadet_event_status_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
):
    new_status = get_status_from_form(
        interface=interface,
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=ROW_STATUS, cadet_id=cadet.id
        ),
        default=MISSING_FROM_FORM
    )

    if new_status is MISSING_FROM_FORM:
        interface.log_error("Can't get new status for %s" % cadet)
        return

    original_status = (
        registration_details.registration_data.registration_data_for_cadet(cadet).status
    )

    if original_status == new_status:
        return

    if new_status.is_cancelled_or_deleted:
        messages = update_status_of_existing_cadet_at_event_to_cancelled_or_deleted_and_return_messages(
            object_store=interface.object_store,
            event=registration_details.event,
            cadet=cadet,
            new_status=new_status,
        )
        if len(messages) > 0:
            for message in messages:
                interface.log_error(message)

    elif new_status.is_active:
        update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting(
            object_store=interface.object_store,
            event=registration_details.event,
            cadet=cadet,
            new_status=new_status,
        )
    else:
        interface.log_error(
            "Status change to cadet %s for %s not recognised contact support"
            % (cadet, str(new_status))
        )

    log_alert_for_status_change(
        interface=interface,
        cadet=cadet,
        original_status=original_status,
        new_status=new_status,
    )


def get_cadet_notes_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
):
    new_notes = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(column_name=NOTES, cadet_id=cadet.id),
        default=MISSING_FROM_FORM
    )
    if new_notes is MISSING_FROM_FORM:
        return

    original_notes = registration_details.registration_data.registration_data_for_cadet(
        cadet
    ).notes

    if original_notes == new_notes:
        return

    update_notes_for_existing_cadet_at_event(
        object_store=interface.object_store,
        cadet=cadet,
        event=registration_details.event,
        new_notes=new_notes,
    )


def get_cadet_health_for_row_in_form_and_alter_registration_data(
    interface: abstractInterface,
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
):
    new_health = interface.value_from_form(
        input_name_from_column_name_and_cadet_id(column_name=HEALTH, cadet_id=cadet.id),
        default=MISSING_FROM_FORM
    )
    if new_health is MISSING_FROM_FORM:
        return

    original_health = (
        registration_details.registration_data.registration_data_for_cadet(cadet).health
    )
    if original_health == new_health:
        return

    update_health_for_existing_cadet_at_event(
        object_store=interface.object_store,
        cadet=cadet,
        event=registration_details.event,
        new_health=new_health,
    )


def get_other_fields_from_form_and_alter_registration_data(
    interface: abstractInterface,
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
):
    all_columns = registration_details.all_columns_excluding_special_fields
    for column_name in all_columns:
        if _column_can_be_edited(column_name):
            ## in place update so doesn't return anything
            get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
                column_name=column_name,
                interface=interface,
                cadet=cadet,
                registration_details=registration_details,
            )


def get_registration_details_for_row_and_column_name_in_form_and_alter_registration_data(
    column_name: str,
    interface: abstractInterface,
    cadet: Cadet,
    registration_details: RegistrationDetailsForEvent,
):
    input_name = input_name_from_column_name_and_cadet_id(
        column_name=column_name, cadet_id=cadet.id
    )

    form_value = interface.value_from_form(input_name, default=MISSING_FROM_FORM)
    if form_value is MISSING_FROM_FORM:
        return

    new_value_for_column = typecast_input_of_column(
        column_name=column_name, value=form_value
    )

    update_data_row_for_existing_cadet_at_event(
        object_store=interface.object_store,
        cadet=cadet,
        event=registration_details.event,
        column_name=column_name,
        new_value_for_column=new_value_for_column,
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
    cadet: Cadet,
):
    if original_attendance == new_attendance:
        return

    warning_str = (
        "*Following volunteers associated with sailor %s for whom days attending updated - check they are still available for their nominated days, and if not update volunteer rota:"
        % cadet.name
    )

    log_alert_for_volunteers(warning_str=warning_str, interface=interface, cadet=cadet)


def log_alert_for_status_change(
    interface: abstractInterface,
    original_status: RegistrationStatus,
    new_status: RegistrationStatus,
    cadet: Cadet,
):
    if original_status == new_status:
        return

    if new_status.is_cancelled_or_deleted:
        warning_str = (
            "*Following volunteers associated with cadet %s for whom status updated to deleted or cancelled - check their availability, and if no longer available update volunteer rota:"
            % cadet
        )
    elif original_status.is_cancelled_or_deleted and new_status.is_active:
        warning_str = (
            "*Following volunteers associated with cadet %s for whom status updated to active registration - check their availability on the volunteer rota and / or add new volunteers if available:"
            % cadet
        )
    else:
        return

    log_alert_for_volunteers(warning_str=warning_str, interface=interface, cadet=cadet)


def log_alert_for_volunteers(
    interface: abstractInterface, cadet: Cadet, warning_str: str
):
    volunteer_names = get_list_of_volunteers_associated_with_cadet(
        object_store=interface.object_store,
        cadet=cadet,
    ).list_of_names()
    if len(volunteer_names) == 0:
        return

    volunteer_list_as_str = ", ".join(volunteer_names)
    interface.log_error(warning_str + " " + volunteer_list_as_str)
