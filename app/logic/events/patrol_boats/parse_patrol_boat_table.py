from app.backend.volunteers.patrol_boats import add_named_boat_to_event_with_no_allocation
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.patrol_boats.render_patrol_boat_table import ADD_BOAT_DROPDOWN
from app.objects.abstract_objects.abstract_interface import abstractInterface


def get_all_copy_buttons_for_rota(interface: abstractInterface) -> list:
    pass


def update_if_copy_button_pressed(interface: abstractInterface, copy_button: str):
    pass


def update_if_save_button_pressed_in_allocation_page(interface: abstractInterface):
    pass

def update_adding_boat(interface: abstractInterface):
    event =get_event_from_state(interface)
    name_of_boat_added = interface.value_from_form(ADD_BOAT_DROPDOWN)

    add_named_boat_to_event_with_no_allocation(name_of_boat_added=name_of_boat_added,
                                               event=event)

