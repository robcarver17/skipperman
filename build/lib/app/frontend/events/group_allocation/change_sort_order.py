from app.frontend.events.group_allocation.store_state import get_current_sort_order, save_new_sort_order
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.forms.reorder_form import reorder_table, reorderFormInterface, is_button_arrow_button
from app.objects.abstract_objects.abstract_form import Form
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_buttons import back_menu_button
from app.objects.abstract_objects.abstract_tables import Table


def display_change_sort_order(interface: abstractInterface):
    sort_order = get_current_sort_order(interface=interface)

    sort_button_table = sort_buttons_for_allocation_table(sort_order)

    return Form(
        ListOfLines(
            [
                "Specify order that group allocation table is sorted in:",
                sort_button_table,
                back_menu_button
            ]
        ),
    )

def sort_buttons_for_allocation_table(sort_order: list) -> Table:
    return reorder_table(sort_order)

def post_change_sort_order(interface:abstractInterface):
    last_button = interface.last_button_pressed()
    if back_menu_button.pressed(last_button):
        return interface.get_new_display_form_for_parent_of_function(display_change_sort_order)

    if is_button_arrow_button(last_button):
        change_sort_order_and_save(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    return display_change_sort_order(interface)

def change_sort_order_and_save(interface: abstractInterface):
    ## Change in order of list
    current_sort_order = get_current_sort_order(interface=interface)
    reorder_form_interface = reorderFormInterface(
        interface, current_order=current_sort_order
    )

    new_sort_order = reorder_form_interface.new_order_of_list()
    save_new_sort_order(interface=interface, new_sort_order=new_sort_order)

