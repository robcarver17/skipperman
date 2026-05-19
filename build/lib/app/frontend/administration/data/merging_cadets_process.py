from app.backend.administration_and_utilities.merge_cadets import merge_cadets
from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.cadet_state import get_cadet_from_state, clear_cadet_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.cadets import Cadet
from app.objects.utilities.exceptions import MissingData


def display_merging_cadet_process(interface: abstractInterface):
    try:
        cadet_to_delete = get_cadet_to_delete_from_state(interface)
    except MissingData: ## been cleared
        return interface.get_new_display_form_for_parent_of_function(display_merging_cadet_process)

    cadet_to_merge = get_cadet_to_merge_with_from_state(interface)

    return Form(
        ListOfLines(
            [Heading("Deleting %s and merging with %s who will be retained" % (cadet_to_delete, cadet_to_merge)), _______________]
            + [Line([yes_button, cancel_button])]
        ).add_Lines()
    )


def post_merging_cadets_process(interface: abstractInterface):
    button_pressed = interface.last_button_pressed()
    print("pressed %s" % button_pressed)
    if yes_button.pressed(button_pressed):
        do_the_deletion(interface)
        return display_merging_cadet_process(interface)
    elif cancel_button.pressed(button_pressed):
        interface.log_error( "Merge cancelled")
        return interface.get_new_display_form_for_parent_of_function(display_merging_cadet_process)
    else:
        return button_error_and_back_to_initial_state_form(interface)



def do_the_deletion(interface: abstractInterface):
    cadet_to_delete = get_cadet_to_delete_from_state(interface)
    cadet_to_merge = get_cadet_to_merge_with_from_state(interface)

    #try:
    merge_cadets(interface=interface, cadet_to_keep=cadet_to_merge, cadet_to_delete=cadet_to_delete)
    interface.object_store.commit()
    interface.object_store.close()
    interface.clear()
    interface.log_error("Merge done")
    clear_cadet_state(interface)

    #except Exception as e:
    #    print("merge error")
    #    interface.log_error("Merge error %s - no changes saved" % str(e))
    #    interface.object_store.close()

yes_button = Button("Yes, go ahead with merge")
cancel_button = Button("No, cancel")


def get_cadet_to_delete_from_state(interface: abstractInterface) -> Cadet:
    return get_cadet_from_state(interface)  ## to make it clearer


def set_cadet_to_merge_with_in_state(interface: abstractInterface, cadet: Cadet):
    interface.set_persistent_value(CADET_TO_MERGE_WITH, cadet.id)


def get_cadet_to_merge_with_from_state(interface: abstractInterface):
    id = interface.get_persistent_value(CADET_TO_MERGE_WITH)
    return get_cadet_from_id(object_store=interface.object_store, cadet_id=id)


CADET_TO_MERGE_WITH = "merge_cadet_with"
