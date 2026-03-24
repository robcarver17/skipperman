from app.backend.groups.sorting import SortOrderGroups
from app.frontend.events.group_allocation.store_state import (
    get_current_sort_order,
    save_new_sort_order,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.forms.reorder_form import (
    reorder_table,
    reorderFormInterface,
    is_button_arrow_button,
)
from app.objects.abstract_objects.abstract_form import Form, radioInput, yes_no_radio
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import save_and_back_menu_button, cancel_menu_button
from app.objects.abstract_objects.abstract_tables import Table

HELM_AND_CREW_TOGETHER = "keep_together"

def display_change_sort_order(interface: abstractInterface):
    sort_order = get_current_sort_order(interface=interface)

    sort_button_table = sort_buttons_for_allocation_table(sort_order.sort_order_as_list)
    keep_helm_and_crew_together =yes_no_radio(input_name=HELM_AND_CREW_TOGETHER,
                                            input_label="Keep paired sailors together",
                                            default_is_yes=sort_order.keep_pairs_together
                                            )

    return Form(
        ListOfLines(
            [
                "Specify order that group allocation table is sorted in:",
                sort_button_table,
                _______________,
                keep_helm_and_crew_together,
                _______________,
                save_and_back_menu_button
            ]
        ),
    )


def sort_buttons_for_allocation_table(sort_order: list) -> Table:
    return reorder_table(sort_order)


def post_change_sort_order(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button):
        return interface.get_new_display_form_for_parent_of_function(
            display_change_sort_order
        )

    if save_and_back_menu_button.pressed(last_button):
        save_pairing_state_only(interface)
        return interface.get_new_display_form_for_parent_of_function(
            display_change_sort_order
        )

    if is_button_arrow_button(last_button):
        change_sort_order_and_save(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    return interface.get_new_form_given_function(display_change_sort_order)


def change_sort_order_and_save(interface: abstractInterface):
    ## Change in order of list
    current_sort_order = get_current_sort_order(interface=interface)
    reorder_form_interface = reorderFormInterface(
        interface, current_order=current_sort_order.sort_order_as_list
    )
    new_sort_order_list = reorder_form_interface.new_order_of_list()
    keep_pairs_together = interface.true_if_radio_was_yes(HELM_AND_CREW_TOGETHER)

    new_sort_order = SortOrderGroups(new_sort_order_list, keep_pairs_together=keep_pairs_together)

    save_new_sort_order(interface=interface, new_sort_order=new_sort_order)

def save_pairing_state_only(interface: abstractInterface):
    ## Change in order of list
    current_sort_order = get_current_sort_order(interface=interface)
    keep_pairs_together = interface.true_if_radio_was_yes(HELM_AND_CREW_TOGETHER)

    current_sort_order.keep_pairs_together=keep_pairs_together
    save_new_sort_order(interface=interface, new_sort_order=current_sort_order)