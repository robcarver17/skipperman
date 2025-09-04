from typing import Union

from app.backend.mapping.list_of_field_mappings import does_event_already_have_mapping

from app.frontend.events.import_data.import_controller import import_controller
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import initial_state_form
from app.backend.wild_apricot.load_wa_file import (
    delete_raw_event_upload_with_event_id,
    get_staged_file_raw_event_filename,
)
from app.backend.wild_apricot.process_upload import process_uploaded_wa_event_file
from app.frontend.shared.events_state import get_event_from_state


def display_form_import_event_file(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    existing_field_mapping = does_event_already_have_mapping(
        object_store=interface.object_store, event=event
    )
    if not existing_field_mapping:
        interface.log_error("Can't import file as no field mapping set up")
        return initial_state_form

    try:
        ## deletes staged file if works ok
        return process_wa_staged_file_already_uploaded(interface)
    except Exception as e:
        # will have to upload again
        delete_staged_file_for_current_event(interface)
        interface.log_error(
            "Problem with file importing data %s try uploading again" % e
        )

        return initial_state_form


def post_form_import_event_file(interface: abstractInterface) -> Union[Form, NewForm]:
    interface.log_error("Shouldn't get to post on import_data event file!")
    return initial_state_form


def process_wa_staged_file_already_uploaded(interface: abstractInterface) -> NewForm:
    ## First call, will do offline stuff and if required then change state for interactive
    ## no need for exceptions always in try catch
    event = get_event_from_state(interface)
    filename = get_staged_file_raw_event_filename(event)
    print("Working on %s " % filename)

    
    process_uploaded_wa_event_file(
        filename=filename, event=event, object_store=interface.object_store
    )
    interface.flush_and_clear()

    return import_controller_form(interface)


def import_controller_form(interface: abstractInterface):
    ## The import controller is common and would be used by other non WA methods
    return interface.get_new_form_given_function(import_controller)


def delete_staged_file_for_current_event(interface: abstractInterface):
    event = get_event_from_state(interface)
    delete_raw_event_upload_with_event_id(event)
