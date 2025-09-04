from datetime import datetime
from typing import Union

from app.backend.events.event_warnings import (
    add_new_event_warning_checking_for_duplicate,
)
from app.data_access.configuration.configuration import local_timezone
from app.objects.cadets import Cadet

from app.backend.registration_data.update_cadets_at_event import (
    no_important_difference_between_cadets_at_event,
)
from app.backend.registration_data.cadet_registration_data import (
    is_cadet_already_at_event,
    add_new_cadet_to_event_from_row_in_registration_data,
    get_cadet_at_event,
)
from app.backend.registration_data.identified_cadets_at_event import (
    get_row_in_registration_data_for_cadet_both_cancelled_and_active,
)

from app.frontend.events.cadets_at_event.track_cadet_id_in_state_when_importing import (
    get_and_save_next_cadet_in_event_data,
    clear_cadet_id_at_event,
)

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.frontend.shared.events_state import get_event_from_state

from app.frontend.events.cadets_at_event.update_existing_cadet_at_event_forms import (
    display_form_for_update_to_existing_cadet_at_event,
    use_original_data_button,
    use_new_data_button,
    use_data_in_form_button,
)
from app.frontend.events.cadets_at_event.update_existing_cadet_at_event_from_form_entries import (
    update_cadets_at_event_with_new_data,
    update_cadets_at_event_with_form_data,
)
from app.objects.cadet_with_id_at_event import (
    get_cadet_at_event_from_row_in_event_raw_registration_data,
)
from app.objects.events import Event
from app.objects.utilities.exceptions import NoMoreData, DuplicateCadets
from app.objects.registration_data import RowInRegistrationData

from app.objects.event_warnings import (
    CADET_REGISTRATION,
)
from app.data_access.configuration.fixed import (
    LOW_PRIORITY,
    MEDIUM_PRIORITY,
    HIGH_PRIORITY,
)


def display_form_interactively_update_cadets_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## rest of the time is a post call

    clear_cadet_id_at_event(interface)

    return process_next_cadet_at_event(interface)


def process_next_cadet_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    print("Looping through updating delta data")
    event = get_event_from_state(interface)

    try:
        cadet = get_and_save_next_cadet_in_event_data(interface)
    except NoMoreData:
        print("Finished looping")
        clear_cadet_id_at_event(interface)
        return finished_looping_return_to_controller(interface)

    print("Current cadet is %s" % cadet)

    return process_update_to_cadet_data(interface=interface, event=event, cadet=cadet)


def process_update_to_cadet_data(
    interface: abstractInterface, event: Event, cadet: Cadet
) -> Form:
    cadet_already_at_event = is_cadet_already_at_event(
        object_store=interface.object_store, event=event, cadet=cadet
    )

    if cadet_already_at_event:
        print("%s already at event" % cadet)
        return process_update_to_existing_cadet_in_event_data(
            event=event, cadet=cadet, interface=interface
        )
    else:
        print("%s new to event" % cadet)
        return process_update_to_cadet_new_to_event(
            event=event, cadet=cadet, interface=interface
        )


def process_update_to_existing_cadet_in_event_data(
    interface: abstractInterface, event: Event, cadet: Cadet
) -> Form:
    try:
        row_in_registration_data = (
            get_row_in_registration_data_for_cadet_both_cancelled_and_active(
                object_store=interface.object_store,
                cadet=cadet,
                event=event,
                raise_error_on_duplicate=True,
            )
        )
    except DuplicateCadets:
        ## Cadet in registration data multiple times
        print("Existing cadet %s is duplicated no action" % cadet)
        message = (
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with multiple active registrations - ignoring any possible changes made to registration - go to WA and cancel one of the registrations please!"
            % cadet
        )
        log_import_error(
            interface=interface,
            message=message,
            priority=HIGH_PRIORITY,
            log_as_warning=True,
        )

        return process_next_cadet_at_event(interface)

    except NoMoreData:
        print("Existing cadet missing from reg data, could be manual %s" % cadet)
        ## Cadet not in registration data
        cadet_at_event = get_cadet_at_event(
            object_store=interface.object_store, event=event, cadet=cadet
        )
        if cadet_at_event.status.is_manual:
            warning = (
                "Cadet %s was added manually - is still not appearing in official registration import. "
                % cadet
            )
            # no need to create formal warning wll be done later
            log_import_error(interface=interface, message=warning, log_as_warning=False)
        else:
            ## No rows match cadet ID in current registration data, so deleted
            message = (
                "Cadet %s was in imported data, now appears to be missing in latest file - possible data corruption of imported file or manual hacking - no changes in file will be reflected in Skipperman"
                % cadet
            )
            log_import_error(
                interface=interface,
                message=message,
                log_as_warning=True,
                priority=LOW_PRIORITY,
            )

        return process_next_cadet_at_event(interface)

    return process_update_to_existing_cadet_at_event(
        interface=interface,
        event=event,
        row_in_registration_data=row_in_registration_data,
        cadet=cadet,
    )


def process_update_to_existing_cadet_at_event(
    interface: abstractInterface,
    row_in_registration_data: RowInRegistrationData,
    cadet: Cadet,
    event: Event,
) -> Form:
    existing_cadet_at_event_data = get_cadet_at_event(
        object_store=interface.object_store, event=event, cadet=cadet
    )

    new_cadet_at_event_data = (
        get_cadet_at_event_from_row_in_event_raw_registration_data(
            row_in_registration_data=row_in_registration_data, event=event, cadet=cadet
        )
    )

    if no_important_difference_between_cadets_at_event(
        new_cadet_at_event_data=new_cadet_at_event_data,
        existing_cadet_at_event_data=existing_cadet_at_event_data,
    ):
        ## nothing to do
        print("Cadet %s unchanged between existing and registration data" % str(cadet))
        return process_next_cadet_at_event(interface)
    else:
        return display_form_for_update_to_existing_cadet_at_event(
            interface=interface,
            event=event,
            new_cadet_at_event_data=new_cadet_at_event_data,
            existing_cadet_at_event_data=existing_cadet_at_event_data,
            cadet=cadet,
        )


def post_form_interactively_update_cadets_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    last_button_pressed = interface.last_button_pressed()

    if use_original_data_button.pressed(last_button_pressed):
        ## nothing to do, no change to master file
        return process_next_cadet_at_event(interface)

    
    if use_new_data_button.pressed(last_button_pressed):
        update_cadets_at_event_with_new_data(interface)
    elif use_data_in_form_button.pressed(last_button_pressed):
        update_cadets_at_event_with_form_data(interface)

    interface.flush_and_clear()

    return process_next_cadet_at_event(interface)


def process_update_to_cadet_new_to_event(
    interface: abstractInterface, event: Event, cadet: Cadet,
raise_error_on_duplicate=True
) -> Form:
    print("New row in master data for cadet with id %s" % cadet.id)

    try:
        relevant_row = get_row_in_registration_data_for_cadet_both_cancelled_and_active(
            object_store=interface.object_store,
            cadet=cadet,
            event=event,
            raise_error_on_duplicate=raise_error_on_duplicate,
        )
        process_update_to_cadet_new_to_event_with_registration_row(interface=interface, event=event,
                                                                   cadet=cadet, relevant_row=relevant_row)

    except DuplicateCadets:
        print("Duplicate cadet %s, trying again with 1st row only" % cadet)
        message = (
            "ACTION REQUIRED: Cadet %s appears more than once in imported file with an active registration - using the first registration found - go to WA and cancel all but one of the registrations please, and then check details here are correct!"
            % cadet
        )
        log_import_error(
            interface=interface,
            message=message,
            priority=HIGH_PRIORITY,
            log_as_warning=True,
        )
        ## try again this time allowing duplicates
        return process_update_to_cadet_new_to_event(
            interface=interface,
            event=event,
            cadet=cadet,
            raise_error_on_duplicate = False
        )


    except NoMoreData:
        print("Vanished cadet %s" % cadet)
        message = (
            "ACTION REQUIRED: Cadet %s vanished from raw registration data file - should not happen: contact support"
            % cadet
        )
        interface.log_error(message)
        log_import_error(
            interface=interface,
            message=message,
            priority=HIGH_PRIORITY,
            log_as_warning=True,
        )


    return process_next_cadet_at_event(interface)


def process_update_to_cadet_new_to_event_with_registration_row(
    interface: abstractInterface, event: Event, cadet: Cadet, relevant_row: RowInRegistrationData
):

    
    add_new_cadet_to_event_from_row_in_registration_data(
        object_store=interface.object_store,
        event=event,
        row_in_registration_data=relevant_row,
        cadet=cadet,
    )
    interface.flush_and_clear()

    print("Added %s with reg row %s" % (cadet, relevant_row))



def finished_looping_return_to_controller(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_interactively_update_cadets_at_event
    )


def log_import_error(
    interface: abstractInterface,
    message: str,
    priority: str = MEDIUM_PRIORITY,
    category=CADET_REGISTRATION,
    log_as_warning: bool = True,
):
    event = get_event_from_state(interface)
    interface.log_error(message)
    if log_as_warning:
        add_new_event_warning_checking_for_duplicate(
            object_store=interface.object_store,
            event=event,
            warning="On import at %s, %s" % (datetime.now(local_timezone), message),
            category=category,
            priority=priority,
            auto_refreshed=False,
        )  ## warning will sit on system until cleared

    print(message)
