from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.events import Event
from app.backend.data.resources import load_list_of_voluteers_at_event_with_patrol_boats, save_list_of_voluteers_at_event_with_patrol_boats

def get_summary_list_of_boat_allocations_for_events(event: Event) -> PandasDFTable:
    return ""


def add_named_boat_to_event_with_no_allocation(name_of_boat_added: str, event: Event):
    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_voluteers_at_event_with_patrol_boats.add_unallocated_boat()
    save_list_of_voluteers_at_event_with_patrol_boats(event=event)
    