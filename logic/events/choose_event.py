from logic.data_and_interface import DataAndInterface
from objects.events import Event


def choose_event(message: str, data_and_interface: DataAndInterface) -> Event:
    data = data_and_interface.data
    interface = data_and_interface.interface

    list_of_events = data.data_list_of_events.read()
    event_names = [str(event) for event in list_of_events]
    interface.message(message)
    option = interface.get_choice_from_adhoc_menu(event_names)
    option_index = event_names.index(option)
    event = list_of_events[option_index]

    return event
