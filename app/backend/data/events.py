from app.data_access.data import data
from app.objects.events import Event, ListOfEvents


def add_new_verified_event(event: Event):
    data.data_list_of_events.add(event)


def get_list_of_all_events() -> ListOfEvents:
    list_of_events = data.data_list_of_events.read()

    return list_of_events
