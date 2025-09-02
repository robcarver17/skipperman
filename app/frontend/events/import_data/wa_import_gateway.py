from typing import Union, List

from app.backend.mapping.event_mapping import (
    is_event_mapped_with_wa_id,
    clear_wa_event_id_mapping,
    get_wa_id_for_event,
)
from app.objects.abstract_objects.abstract_text import Heading, bold

from app.backend.registration_data.raw_mapped_registration_data import (
    does_event_have_imported_registration_data,
)
from app.frontend.events.import_data.upload_event_file import (
    display_form_upload_event_file,
)
from app.frontend.events.import_data.import_wa_file import (
    display_form_import_event_file,
)
from app.frontend.events.mapping.ENTRY_event_field_mapping import (
    display_form_event_field_mapping,
)
from app.backend.mapping.list_of_field_mappings import does_event_already_have_mapping
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    HelpButton,
    main_menu_button,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.abstract_objects.abstract_buttons import back_menu_button
from app.frontend.form_handler import (
    button_error_and_back_to_initial_state_form,
)
from app.frontend.shared.events_state import get_event_from_state
from app.objects.events import Event
from app.backend.wild_apricot.load_wa_file import does_raw_event_file_exist


def display_form_WA_import_gateway(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    heading = Heading(
        "Import event registration data for %s from Wild Apricot (WA) export spreadsheets"
        % event.event_name
    )
    nav_bar = ButtonBar([main_menu_button, back_menu_button, help_button])
    upload_status = report_on_status_of_upload(interface=interface, event=event)
    buttons = get_buttons_depending_on_event_status(interface=interface, event=event)

    return Form(ListOfLines([nav_bar, heading, upload_status, buttons]).add_Lines())


def report_on_status_of_upload(
    interface: abstractInterface, event: Event
) -> ListOfLines:
    existing_field_mapping = does_event_already_have_mapping(
        object_store=interface.object_store, event=event
    )
    event_mapping_set_up = is_event_mapped_with_wa_id(
        object_store=interface.object_store, event=event
    )
    has_reg_data = does_event_have_imported_registration_data(
        object_store=interface.object_store, event=event
    )
    raw_event_file_uploaded = does_raw_event_file_exist(event)

    field_text = (
        "Field mapping has been setup."
        if existing_field_mapping
        else "No field mapping set up - do this before you can import any data"
    )
    if event_mapping_set_up:
        WA_ID = get_wa_id_for_event(event=event, object_store=interface.object_store)
        event_text = "A WA file with WA ID %s has been previously uploaded." % WA_ID
    else:
        event_text = "No WA file has ever been uploaded before (or WA ID has been manually cleared)."

    reg_text = (
        "Registration data has been imported already, but can be updated from a new file."
        if has_reg_data
        else "No registration data imported yet."
    )
    upload_text = (
        "WA file has been uploaded and can be imported."
        if raw_event_file_uploaded
        else "No file currently uploaded for import."
    )

    return ListOfLines(
        [bold("Status:"), field_text, event_text, reg_text, upload_text]
    ).add_Lines()


def get_buttons_depending_on_event_status(
    interface: abstractInterface, event: Event
) -> List[Button]:
    existing_field_mapping = does_event_already_have_mapping(
        object_store=interface.object_store, event=event
    )

    if existing_field_mapping:
        return get_buttons_if_field_mapping_set_up(interface=interface, event=event)
    else:
        ## no mapping have to do mapping first
        return [new_wa_field_mapping_button, first_upload_file_button]


def get_buttons_if_field_mapping_set_up(
    interface: abstractInterface, event: Event
) -> List[Button]:
    event_mapping_set_up = is_event_mapped_with_wa_id(
        object_store=interface.object_store, event=event
    )
    clear_event_mapping_button = clear_event_id_button if event_mapping_set_up else ""
    upload_or_imports_button_from_combo = get_upload_or_import_buttons(
        interface=interface, event=event
    )

    return (
        [existing_wa_field_mapping_button]
        + upload_or_imports_button_from_combo
        + [clear_event_mapping_button]
    )


def get_upload_or_import_buttons(
    interface: abstractInterface, event: Event
) -> List[Button]:
    has_reg_data = does_event_have_imported_registration_data(
        object_store=interface.object_store, event=event
    )
    raw_event_file_uploaded = does_raw_event_file_exist(event)

    logical_combo = (raw_event_file_uploaded, has_reg_data)

    combo_to_button_dict = {
        (False, False): [first_upload_file_button],
        (True, False): [import_file_button, subsequent_upload_file_button],
        (False, True): [subsequent_upload_file_button],
        (True, True): [update_file_button, subsequent_upload_file_button],
    }
    upload_or_import_buttons_from_combo = combo_to_button_dict[logical_combo]

    return upload_or_import_buttons_from_combo


help_button = HelpButton("import_registration_data_help")

new_wa_field_mapping_button = Button("Set up WA field mapping", tile=True)
existing_wa_field_mapping_button = Button("Check or modify WA field mapping", tile=True)

first_upload_file_button = Button("Upload a WA export file", tile=True)
import_file_button = Button("Import data from current WA file", tile=True)
update_file_button = Button("Update data using current WA file", tile=True)
subsequent_upload_file_button = Button("Upload a new WA export file", tile=True)

clear_event_id_button = Button("Reset the stored WA event ID", tile=True)

nav_bar = ButtonBar([back_menu_button, help_button])


def post_form_WA_import_gateway(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    button_pressed = interface.last_button_pressed()
    ## check button pressed (can only be upload or back - anything else treat as back as must be an error)
    if new_wa_field_mapping_button.pressed(
        button_pressed
    ) or existing_wa_field_mapping_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_event_field_mapping)
    elif import_file_button.pressed(button_pressed) or update_file_button.pressed(
        button_pressed
    ):
        return interface.get_new_form_given_function(display_form_import_event_file)

    elif first_upload_file_button.pressed(
        button_pressed
    ) or subsequent_upload_file_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_upload_event_file)

    elif clear_event_id_button.pressed(button_pressed):
        clear_wa_event_id_mapping_from_data(interface)
        return interface.get_new_form_given_function(display_form_WA_import_gateway)

    elif back_menu_button.pressed(button_pressed):
        return previous_form(interface)

    else:
        button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_WA_import_gateway
    )


def clear_wa_event_id_mapping_from_data(interface: abstractInterface):

    event = get_event_from_state(interface)
    interface.lock_cache()
    clear_wa_event_id_mapping(object_store=interface.object_store, event=event)
    interface.save_changes_in_cached_data_to_disk()
    interface.log_error(
        "Cleared WA ID for %s - make sure you upload the right file!" % event
    )
