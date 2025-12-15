from app.backend.mapping.list_of_field_mappings import (
    delete_mapping_given_skipperman_field,
    save_new_mapping_pairing,
)
from app.frontend.events.mapping.clone_field_mapping import (
    display_form_for_clone_event_field_mapping,
)
from app.frontend.events.mapping.create_mapping import (
    display_form_for_create_custom_field_mapping,
)
from app.frontend.events.mapping.template_field_mapping import (
    display_form_for_choose_template_field_mapping,
)
from app.frontend.events.mapping.mapping_table import *
from app.objects.abstract_objects.abstract_form import NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import MISSING_FROM_FORM


def template_mapping_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(
        display_form_for_choose_template_field_mapping
    )


def clone_mapping_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(
        display_form_for_clone_event_field_mapping
    )


def create_mapping_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_form_given_function(
        display_form_for_create_custom_field_mapping
    )


def add_skipperman_field_to_mapping(interface: abstractInterface):
    skipperman_field = interface.value_from_form(
        ADD_SKIPPERMAN_FIELD_DROPDOWN_NAME, default=ADD_SKIPPERMAN_FIELD_DROPDOWN_EMPTY
    )
    if skipperman_field == ADD_SKIPPERMAN_FIELD_DROPDOWN_EMPTY:
        clear_current_skipperman_field_to_add_from_state(interface)
        return

    save_current_skipperman_field_to_add_from_state(
        interface=interface, skipperman_field=skipperman_field
    )


def add_WA_and_skipperman_field_to_mapping(interface: abstractInterface):
    event = get_event_from_state(interface)
    skipperman_field = interface.value_from_form(
        ADD_SKIPPERMAN_FIELD_DROPDOWN_NAME, default=ADD_SKIPPERMAN_FIELD_DROPDOWN_EMPTY
    )
    wa_field = get_wa_field_mapping_from_form(interface)

    if not valid_inputs_for_mapping(
        skipperman_field=skipperman_field, wa_field=wa_field
    ):
        clear_current_skipperman_field_to_add_from_state(interface)
        return

    
    try:
        save_new_mapping_pairing(
            object_store=interface.object_store,
            event=event,
            skipperman_field=skipperman_field,
            wa_field=wa_field,
        )
    except Exception as e:
        interface.log_error(
            "Cannot add mapping pair %s/%s because %s"
            % (skipperman_field, wa_field, str(e))
        )

    clear_current_skipperman_field_to_add_from_state(interface)
    interface.DEPRECATE_flush_and_clear()


def get_wa_field_mapping_from_form(interface: abstractInterface):
    wa_field_text_input = interface.value_from_form(
        ADD_WA_FIELD_INPUT_FIELD_NAME, default=MISSING_FROM_FORM
    )
    wa_field_dropdown = interface.value_from_form(
        ADD_WA_FIELD_DROPDOWN_NAME, default=ADD_WA_FIELD_DROPDOWN_EMPTY
    )

    if wa_field_text_input is MISSING_FROM_FORM:
        return wa_field_dropdown
    else:
        return wa_field_text_input


def valid_inputs_for_mapping(skipperman_field: str, wa_field: str):
    if skipperman_field == ADD_SKIPPERMAN_FIELD_DROPDOWN_EMPTY:
        return False

    if wa_field == ADD_WA_FIELD_DROPDOWN_EMPTY:
        return False

    return True


def delete_mapping(interface: abstractInterface):
    event = get_event_from_state(interface)
    skipperman_field = get_skipperman_field_from_delete_button(
        interface.last_button_pressed()
    )
    try:
        delete_mapping_given_skipperman_field(
            object_store=interface.object_store,
            event=event,
            skipperman_field=skipperman_field,
        )
    except Exception as e:
        interface.log_error(
            "Error deleting mapping for %s, %s" % (skipperman_field, str(e))
        )
    interface.DEPRECATE_flush_and_clear()
